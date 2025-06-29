import asyncio
import logging
import grpc
import cv2
import io
from PIL import Image
import pytesseract
import numpy as np
import common_pb2
import ocr_service_pb2_grpc
from google.protobuf import empty_pb2


logger = logging.getLogger(__name__)


class ImageProcessorServicer(ocr_service_pb2_grpc.ImageProcessorServicer):
    def __init__(self):
        self.file_size = None
        # maybe help in the future

    async def ReadFileSize(self, request, context):
        """
        read the file size
        """

        try:
            self.file_size = request.size
            return empty_pb2.Empty()

        except Exception as e:
            logger.error(f"error in READFILESIZE method: {e}", exc_info=True)
            raise

    async def ProcessImage(self, request_iterator, context):
        """
        collect the image bytes chunks process it and yield back to client
        """

        try:
            chunks = []

            total_bytes = 0
            async for request in request_iterator:
                chunks.append(request.content)
                total_bytes += len(request.content)
                progress = (total_bytes * 100) / self.file_size
                yield common_pb2.ProgressResponse(percent=progress)

            logger.info("successfully chunks collected")

            full_image_bytes = b"".join(chunks)

            extracted_text = self.extract_text_from_image(full_image_bytes)

            yield common_pb2.ProgressResponse(result=extracted_text)

        except Exception as e:
            logger.error(f"error in ProcessImage method {str(e)}")

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Convert PIL to OpenCV format for preprocessing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Apply image preprocessing for better OCR
            processed_image = self.preprocess_image(cv_image)

            # DEBUG: Save the processed image to disk
            # cv2.imwrite("debug_processed_image.png", processed_image)

            # Perform OCR
            text = pytesseract.image_to_string(processed_image)

            return f"Extracted text: {text.strip()}"

        except Exception as e:
            return f"OCR Error: {str(e)}"

    def preprocess_image(self, image):
        """
        Apply image preprocessing techniques to improve OCR accuracy
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Apply morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        # Remove noise with opening operation
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        # Fill gaps with closing operation
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)

        return closing


async def serve():
    server = grpc.aio.server()
    ocr_service_pb2_grpc.add_ImageProcessorServicer_to_server(
        ImageProcessorServicer(), server
    )
    server.add_insecure_port("[::]:50052")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
