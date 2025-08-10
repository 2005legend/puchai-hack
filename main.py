import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import pytesseract

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO if too verbose
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow frontend requests (adjust origins if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model for extracted text
class OCRResult(BaseModel):
    extracted_text: str
    error: Optional[str] = None


@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "TARA API is running"}


@app.post("/bill_scanner_upload", response_model=OCRResult)
async def bill_scanner_upload(file: UploadFile = File(...)):
    logger.info(f"Received file upload request: {file.filename}")

    try:
        # Check file type
        if not file.content_type.startswith("image/"):
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.debug(f"File saved temporarily at {temp_path}")

        # Run OCR
        logger.info(f"Starting OCR on {temp_path}")
        image = Image.open(temp_path)
        extracted_text = pytesseract.image_to_string(image)
        logger.info("OCR processing completed")

        # Clean up temp file
        os.remove(temp_path)
        logger.debug(f"Temporary file {temp_path} removed")

        return OCRResult(extracted_text=extracted_text)

    except Exception as e:
        logger.exception("Error occurred during /bill_scanner_upload processing")
        return OCRResult(extracted_text="", error=str(e))


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting TARA API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
