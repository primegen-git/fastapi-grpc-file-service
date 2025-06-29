import tempfile
import os
import asyncio
import logging
from typing import AsyncGenerator
import grpc
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
import ocr_service_pb2_grpc
import pdf_service_pb2_grpc
import common_pb2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI()


async def grpc_stream_pdf(
    file_path: str, file_size_kb: int
) -> AsyncGenerator[str, None]:

    try:
        logger.info("inside the grpc_stream_pdf method")

        # open the gRPC channel
        async with grpc.aio.insecure_channel("localhost:50051") as channel:

            logger.info("connection successful")

            # create the stub (local representator of remote service)

            stub = pdf_service_pb2_grpc.FileProcessorStub(channel)

            logger.info("stub successful")

            # first send the file size in kb...

            await stub.ReadFileSize(common_pb2.FileSize(size=file_size_kb))

            async def pdf_chunk_generator():
                try:
                    with open(file_path, "rb") as file:
                        logger.info(f"start reading the file {file_path}")
                        while chunk := file.read(64 * 1024):
                            yield common_pb2.FileChunk(content=chunk, type="PDF")
                except Exception as e:
                    logger.error(f"PDF File read error: {str(e)}")
                    raise

            response_stream = stub.ProcessFile(pdf_chunk_generator())

            print(response_stream)

            logger.info("response_stream detected")

            async for response in response_stream:
                if response.HasField("percent"):
                    logger.info("progress_returned successful")
                    yield f"progress : {response.percent:.1f}%\n"
                    # await asyncio.sleep(0.1)
                elif response.HasField("result"):
                    logger.info("result returned successful")
                    yield f"result : {response.result}"

        # NOTE: handle the file closing
        os.unlink(file_path)
    except asyncio.CancelledError:
        logger.info("Client disconnected")
        # Add cleanup logic if needed
        raise


async def grpc_stream_image(
    file_path: str, file_size_kb: int
) -> AsyncGenerator[str, None]:
    try:

        # create gRPC connection
        async with grpc.aio.insecure_channel("localhost:50052") as channel:

            logger.info("image gRPC connection created")

            # create the stubs
            stub = ocr_service_pb2_grpc.ImageProcessorStub(channel)

            # send the file size in kb
            await stub.ReadFileSize(common_pb2.FileSize(size=file_size_kb))

            async def image_chunk_generator():
                try:
                    with open(file_path, "rb") as f:
                        logger.info(f"start reading the file {file_path}")
                        while chunk := f.read(64 * 1024):
                            if not chunk:
                                continue
                            yield common_pb2.FileChunk(content=chunk, type="IMAGE")
                except Exception as e:
                    logger.error(f"error while generate image chunk {str(e)}")
                    raise Exception(f"{str(e)}")

            response_stream = stub.ProcessImage(image_chunk_generator())

            async for response in response_stream:
                if response.HasField("percent"):
                    logger.info(
                        f"image processsing percentage : {response.percent:.1f}%"
                    )
                    yield f"progress percent : {response.percent:.1f}%\n"
                elif response.HasField("result"):
                    logger.info("final image ocr recieved")
                    yield f"extracted text is : {response.result}"

            os.unlink(file_path)

    except Exception as e:
        logger.error(f"error in image grpc_stream method {str(e)}")
        raise Exception(f"{str(e)}")


@app.get("/", response_class=RedirectResponse)
async def msg():
    return "http://localhost:8000/docs"


@app.post("/process-file")
async def process_file(request: Request, file: UploadFile):

    try:
        # validate the uploaded file
        if file.content_type == "application/pdf":
            logger.info("pdf file detected")

            # print(f"file_size: {file.size}")

            with tempfile.NamedTemporaryFile(delete=False) as tmp:

                content = await file.read()

                tmp.write(content)

                file_path = tmp.name

            return StreamingResponse(
                grpc_stream_pdf(file_path, file.size),
                media_type="text/plain",
            )
        else:
            raise HTTPException(status_code=400, detail="unsupport file type")
    finally:
        await file.close()


@app.post("/process-image")
async def process_image(request: Request, file: UploadFile):

    try:
        # validate the uploaded file
        if file.content_type.startswith("image/"):
            logger.info("image file detected")

            # print(f"file_size: {file.size}")

            with tempfile.NamedTemporaryFile(delete=False) as tmp:

                content = await file.read()

                logger.info(f"content : {content[:50]}")

                tmp.write(content)

                file_path = tmp.name

            return StreamingResponse(
                grpc_stream_image(file_path, file.size), media_type="text/plain"
            )
        else:
            raise HTTPException(status_code=400, detail="unsupport file type")
    finally:
        await file.close()
