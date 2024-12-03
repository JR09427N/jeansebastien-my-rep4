Overview

This repository contains Python FastAPI code for a server I built as part of a personal project. 
The server is designed to process image data for student ID verification. It handles tasks like 
comparing faces between a student’s ID and a selfie, and extracting the student’s name from the ID image.

Note for Professor Baik

I want to acknowledge that this project isn’t aligned with the OS capstone's assignment requirements. 
Unfortunately, after losing all my work from earlier parts of the assignment due to technical issues, 
I wasn’t able to fully recover or rebuild my progress in time. Instead, I’m submitting this personal project 
to show my understanding of how to build and interact with a web server, even though it’s unrelated to the 
task. I hope it still reflects some of the skills you’re looking for.

What This Server Does

POST Endpoints:

/send_id_string: Receives a base64-encoded image of a student’s school ID.
/send_selfie_string: Receives a base64-encoded image of the student’s selfie.

Image Processing Functions:

run_comparison(): Compares the two images to check if the faces match using OpenCV.
convert_to_name(): Extracts text from the ID image using pytesseract and isolates the student’s name.

GET Endpoints:

/is_same_face: Returns true if the faces match, and false if they don’t.
/read_name_from_id: Sends back the name extracted from the ID image.
