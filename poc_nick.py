import cv2
import mediapipe as mp
import math
from pywinauto import Desktop, application
from pywinauto.keyboard import send_keys

# TODO range of scrolling based on distance between points

# Helper function to calculate Euclidean distance if the distance between x and y is relevant
def get_euclidean_distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def spinRouelett():
    try:
        roulette = desktop.window(class_name="GlassWndClass-GlassWindowClass-2")
        roulette.set_focus()
        send_keys("{SPACE}")
    except:
        print("Glücksrad ist nicht offen")

def scrollAction(window, direction):
    # Simulates mouse wheel actions based on detected hand movement direction
    try:
        wheel_direction = -1 if direction == "Moving Down" else 1
        for _ in range(10):
            window.wheel_mouse_input(wheel_dist=wheel_direction)
    except Exception as e:
        print(e)

def recognize_y_movement(previous_y, current_y, height):
    # Recognizes significant vertical hand movement for scrolling action
    movement_distance = abs(current_y - previous_y)
    movement_threshold = 0.10 * height  # 10% of the frame height
    if movement_distance > movement_threshold:
        if current_y < previous_y:
            return ("Moving Up", movement_distance)
        else:
            return ("Moving Down", movement_distance)

def scrollRecognition():
    # Main function to handle hand recognition and trigger appropriate actions
    print("Starting recognition...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()

    previous_y_center_right = None  # Track previous y-center for right hand

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            results = hands.process(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    if handedness.classification[0].label == 'Right':
                        wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y
                        frame_height = frame.shape[0]

                        if previous_y_center_right is not None:
                            result = recognize_y_movement(previous_y_center_right, wrist_y * frame_height, frame_height)
                            if result:
                                movement_type, value = result
                                if value > 250:  # Ensure movement is significant
                                    print(f"{movement_type} detected with distance {value}")
                                    scrollAction(pdf, movement_type)

                        previous_y_center_right = wrist_y * frame_height

                        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            cv2.imshow('MediaPipe Hands', frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

# start of the program
desktop = Desktop(backend="uia")
pdf = desktop.window(class_name="AcrobatSDIWindow")  # specify the correct class_name as needed
scrollRecognition()
