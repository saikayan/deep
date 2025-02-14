from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uuid
from typing import List, Optional

app = FastAPI()

# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory for uploaded files
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatResponse(BaseModel):
    text: str
    image_url: Optional[str] = None

def process_text(text: str):
    """Example text processing function"""
    return f"Processed text: {text} (This is a mock response)"

def process_image(image_path: str):
    """Example image processing function"""
    return {"description": "This is a mock image description"}

@app.post("/chat/", response_model=ChatResponse)
async def chat_endpoint(
    text: Optional[str] = Form(None),
    images: List[UploadFile] = File([])
):
    try:
        # Process text input
        text_response = process_text(text) if text else "No text provided"

        # Process images
        image_responses = []
        for image in images:
            # Save uploaded image
            file_ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = f"static/uploads/{filename}"
            
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())
            
            # Process image (replace with your actual image processing logic)
            img_result = process_image(file_path)
            image_responses.append(img_result)

        # Generate mock image response (replace with actual logic)
        # In a real scenario, you might generate an image and save it to static
        mock_image_url = "https://picsum.photos/200/300"  # Random example image

        return {
            "text": f"{text_response}. Received {len(images)} images.",
            "image_url": mock_image_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)