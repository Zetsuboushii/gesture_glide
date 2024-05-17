import cv2
import mediapipe as mp
import json
import os

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def capture_gesture(gesture_name: str):
    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands()
    landmarks = []

    print("Hold hand still and press 's' to capture the gesture")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imshow("GestureCapturer", image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            if landmarks:
                save_gesture(gesture_name, landmarks)
                print(f"Gesture '{gesture_name}' was saved")
                break
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def save_gesture(gesture_name: str, landmarks: list):
    gesture_data = {gesture_name: landmarks}
    if os.path.exists("gesture_config.json"):
        with open("gesture_config.json", "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
        data.update(gesture_data)
    else:
        data = gesture_data

    with open("gesture_config.json", "w") as file:
        json.dump(data, file, indent=4)


def recognize_gesture():
    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands()

    if os.path.exists('gesture_config.json'):
        with open('gesture_config.json', 'r') as file:
            try:
                gesture_data = json.load(file)
            except json.JSONDecodeError:
                gesture_data = {}
    else:
        gesture_data = {}

    print("Recognition started. Press 'q' to quit")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                current_landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

                for gesture_name, stored_landmarks in gesture_data.items():
                    if compare_landmarks(current_landmarks, stored_landmarks):
                        print(f"Erkannte Geste: {gesture_name}")
                        break

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imshow('GestureRecognizer', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def compare_landmarks(current, stored, threshold=0.1):
    if len(current) != len(stored):
        return False

    for i in range(len(current)):
        cx, cy, cz = current[i]
        sx, sy, sz = stored[i]
        if abs(cx - sx) > threshold or abs(cy - sy) > threshold or abs(cz - sz) > threshold:
            return False

    return True


if __name__ == "__main__":
    while True:
        print("Options: (1) Capture a new gesture, (2) Recognize a gesture, (q) Quit")
        option = input("Enter your option: ")

        if option == "1":
            gesture_name = input("Enter your gesture name: ")
            capture_gesture(gesture_name)
        elif option == "2":
            recognize_gesture()
        elif option == "q":
            break
        else:
            print("Invalid option")