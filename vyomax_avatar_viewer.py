# face_detector.py

import cv2
import face_recognition
import os
# No Pygame here

FACES_DIR_FD = "known_faces/" # Using _FD to avoid conflict if robot.py also defines FACES_DIR
KNOWN_FACE_ENCODINGS_FD = []
KNOWN_FACE_NAMES_FD = []

def load_known_faces_from_detector():
    global KNOWN_FACE_ENCODINGS_FD, KNOWN_FACE_NAMES_FD
    KNOWN_FACE_ENCODINGS_FD = [] # Clear previous
    KNOWN_FACE_NAMES_FD = []

    if not os.path.exists(FACES_DIR_FD):
        print(f"FaceDetector: Directory '{FACES_DIR_FD}' not found.")
        return False

    print(f"FaceDetector: Loading known faces from {FACES_DIR_FD}...")
    loaded_count = 0
    for filename in os.listdir(FACES_DIR_FD):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(filename)[0].title()
            image_path = os.path.join(FACES_DIR_FD, filename)
            try:
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    KNOWN_FACE_ENCODINGS_FD.append(encodings[0])
                    KNOWN_FACE_NAMES_FD.append(name)
                    print(f"FaceDetector: Loaded face - {name}")
                    loaded_count += 1
                else:
                    print(f"FaceDetector: No face found in {image_path} for {name}.")
            except Exception as e:
                print(f"FaceDetector: Error loading {image_path}: {e}")
    
    if loaded_count > 0:
        print(f"FaceDetector: Successfully loaded {loaded_count} known faces.")
        return True
    else:
        print("FaceDetector: No known faces were successfully loaded.")
        return False


def recognize_face_from_cam_detector(timeout_seconds=10):
    """
    Tries to recognize a face from the webcam for a given duration.
    Returns the name of the recognized person or None.
    This function will show a CV2 window for the camera feed.
    """
    if not KNOWN_FACE_ENCODINGS_FD:
        print("FaceDetector: No known faces loaded to compare against.")
        return None

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("FaceDetector: Error - Could not open video camera.")
        return None

    print("FaceDetector: Starting face recognition from camera... (Press 'q' in CV2 window to skip)")
    
    start_time = time.time()
    recognized_name = None

    while (time.time() - start_time) < timeout_seconds:
        ret, frame = video_capture.read()
        if not ret:
            print("FaceDetector: Error - Failed to capture frame.")
            break

        # Resize for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        try:
            face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
            face_encodings_in_frame = face_recognition.face_encodings(rgb_small_frame, face_locations)
        except Exception as e:
            print(f"FaceDetector: Error in face detection/encoding step: {e}")
            # This can be the dlib TypeError if installation is an issue
            break 

        for face_encoding in face_encodings_in_frame:
            matches = face_recognition.compare_faces(KNOWN_FACE_ENCODINGS_FD, face_encoding, tolerance=0.6)
            name_match = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name_match = KNOWN_FACE_NAMES_FD[first_match_index]
                recognized_name = name_match
                print(f"FaceDetector: Recognized {recognized_name}")
                break # Found one, exit inner loop
        
        if recognized_name:
            break # Exit outer (time-based) loop

        # Display the resulting image (optional, but helpful for user)
        for (top, right, bottom, left) in face_locations:
            top *= 4; right *= 4; bottom *= 4; left *= 4 # Scale back up
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Determine name to display for this box
            temp_name_disp = "Unknown"
            # (Could re-run comparison here for display if needed, or use last recognized if only one face)
            if recognized_name and len(face_locations) == 1: # Simple case: if one face and it's recognized
                 temp_name_disp = recognized_name

            cv2.putText(frame, temp_name_disp, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
        
        cv2.imshow("Face Recognition (detector)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("FaceDetector: Face recognition skipped by user.")
            break
            
    video_capture.release()
    cv2.destroyAllWindows()
    return recognized_name

if __name__ == '__main__':
    # Test functions
    import time
    if load_known_faces_from_detector():
        print("\nAttempting to recognize a face for 10 seconds...")
        name = recognize_face_from_cam_detector(timeout_seconds=10)
        if name:
            print(f"Test: Recognized - {name}")
        else:
            print("Test: No known face recognized or skipped.")
    else:
        print("Test: Could not load known faces.")
