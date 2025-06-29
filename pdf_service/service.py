import io
import re
import nltk
import PyPDF2
import asyncio
import grpc
import pdf_service_pb2_grpc
import common_pb2
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

import logging
from google.protobuf import empty_pb2


logger = logging.getLogger(__name__)


class FileProcessorServicer(pdf_service_pb2_grpc.FileProcessorServicer):
    def __init__(self):
        # Download required NLTK data (run once)
        try:
            nltk.download("punkt_tab", quiet=True)
        except Exception as e:
            logger.warning(f"NLTK download warning: {e}")

        self.fize_size = None

    async def ReadFileSize(self, request, context):
        try:
            self.file_size = request.size
            return empty_pb2.Empty()

        except Exception as e:
            logger.error(f"error in READFILESIZE method : {e}")
            raise

    async def ProcessFile(self, request_iterator, context):

        try:

            logger.info("Process_file method is called")
            chunks = []

            # collect the chunk from the client(fastapi application in here)

            total_bytes = 0
            async for request in request_iterator:
                chunks.append(request.content)  # total_chunks += 1
                total_bytes += len(request.content)
                progress = (total_bytes * 100) / self.file_size
                yield common_pb2.ProgressResponse(percent=progress)

            full_content = b"".join(chunks)

            logger.info(f"chunks is combined {full_content[:300]}")

            summary = self.generate_summary(full_content)

            yield common_pb2.ProgressResponse(result=summary)
        except Exception as e:
            raise Exception(f"{str(e)}")

    def generate_summary(self, content: bytes) -> str:
        """
        Extract and clean text from PDF, then generate a readable summary
        """
        try:
            logger.info("generate summary method is called")

            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            raw_text = ""

            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    raw_text += page_text + " "
                logger.info(f"extracted page: {page_num + 1}")

            # Clean and format the extracted text
            cleaned_text = self.clean_pdf_text(raw_text)

            if not cleaned_text.strip():
                return "summary: No readable text found in PDF"

            # Check if text is long enough for summarization
            word_count = len(cleaned_text.split())
            if word_count < 20:
                return f"summary: {cleaned_text[:300]}..."

            # Generate summary
            parser = PlaintextParser.from_string(cleaned_text, Tokenizer("english"))
            summarizer = LexRankSummarizer()

            sentences_count = min(3, max(2, word_count // 100))
            summary_sentences = summarizer(parser.document, sentences_count)

            # Format the summary properly
            summary_text = ". ".join(
                str(sentence).strip() for sentence in summary_sentences
            )

            # Ensure proper sentence ending
            if summary_text and not summary_text.endswith("."):
                summary_text += "."

            logger.info(f"Summary generated successfully")
            return f"summary: {summary_text}"

        except Exception as e:
            logger.error(f"Error in generate_summary: {str(e)}")
            return "summary: Error processing PDF - unable to extract readable text"

    def clean_pdf_text(self, text: str) -> str:
        """
        Clean and format text extracted from PDF
        """
        # Remove excessive whitespace and normalize
        text = re.sub(r"\s+", " ", text)

        # Add spaces before capital letters that follow lowercase letters
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

        # Add spaces around numbers
        text = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", text)
        text = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", text)

        # Fix common PDF extraction issues
        text = re.sub(r"([.!?])([A-Z])", r"\1 \2", text)  # Space after punctuation
        text = re.sub(
            r"([a-z])([.!?])([A-Z])", r"\1\2 \3", text
        )  # Space after sentence end

        # Remove special characters that don't add meaning
        text = re.sub(r"[•◦▪▫]", "", text)  # Remove bullet points
        text = re.sub(r"[^\w\s.,!?;:()\-]", " ", text)  # Keep basic punctuation

        # Final cleanup
        text = re.sub(r"\s+", " ", text).strip()

        return text


async def serve():
    server = grpc.aio.server()
    pdf_service_pb2_grpc.add_FileProcessorServicer_to_server(
        FileProcessorServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
