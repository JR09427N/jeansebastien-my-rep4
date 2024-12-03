from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from io import BytesIO
import numpy as np
import pytesseract as pyt
import cv2
from deepface import DeepFace

# python -m uvicorn main:app --reload
# python -m uvicorn main:app --host 0.0.0.0 --port 8000
app = FastAPI()

# Global variables to store the byte arrays of the images
decoded_id_image_bytes = None
decoded_selfie_image_bytes = None
threshold = 0.6
match = None

# Define a data model for the request body
class MessageRequest(BaseModel):
    message: str


# *************************************************** Endpoints to receive image strings ***************************************************  #



# Endpoint for ID image string
@app.post("/send_id_string")
async def receive_id_string(data: MessageRequest):
    global decoded_id_image_bytes  # Declare the global variable
    
    # Decode the Base64 string to bytes
    decoded_id_image_bytes = base64.b64decode(data.message)
    
    print("Received and decoded ID image successfully!")
    run_comparison()  # Check if we can run comparison after receiving this image
    return {"message": "ID image received and decoded successfully!"}

# Endpoint for selfie image string
@app.post("/send_selfie_string")
async def receive_selfie_string(data: MessageRequest):
    global decoded_selfie_image_bytes  # Declare the global variable
    
    # Decode the Base64 string to bytes
    decoded_selfie_image_bytes = base64.b64decode(data.message) 
    
    print("Received and decoded selfie image successfully!")
    run_comparison()  # Check if we can run comparison after receiving this image
    return {"message": "Selfie image received and decoded successfully!"}



# *************************************************** functions to compare faces ***************************************************  #

# convert byte array to image
def byte_array_to_image(byte_array):
    # Convert byte array to NumPy array
    nparr = np.frombuffer(byte_array, np.uint8)
    # Decode the NumPy array into an image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


# code to compare faces
def compare_faces(id_img, selfie_img, threshold):
    
    result = DeepFace.verify(id_img, selfie_img)

    distance = result["distance"]

    is_same_face = distance < threshold

    print(f"Distance between faces: {distance}")
    print(f"Threshold: {threshold}")

    # Determine if the faces match
    if is_same_face:
        print("Faces match")
        return True
    else:
        print("Faces do not match")
        return False


# runs face comparison & returns true or false
def run_comparison():
    if decoded_id_image_bytes and decoded_selfie_image_bytes:
        id_image = byte_array_to_image(decoded_id_image_bytes)
        selfie_image = byte_array_to_image(decoded_selfie_image_bytes)
        
        # Compare faces
        global match
        match = compare_faces(id_image, selfie_image, threshold)
        return match
    else:
        print("No images have been received yet.")
        return False



# *************************************************** function to read name from ID ***************************************************  #

def convert_to_name():
    if decoded_id_image_bytes is None:
        raise HTTPException(status_code=400, detail="ID image has not been received yet.")
    
    # Convert byte array to OpenCV image
    id_img = byte_array_to_image(decoded_id_image_bytes)
    
    # Convert image to grayscale
    gray_image = cv2.cvtColor(id_img, cv2.COLOR_BGR2GRAY)

    # Configure Tesseract
    try:
        pyt.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tesseract configuration error: {e}")
    
    # Extract text from image
    try:
        text = pyt.image_to_string(gray_image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction error: {e}")

    # Remove unwanted text and digits
    text = ''.join(c for c in text if not c.isdigit())  # Remove digits
    text = text.replace('STUDENT ', "").replace("ID", "").replace("PACE", "").replace("UNIVERSITY", "").replace('\n', '')  # Remove specific words

    # Capitalize name
    text = text.title()

    if text is None:
        return "No text read"
    else:
        return text



# *************************************************** endpoints to send boolean results ***************************************************  #


@app.get("/is_same_face")
def is_match():
    run_comparison()
    global match
    if match is None:
        raise HTTPException(status_code=400, detail="Face comparison not performed yet.")
    print(match)
    return {"is_same_face": match}


@app.get("/read_name_from_id")
def read_name():
    try:
        name = convert_to_name()
        print(name)
        return {"name_from_id": name}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
