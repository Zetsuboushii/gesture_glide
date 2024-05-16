import cv2
import mediapipe as mp
import json
import numpy as np

# Lade Gesten Config File
with open('fist_gesture.json', 'r') as file:
    gestures_config = json.load(file)

# Initialisiere MediaPipe Hände
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Klasse zur Aufzeichnung von Landmarks über die Zeit
class LandmarkRecorder:
    def __init__(self):
        self.landmarks_history = []

    def add_landmarks(self, landmarks):
        self.landmarks_history.append(landmarks)

# Funktion zum Erkennen von Handgesten und Aufzeichnen der Landmarks
def detect_and_record_landmarks(frame, landmark_recorder):
    # Konvertiere das Bild zu RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # MediaPipe um Hände zu erkennen
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Berechne Positionen der Handlandmarks
            landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
            landmark_recorder.add_landmarks(landmarks)

            # Durchlaufe die definierten Gesten und vergleiche die Landmarks
            for gesture in gestures_config['gestures']:
                for ref_landmarks in gesture['landmarks']:
                    if compare_landmarks(landmarks, ref_landmarks):
                        print("Erkannte Geste:", gesture['name'], "-", gesture['description'])
                        break

            # Paint
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    return frame

# Funktion zum Vergleichen von Landmarks
def compare_landmarks(landmarks1, landmarks2):
    # Normiere die Landmarks
    landmarks1 = np.array(landmarks1)
    landmarks2 = np.array(landmarks2)

    def normalize(landmarks):
        mean = np.mean(landmarks, axis=0)
        max_dist = np.max(np.linalg.norm(landmarks - mean, axis=1))
        return (landmarks - mean) / max_dist

    normalized_landmarks1 = normalize(landmarks1)
    normalized_landmarks2 = normalize(landmarks2)

    # Berechne Euklidischen Abstand für threshold
    threshold = 0.1
    distances = np.linalg.norm(normalized_landmarks1 - normalized_landmarks2, axis=1)
    mean_distance = np.mean(distances)

    # Debugging-Ausgabe
    return mean_distance < threshold

# Mao Zhedong Surveillance Activated
cap = cv2.VideoCapture(0)
landmark_recorder = LandmarkRecorder()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Erkenne Handgesten und zeichne Landmarks auf
    frame = detect_and_record_landmarks(frame, landmark_recorder)

    # Zeige das Bild an
    cv2.imshow('Hand Gestures', frame)

    # Warte auf Tastendruck "t" zum Ausgeben der Landmarks
    key = cv2.waitKey(1)
    if key == ord('t'):
        landmark_recorder.print_landmarks()

    if key & 0xFF == ord('q'):
        break

# Die
cap.release()
cv2.destroyAllWindows()
