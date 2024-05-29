import math
import time
from typing import List

import mediapipe as mp
from mediapipe.tasks.python.components.containers import Landmark

from gesture_glide.camera_handler import FrameMetadata
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.utils import Observer, Observable, Handedness, ScrollDirection, Directions, ScrollData, \
    HandMovementState, HandMovementType, HandMovementData, FrameData, get_last_valid_frame_data

# TODO maybe change delta if needed
DELTA_TIME = 0.5
# TODO keep an eye on naming !
INTER_FRAME_MOVEMENT_DETECTION_RELATIVE_DISTANCE_THRESHOLD = 0.03


class HandMovementRecognizer(Observer, Observable):
    def __init__(self, mp_wrapper: MPWrapper):
        super().__init__()
        self.mp_wrapper = mp_wrapper
        self.mp_wrapper.add_observer(self)
        self.previous_y_center_right = None

    def get_past_comparison_hand(self, hand_data_array):
        try:
            return next(x.results for x in hand_data_array if x.time > time.time() - DELTA_TIME)
        except StopIteration:
            return None

    def get_hand_landmark(self, mp_results, target_handedness: Handedness) -> List[Landmark] | None:
        if mp_results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(mp_results.multi_hand_landmarks, mp_results.multi_handedness):
                if handedness.classification[0].label == target_handedness.value:
                    return hand_landmarks
        return None

    def get_euclidean_distance(self, a, b):
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)

    def calculate_movement_data(self, current_wrist, previous_wrist, time_delta):
        movement_flag = False
        euclidean_distance = self.get_euclidean_distance(current_wrist, previous_wrist)

        if euclidean_distance > INTER_FRAME_MOVEMENT_DETECTION_RELATIVE_DISTANCE_THRESHOLD:
            movement_flag = True

        x_movement = current_wrist.x - previous_wrist.x
        y_movement = current_wrist.y - previous_wrist.y

        # Determine the most dominant movement direction
        if abs(x_movement) > abs(y_movement):
            most_dominant_movement = Directions.RIGHT if x_movement > 0 else Directions.LEFT
            speed = abs(x_movement) / time_delta
        else:
            most_dominant_movement = Directions.UP if y_movement < 0 else Directions.DOWN
            speed = abs(y_movement) / time_delta

        return movement_flag, most_dominant_movement, speed

    def determine_hand_movement_state(self, hand_data_array: List[FrameData], time_delta, hand_landmarks_right=None,
                                      hand_landmarks_left=None,
                                      previous_hand_landmarks_right=None, previous_hand_landmarks_left=None):

        current_hand_data = hand_data_array[-1]
        previous_hand_data = hand_data_array[-2]

        current_wrist_right, current_wrist_left = None, None
        previous_wrist_right, previous_wrist_left = None, None
        left_hand_movement_detected, right_hand_movement_detected = False, False
        right_hand_movement_direction, left_hand_movement_direction = False, False
        right_hand_speed, left_hand_speed = None, None

        if hand_landmarks_right and previous_hand_landmarks_right:
            current_wrist_right = hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            previous_wrist_right = previous_hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            right_hand_movement_detected, right_hand_movement_direction, right_hand_speed = self.calculate_movement_data(
                current_wrist_right, previous_wrist_right, time_delta)

        if hand_landmarks_left and previous_hand_landmarks_left:
            current_wrist_left = hand_landmarks_left.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            previous_wrist_left = previous_hand_landmarks_left.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            left_hand_movement_detected, left_hand_movement_direction, left_hand_speed = self.calculate_movement_data(
                current_wrist_left, previous_wrist_left, time_delta)

        current_hand_data.left_hand_movement_data.speed = left_hand_speed
        current_hand_data.right_hand_movement_data.speed = right_hand_speed
        current_hand_data.left_hand_movement_data.direction = left_hand_movement_direction
        current_hand_data.right_hand_movement_data.direction = right_hand_movement_direction

        self.apply_hand_movement_state_for_hand(left_hand_movement_detected, left_hand_movement_direction,
                                                hand_data_array, Handedness.LEFT)

        self.apply_hand_movement_state_for_hand(right_hand_movement_detected, right_hand_movement_direction,
                                                hand_data_array, Handedness.RIGHT)

    def apply_hand_movement_state_for_hand(self, hand_movement_detected: bool, hand_movement_direction: Directions,
                                           hand_data_array: List[FrameData], handedness: Handedness):
        previous_frame_data, current_frame_data = hand_data_array[-2], hand_data_array[-1]
        previous_hand_data = self.get_hand_movement_data(previous_frame_data, handedness)
        current_hand_data = self.get_hand_movement_data(current_frame_data, handedness)

        match previous_hand_data.hand_movement_state:
            case HandMovementState.NO_MOVEMENT:
                current_hand_data.hand_movement_state = HandMovementState.MOVEMENT_BEGIN if (
                    hand_movement_detected) else HandMovementState.NO_MOVEMENT
                if hand_movement_direction in {Directions.UP, Directions.DOWN}:
                    current_hand_data.hand_movement_type = HandMovementType.SCROLLING
            case HandMovementState.MOVEMENT_BEGIN:
                if hand_movement_detected:
                    current_hand_data.hand_movement_state = HandMovementState.IN_MOVEMENT
                else:
                    current_hand_data.hand_movement_state = HandMovementState.QUASI_END
                    current_hand_data.hand_movement_type = HandMovementType.NONE
            case HandMovementState.IN_MOVEMENT:
                if hand_movement_detected:
                    current_hand_data.hand_movement_state = HandMovementState.IN_MOVEMENT
                else:
                    current_hand_data.hand_movement_state = HandMovementState.QUASI_END
                    current_hand_data.hand_movement_type = HandMovementType.NONE
            case HandMovementState.QUASI_END:
                if hand_movement_detected:
                    current_hand_data.hand_movement_state = HandMovementState.IN_MOVEMENT
                else:
                    if all(self.get_hand_movement_data(frame_data, handedness) == HandMovementState.QUASI_END for
                           frame_data in hand_data_array[-4:-2]):
                        current_hand_data.hand_movement_state = HandMovementState.MOVEMENT_END
                        current_hand_data.hand_movement_type = HandMovementType.NONE
                    else:
                        current_hand_data.hand_movement_state = HandMovementState.QUASI_END
            case HandMovementState.MOVEMENT_END:
                # One frame buffer before a new movement can begin
                current_hand_data.hand_movement_state = HandMovementState.NO_MOVEMENT
            case state if state is None:
                current_hand_data.hand_movement_state = HandMovementState.NO_MOVEMENT

    def get_hand_movement_data(self, frame_data: FrameData, handedness: Handedness) -> HandMovementData:
        current_hand_data = frame_data.left_hand_movement_data if handedness == Handedness.LEFT else frame_data.right_hand_movement_data
        return current_hand_data

    def recognize_y_movement(self, previous_y, current_y, height) -> ScrollData | None:
        # Recognizes significant vertical hand movement for scrolling action
        movement_distance = abs(current_y - previous_y)
        # TODO maybe adjust threshold if needed
        movement_threshold = 0.20 * height  # 20% of the frame height
        if movement_distance > movement_threshold:
            return ScrollData(ScrollDirection.UP if current_y < previous_y else ScrollDirection.DOWN, movement_distance)

    def calculate_movement_command(self, frame_height, hand_landmarks_right, kwargs, scroll_command):
        if hand_landmarks_right:
            wrist_y_right = hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST].y
            previous_hand_landmarks = self.get_hand_landmark(
                self.get_past_comparison_hand(kwargs["hand_data_buffer"]),
                Handedness.RIGHT)
            if previous_hand_landmarks is not None:
                previous_wrist_y = previous_hand_landmarks.landmark[
                                       self.mp_wrapper.mp_hands.HandLandmark.WRIST].y * frame_height
            else:
                previous_wrist_y = None

            if previous_wrist_y is not None:
                # scroll_command = self.recognize_y_movement(previous_wrist_y, wrist_y_right * frame_height,
                #                                            frame_height)
                pass

        return scroll_command

    def update(self, observable, *args, **kwargs):
        metadata: FrameMetadata = kwargs["metadata"]
        hand_data_buffer: List[FrameData] = kwargs["hand_data_buffer"]
        scroll_command: ScrollData | None = None
        frame = kwargs["frame"]
        frame_height = metadata.height
        hand_landmarks_left, hand_landmarks_right = None, None

        current_hand_data = hand_data_buffer[-1].results
        previous_hand_data = hand_data_buffer[-2].results

        current_time = hand_data_buffer[-1].time
        previous_time = hand_data_buffer[-2].time
        time_between_frames = current_time - previous_time

        hand_landmarks_right = self.get_hand_landmark(current_hand_data, Handedness.RIGHT)
        hand_landmarks_left = self.get_hand_landmark(current_hand_data, Handedness.LEFT)
        previous_hand_landmarks_right = self.get_hand_landmark(previous_hand_data, Handedness.RIGHT)
        previous_hand_landmarks_left = self.get_hand_landmark(previous_hand_data, Handedness.LEFT)

        right_distance_str = ""
        left_distance_str = ""

        hand_data_buffer[-1].left_hand_movement_data = HandMovementData(Handedness.LEFT, HandMovementState.NO_MOVEMENT, None, None, None)
        hand_data_buffer[-1].right_hand_movement_data = HandMovementData(Handedness.RIGHT, HandMovementState.NO_MOVEMENT, None, None, None)

        any_hand_detected = False
        if hand_landmarks_right is None:
            self.handle_empty_current_frame(hand_data_buffer, Handedness.RIGHT)
            any_hand_detected = True
        if hand_landmarks_left is None:
            self.handle_empty_current_frame(hand_data_buffer, Handedness.LEFT)
            any_hand_detected = True
        if any_hand_detected:
            self.determine_hand_movement_state(hand_data_buffer, time_between_frames, hand_landmarks_right,
                                               hand_landmarks_left,
                                               previous_hand_landmarks_right, previous_hand_landmarks_left)
        movement_state_str_r = f"R: Movement State: {hand_data_buffer[-1].right_hand_movement_data.hand_movement_state.name}"
        movement_state_str_l = f"L: Movement State: {hand_data_buffer[-1].left_hand_movement_data.hand_movement_state.name}"

        scroll_command = self.calculate_movement_command(frame_height, hand_landmarks_right,
                                                         kwargs,
                                                         scroll_command)

        if hand_landmarks_right and previous_hand_landmarks_right:
            current_wrist_right = hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            previous_wrist_right = previous_hand_landmarks_right.landmark[
                self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            euclidean_distance_right = self.get_euclidean_distance(current_wrist_right, previous_wrist_right)
            right_distance_str = f"Right Distance: {euclidean_distance_right:.3f}"

        if hand_landmarks_left and previous_hand_landmarks_left:
            current_wrist_left = hand_landmarks_left.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            previous_wrist_left = previous_hand_landmarks_left.landmark[
                self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            euclidean_distance_left = self.get_euclidean_distance(current_wrist_left, previous_wrist_left)
            left_distance_str = f"Left Distance: {euclidean_distance_left:.3f}"

        print(f"time between frames: {time_between_frames:.3f}", end=" ")
        if movement_state_str_r:
            print(movement_state_str_r, end=" ")
        if movement_state_str_l:
            print(movement_state_str_l, end=" ")
        if right_distance_str:
            print(right_distance_str, end=" ")
        if left_distance_str:
            print(left_distance_str, end=" ")
        print()

        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks_right,
                                                  self.mp_wrapper.mp_hands.HAND_CONNECTIONS)
        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks_left,
                                                  self.mp_wrapper.mp_hands.HAND_CONNECTIONS)

        send_scroll_command = False
        if scroll_command is not None:
            print(f"Sending scroll command: {scroll_command}")
            send_scroll_command = True

        self.notify_observers(scroll_command=scroll_command if send_scroll_command else None,
                              scroll_overlay=frame)

    def handle_empty_current_frame(self, hand_data_buffer: List[FrameData], handedness: Handedness):
        previous_movement_data = self.get_hand_movement_data(hand_data_buffer[-2], handedness)
        current_movement_data = self.get_hand_movement_data(hand_data_buffer[-1], handedness)


        if previous_movement_data is None:
            current_movement_data.hand_movement_state = HandMovementState.NO_MOVEMENT
            return

        current_movement_data.hand_movement_type = previous_movement_data.hand_movement_type
        match previous_movement_data.hand_movement_state:
            case (HandMovementState.MOVEMENT_BEGIN | HandMovementState.IN_MOVEMENT):
                current_movement_data.hand_movement_state = HandMovementState.QUASI_END
            case (HandMovementState.NO_MOVEMENT | HandMovementState.MOVEMENT_END):
                current_movement_data.hand_movement_state = HandMovementState.NO_MOVEMENT
            case HandMovementState.QUASI_END:
                if all(self.get_hand_movement_data(frame_data, handedness) == HandMovementState.QUASI_END for
                       frame_data in hand_data_buffer[-4:-2]):
                    current_movement_data.hand_movement_state = HandMovementState.MOVEMENT_END
                    current_movement_data.hand_movement_type = HandMovementType.NONE
                else:
                    current_movement_data.hand_movement_state = HandMovementState.QUASI_END

# TODO a lot
#   checken ob current leer, wenn ja wird er zu quasi -> check if in full buffer die letzten 3 auch quasi, wenn ja ENDE-State, wenn nein nächsten Frame bearbeiten
#   wenn current nicht leer -> daten aus zuletzt gültigen Frame nehmen und den State und die Distanze vergleichen und berechnungen anstellen -> neuer State wird anhand des Switchcases ermittelt
#   beachte die Daten der letzten gültigen Hand als Tupel abzulegen, weil rechte und linke hand seperat benötigt und wir brauchen kein Buffer dafür, weil wir maximal den previous gültigen Frame brauchen
#   in die Vergangenheit gucken wir eh nur beim full buffer, falls ein qusi auftritt, um END zustand zu ermitteln (falls hand still gehalten wird oder zu lang nicht das ist bpsw. aus dem Screen gegangen)