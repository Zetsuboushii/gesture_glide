import json
import os

# TODO Frames, etc. aus PoC übernehmen
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


def capture_gesture(mp_wrapper, gesture_name: str):
    def capture_callback(landmarks):
        save_gesture(gesture_name, landmarks)
        print(f"Gesture '{gesture_name}' was saved")

    mp_wrapper.set_capture_callback(capture_callback)
    print("Hold hand still and press 's' to capture the gesture")
