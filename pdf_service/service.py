import asyncio
import grpc
import pdf_service_pb2_grpc
import common_pb2
import base64

import logging


logger = logging.getLogger(__name__)


class FileProcessServicer(pdf_service_pb2_grpc.FileProcessServicer):
    async def ProcessFile(self, request_iterator, context):

        try:

            logger.info("Process_file method is called")
            # first jop is to capture the chunks
            # total_chunks = 0
            chunks = []

            async for request in request_iterator:
                chunks.append(request.content)
                # total_chunks += 1
                progress = len(chunks) * 10
                yield common_pb2.ProgressResponse(percent=progress)

            print(f"chunk of len : {len(chunks)} is read successfully")

            full_content = b"".join(chunks)

            logger.info(f"chunks is combined {full_content[:100]}")

            summary = self.generate_summary(full_content)

            yield common_pb2.ProgressResponse(result=summary)
        except Exception as e:
            raise Exception(f"{str(e)}")

    def generate_summary(self, content: bytes) -> str:
        logger.info("generate summary method is called")
        return f"summary : {base64.b64encode(content)[:100]}"


async def serve():
    server = grpc.aio.server()
    pdf_service_pb2_grpc.add_FileProcessServicer_to_server(
        FileProcessServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
