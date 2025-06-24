import tempfile
import os
import asyncio
import logging
from typing import AsyncGenerator
import grpc
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
import pdf_service_pb2_grpc
import common_pb2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI()


async def grpc_stream_pdf(file_path: str) -> AsyncGenerator[str, None]:

    try:
        logger.info("inside the grpc_stream_pdf method")

        # open the gRPC channel
        async with grpc.aio.insecure_channel("localhost:50051") as channel:

            logger.info("connection successful")

            # create the stub (local representator of remote service)

            stub = pdf_service_pb2_grpc.FileProcessStub(channel)

            logger.info("stub successful")

            async def chunk_generator():
                try:
                    with open(file_path, "rb") as file:
                        logger.info(f"start reading the file {file_path}")
                        while chunk := file.read(1024 * 1024):
                            yield common_pb2.FileChunk(content=chunk, type="PDF")
                except Exception as e:
                    logger.error(f"File read error: {str(e)}")
                    raise

            response_stream = stub.ProcessFile(chunk_generator())

            print(response_stream)

            logger.info("response_stream detected")

            # response_stream contains the program in yield from but the summary once object complete

            # check if respnose stream has percent or it yeild result
            async for response in response_stream:
                if response.HasField("percent"):
                    logger.info("progress_returned successful")
                    yield f"progress : {response.percent:.1f}%"
                elif response.HasField("result"):
                    logger.info("result returned successful")
                    yield f"result : {response.result}"

        # NOTE: handle the file closing
        os.unlink(file_path)
    except asyncio.CancelledError:
        logger.info("Client disconnected")
        # Add cleanup logic if needed
        raise


@app.get("/", response_class=RedirectResponse)
async def msg():
    return "http://localhost:8000/docs"


@app.post("/process-file")
async def process_file(request: Request, file: UploadFile):

    try:
        # validate the uploaded file
        if file.content_type == "application/pdf":
            logger.info("pdf file detected")

            with tempfile.NamedTemporaryFile(delete=False) as tmp:

                content = await file.read()

                tmp.write(content)

                file_path = tmp.name

            return StreamingResponse(
                grpc_stream_pdf(file_path), media_type="text/plain"
            )
        else:
            raise HTTPException(status_code=400, detail="unsupport file type")
    finally:
        await file.close()
