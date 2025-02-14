from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from io import BytesIO
import os
from typing import Optional

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (update this for production)
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Hugging Face API settings
HF_API_URL = "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32"
HF_API_TOKEN = os.getenv("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")  # Set your Hugging Face token in environment variables

headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

async def analyze_image(image: UploadFile):
    """
    Analyze an image using Hugging Face's CLIP model.
    Returns a description of the image.
    """
    try:
        # Read the image file
        image_content = await image.read()
        image_bytes = BytesIO(image_content)

        # Send the image to Hugging Face's CLIP API
        response = requests.post(
            HF_API_URL,
            headers=headers,
            files={"file": image_bytes.getvalue()},
            data={"inputs": "What is in this image? Provide details and history if relevant."},
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from Hugging Face API")

        # Extract the most relevant label and score
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            best_match = result[0]  # Get the first result (most relevant)
            return {
                "label": best_match.get("label", "Unknown"),
                "score": best_match.get("score", 0),
                "description": f"This is a {best_match.get('label', 'object')} with a confidence score of {best_match.get('score', 0):.2f}."
            }
        else:
            return {"description": "No relevant information found for this image."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

async def analyze_text(text: str):
    """
    Analyze text using Hugging Face's CLIP model.
    Returns a description or relevant information about the text.
    """
    try:
        # Send the text to Hugging Face's CLIP API
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": text},
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from Hugging Face API")

        # Extract the most relevant response
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            best_match = result[0]  # Get the first result (most relevant)
            return {
                "label": best_match.get("label", "Unknown"),
                "score": best_match.get("score", 0),
                "description": f"This is about {best_match.get('label', 'the input')} with a confidence score of {best_match.get('score', 0):.2f}."
            }
        else:
            return {"description": "No relevant information found for this text."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")

@app.post("/chat/")
async def chat_endpoint(
    text: Optional[str] = Form(None),
    images: list[UploadFile] = File([]),
):
    """
    Endpoint to handle chat requests.
    Accepts text and/or images, processes them using CLIP, and returns responses.
    """
    try:
        responses = []

        # Analyze text if provided
        if text:
            text_response = await analyze_text(text)
            responses.append({"type": "text", "content": text_response})

        # Analyze images if provided
        for image in images:
            image_response = await analyze_image(image)
            responses.append({"type": "image", "content": image_response})

        return {"responses": responses}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
