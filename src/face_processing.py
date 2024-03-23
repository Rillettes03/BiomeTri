import face_recognition
import os, sys
import cv2
import numpy as np
import math
import dlib


# Get image file path relatively
def getPath(imfile, ipath="interface"):
    # Get the current directory of the script
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # Get the parent directory (one level up)
    project_directory = os.path.dirname(current_directory)
    # Now you can use this to construct relative paths
    image_path = os.path.join(project_directory, ipath, imfile)
    return image_path

def face_confidence(face_distance, face_match_threshold=0.6):
    #calculating the percentage of matching accuracy as 
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0 )

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + "%"
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + "%"

def rect_to_bb(rect):
	# take a bounding predicted by dlib and convert it
	# to the format (x, y, w, h) as we would normally do
	# with OpenCV
	x = rect.left()
	y = rect.top()
	w = rect.right() - x
	h = rect.bottom() - y
	# return a tuple of (x, y, w, h)
	return (x, y, w, h)

def shape_to_np(shape, dtype="int"):
	# initialize the list of (x, y)-coordinates
	coords = np.zeros((68, 2), dtype=dtype)
	# loop over the 68 facial landmarks and convert them
	# to a 2-tuple of (x, y)-coordinates
	for i in range(0, 68):
		coords[i] = (shape.part(i).x, shape.part(i).y)
	# return the list of (x, y)-coordinates
	return coords



class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True # save some computer power by not trying to recognise faces from any single frame
    # Create a black background
    background = (0, 0, 0)

    # Text to display
    instruction1 = "Press 'Esc' to close "
    instruction2 = "Press 'Enter' to save"

    def __init__(self):
       self.encode_faces()
    
    def enroll_face(self, filename):
        # initialize the camera
        cam_port = 0
        cam = cv2.VideoCapture(cam_port)

        # Load the pre-trained face detection classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Load the pre-trained facial landmark predictor
        predictor_path = "src/shape_predictor_68_face_landmarks.dat"
        predictor = dlib.shape_predictor(predictor_path)

        # open a window to show the video frame
        window_name = "Face Enrolling"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
        cv2.moveWindow(window_name, 363, 144)

        # display the video frame until a key is pressed
        while True:
            # reading the input using the camera
            result, image = cam.read()

            # If an image is detected without any error, show result
            if result:
                # Convert the image to grayscale for face detection
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Detect faces in the image
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

                # Draw rectangles around the detected faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

                    # Convert the OpenCV rectangle to a dlib rectangle
                    dlib_rect = dlib.rectangle(int(x), int(y), int(x+w), int(y+h))

                    # Detect the facial landmarks
                    landmarks = predictor(gray, dlib_rect)

                    # Draw the facial landmarks on the image
                    for i in range(0, 68):
                        x = landmarks.part(i).x
                        y = landmarks.part(i).y
                        cv2.circle(image, (x, y), 1, (0, 255, 0), -1)

                # Display the video frame
                cv2.imshow(window_name, image)


                # Check for key press to exit
                key = cv2.waitKey(10)
                if key == 13 or key == 27:
                    break
           
        if key==13:
            # saving the last captured frame in local storage
            image_path = fr"{getPath('faces','biometries_data')}\{filename}"
            cv2.imwrite(image_path, image)

        # destroy the window
        cv2.destroyWindow(window_name)

    def encode_faces(self):
        for image in os.listdir('biometries_data/faces'):
            face_image = face_recognition.load_image_file(f'biometries_data/faces/{image}')

            face_encodings = face_recognition.face_encodings(face_image)

            if face_encodings:
                face_encoding = face_encodings[0]
            else:
                # Handle the case when no face is found in the image
                print("No face found in the image")

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)

        print(self.known_face_names)

    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit('Video source not found...')
        
        while True:
            ret, frame = video_capture.read()

            # Create a black rectangle to place the text over
            cv2.rectangle(frame, (0, 0), (640, 20), (0, 0, 255), -1)
            # Display text
            cv2.putText(frame,self.instruction1, (215, 17), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 0, 0), 1,cv2.LINE_AA)

            if self.process_current_frame:
                small_frame = cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5)
                rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

                # Find all faces in the current frame
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                # print(f"Number of faces detected: {len(self.face_locations)}")
                try:
                    self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations, num_jitters=1)
                except Exception as e:
                    print(f"Error extracting face encodings: {e}")
                    self.face_encodings = []

                self.face_names = []
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = 'Unknown'
                    confidence = 'Unknown'

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])

                    
                    self.face_names.append(f'{name} ({confidence})')
            self.process_current_frame = not self.process_current_frame

            # Display annotations
            for(top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 2
                right *= 2
                left *= 2
                bottom *= 2

                # Set the rectangle color based on whether the face is known or unknown
                if 'Unknown' in name:
                    rect_color = (0, 0, 255)  # Red for unknown faces
                else:
                    rect_color = (0, 255, 0)  # Green for known faces

                cv2.rectangle(frame, (left, top), (right, bottom), rect_color, 2)
                cv2.rectangle(frame, (left, bottom-35), (right, bottom), rect_color, -1)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Face Recognition", frame)
            
            key = cv2.waitKey(1)
            # break the loop if 'enter' or 'esc' key is pressed 
            if key == 13 or key ==27:
                break

        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    fr = FaceRecognition()
    fr.enroll_face("runrun.jpg")
    # fr.run_recognition()
