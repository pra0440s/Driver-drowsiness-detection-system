import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance

# Eye landmark indices (MediaPipe)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# EAR calculation function
def calculate_EAR(eye_landmarks, img_width, img_height):
    p1 = np.array([eye_landmarks[0].x * img_width, eye_landmarks[0].y * img_height])
    p2 = np.array([eye_landmarks[1].x * img_width, eye_landmarks[1].y * img_height])
    p3 = np.array([eye_landmarks[2].x * img_width, eye_landmarks[2].y * img_height])
    p4 = np.array([eye_landmarks[3].x * img_width, eye_landmarks[3].y * img_height])
    p5 = np.array([eye_landmarks[4].x * img_width, eye_landmarks[4].y * img_height])
    p6 = np.array([eye_landmarks[5].x * img_width, eye_landmarks[5].y * img_height])
    ear = (distance.euclidean(p2, p6) + distance.euclidean(p3, p5)) / (2.0 * distance.euclidean(p1, p4))
    return ear

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Open webcam
cap = cv2.VideoCapture(0)

# Drowsiness parameters
EAR_THRESHOLD = 0.20
CONSEC_FRAMES = 50

frame_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            left_eye_landmarks = [landmarks.landmark[i] for i in LEFT_EYE]
            right_eye_landmarks = [landmarks.landmark[i] for i in RIGHT_EYE]
            # Print coordinates for left eye landmarks
            print("Left Eye Landmarks:")
            for i, lm in enumerate(left_eye_landmarks):
                print(f"Landmark {LEFT_EYE[i]}: x={lm.x:.3f}, y={lm.y:.3f}")

            # Print coordinates for right eye landmarks
            print("Right Eye Landmarks:")
            for i, lm in enumerate(right_eye_landmarks):
                print(f"Landmark {RIGHT_EYE[i]}: x={lm.x:.3f}, y={lm.y:.3f}")

            # Draw green circles on eyes
            for lm in LEFT_EYE + RIGHT_EYE:
                x, y = int(landmarks.landmark[lm].x * w), int(landmarks.landmark[lm].y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                #cv2.putText(frame, f"({landmarks.landmark[lm].x:.2f}, {landmarks.landmark[lm].y:.2f})",
                #(x + 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            left_ear = calculate_EAR(left_eye_landmarks, w, h)
            right_ear = calculate_EAR(right_eye_landmarks, w, h)
            avg_ear = (left_ear + right_ear) / 2.0

            # Display EAR
            cv2.putText(frame, f'EAR: {avg_ear:.2f}', (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            # Drowsiness detection logic
            if avg_ear < EAR_THRESHOLD:
                frame_counter += 1
                if frame_counter >= CONSEC_FRAMES:
                    cv2.putText(frame, "DROWSY ALERT!", (30, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            else:
                frame_counter = 0

    cv2.imshow("Driver Drowsiness Detection", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()

