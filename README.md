# File Processing Microservice

A microservices-based system for processing PDF and image files using gRPC and FastAPI. The project provides endpoints for uploading files, which are then streamed to backend services for PDF summarization or image OCR extraction.

## Features

- **PDF Summarization:** Extracts and summarizes text from PDF files.
- **Image OCR:** Extracts text from images using OCR with preprocessing.
- **Streaming gRPC:** Efficiently streams file chunks between services.
- **FastAPI Gateway:** HTTP API for file uploads, streaming results back to the client.
- **Modular Microservices:** Separate services for PDF and image processing.

## Project Structure

```
.
├── api_gateway/
│   ├── __init__.py
│   └── main.py
├── ocr_service/
│   ├── __init__.py
│   └── service.py
├── pdf_service/
│   ├── __init__.py
│   └── service.py
├── protobufs/
│   ├── common.proto
│   ├── ocr_service.proto
│   └── pdf_service.proto
├── common_pb2.py
├── common_pb2_grpc.py
├── ocr_service_pb2.py
├── ocr_service_pb2_grpc.py
├── pdf_service_pb2.py
├── pdf_service_pb2_grpc.py
├── .gitignore
└── __init__.py
```

## How It Works

### 1. API Gateway ([api_gateway/main.py](api_gateway/main.py))

- Exposes HTTP endpoints using FastAPI:
  - `POST /process-file`: Accepts PDF uploads, streams to PDF service, returns summary/progress.
  - `POST /process-image`: Accepts image uploads, streams to OCR service, returns extracted text/progress.
- Handles file uploads, saves them temporarily, and streams file chunks to the appropriate gRPC service.
- Streams progress and results back to the client as plain text.

### 2. PDF Service ([pdf_service/service.py](pdf_service/service.py))

- Receives streamed PDF file chunks via gRPC.
- Reassembles the file, extracts text using PyPDF2, cleans it, and generates a summary using the LexRank algorithm (Sumy).
- Streams progress updates and the final summary back to the gateway.

### 3. OCR Service ([ocr_service/service.py](ocr_service/service.py))

- Receives streamed image file chunks via gRPC.
- Reassembles the image, preprocesses it (grayscale, blur, threshold, morphology), and extracts text using Tesseract OCR.
- Streams progress updates and the final extracted text back to the gateway.

### 4. Protobuf Definitions ([protobufs/](protobufs/))

- `common.proto`: Defines shared messages (`FileChunk`, `ProgressResponse`) and the `FileType` enum.
- `pdf_service.proto`: Defines the `FileProcessor` service for PDF processing.
- `ocr_service.proto`: Defines the `ImageProcessor` service for image processing.

## Running the Project

### Prerequisites

- Python 3.8+
- [gRPC](https://grpc.io/docs/languages/python/quickstart/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyPDF2](https://pypdf2.readthedocs.io/)
- [Sumy](https://github.com/miso-belica/sumy)
- [NLTK](https://www.nltk.org/)
- [OpenCV](https://opencv.org/)
- [Pillow](https://python-pillow.org/)
- [pytesseract](https://pypi.org/project/pytesseract/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (system dependency)

Install Python dependencies:

```sh
pip install -r requirements.txt
```

### 1. Generate gRPC Code

From the project root:

```sh
python -m grpc_tools.protoc -I./protobufs --python_out=. --grpc_python_out=. ./protobufs/common.proto
python -m grpc_tools.protoc -I./protobufs --python_out=. --grpc_python_out=. ./protobufs/pdf_service.proto
python -m grpc_tools.protoc -I./protobufs --python_out=. --grpc_python_out=. ./protobufs/ocr_service.proto
```

### 2. Start the Services

In separate terminals, run:

**PDF Service:**
```sh
python pdf_service/service.py
```

**OCR Service:**
```sh
python ocr_service/service.py
```

**API Gateway:**
```sh
uvicorn api_gateway.main:app --reload
```

### 3. Usage

- Open [http://localhost:8000/docs](http://localhost:8000/docs) for the FastAPI Swagger UI.
- Use `/process-file` to upload a PDF and receive a summary.
- Use `/process-image` to upload an image and receive extracted text.

## Notes

- Temporary files are deleted after processing.
- Progress is streamed as the file is processed.
- Ensure Tesseract OCR is installed and available in your system PATH for image OCR.

## License

MIT License

---

