import cv2
import mediapipe as mp
import json

# Initialisiere MediaPipe Hände
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Funktion zum Erfassen von Landmarks
def capture_fist_landmarks():
    cap = cv2.VideoCapture(0)
    fist_landmarks = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Konvertiere das Bild zu RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe um Hände zu erkennen
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Berechne Positionen der Handlandmarks
                landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
                fist_landmarks.append(landmarks)

                # Paint
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Zeige das Bild an
        cv2.imshow('Capture Landmarks', frame)

        # Warte auf Tastendruck "s" zum Speichern der Landmarks und "q" zum Beenden
        key = cv2.waitKey(1)
        if key == ord('s'):
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
                    fist_landmarks.append(landmarks)
                    print("Landmarks gespeichert")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return fist_landmarks

# Erfasse die Landmarks für die geballte Faust
fist_landmarks = capture_fist_landmarks()

# Speichere die Landmarks in einer JSON-Datei
gestures_config = {
    "gestures": [
        {
            "name": "Open Hand",
            "description": "Hand is open.",
            "landmarks": fist_landmarks
        }
    ]
}

with open('open_gesture.json', 'w') as file:
    json.dump(gestures_config, file, indent=4)

print("Landmarks wurden gespeichert.")