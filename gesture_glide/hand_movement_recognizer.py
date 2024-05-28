import enum
import math
import time

import cv2
import mediapipe as mp

from gesture_glide.camera_handler import FrameMetadata
from gesture_glide.mp_wrapper import MPWrapper, HandMovementState, HandMovementType
from gesture_glide.utils import Observer, Observable

# TODO maybe change delta if needed
DELTA_TIME = 0.5
# TODO keep an eye on naming !
INTER_FRAME_MOVEMENT_DETECTION_RELATIVE_DISTANCE_THRESHOLD = 0.01


class Handedness(enum.StrEnum):
    LEFT = "Left"
    RIGHT = "Right"


class ScrollDirection(enum.Enum):
    UP = 1
    DOWN = -1


class ScrollData:
    direction: ScrollDirection
    distance: float
    duration: float

    def __init__(self, direction: ScrollDirection, distance: float, duration: float = None):
        self.direction = direction
        self.distance = distance
        self.duration = duration if duration is not None else 1.

    def __str__(self):
        return f"<ScrollData(direction={self.direction}, distance={self.distance}, duration={self.duration})>"


class ZoomData:
    zoom_in: bool
    scale: float

    def __init__(self, zoom_in: bool, scale: float):
        self.zoom_in = zoom_in
        self.scale = scale

    def __str__(self):
        return f"<ZoomData(zoom_in={self.zoom_in}, scale={self.scale})>"


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

    def get_hand_landmark(self, hands, target_handedness: Handedness):
        if hands.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(hands.multi_hand_landmarks, hands.multi_handedness):
                if handedness.classification[0].label == target_handedness.value:
                    return hand_landmarks
        return None

    def get_euclidean_distance(self, a, b):
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


    def determine_hand_movement_state(self, hand_data_array, hand_landmarks_right=None, hand_landmarks_left=None,
                                  previous_hand_landmarks_right=None, previous_hand_landmarks_left=None, height=None):
        distance_threshold = INTER_FRAME_MOVEMENT_DETECTION_RELATIVE_DISTANCE_THRESHOLD * height

        current_hand_data = hand_data_array[-1]
        previous_hand_data = hand_data_array[-2]

        current_wrist_right, current_wrist_left = None, None
        previous_wrist_right, previous_wrist_left = None, None
        euclidean_distance_right, euclidean_distance_left = 0, 0
        left_hand_movement, right_hand_movement = False, False

        # TODO Check why no movement

        if hand_landmarks_right and previous_hand_landmarks_right:
            current_wrist_right = hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            previous_wrist_right = previous_hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            euclidean_distance_right = self.get_euclidean_distance(current_wrist_right, previous_wrist_right)
            if euclidean_distance_right > distance_threshold:
                right_hand_movement = True

        if hand_landmarks_left and previous_hand_landmarks_left:
            current_wrist_left = hand_landmarks_left.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            previous_wrist_left = previous_hand_landmarks_left.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
            euclidean_distance_left = self.get_euclidean_distance(current_wrist_left, previous_wrist_left)
            if euclidean_distance_left > distance_threshold:
                left_hand_movement = True

        match previous_hand_data.hand_movement_state:
            case HandMovementState.NO_MOVEMENT:
                if left_hand_movement or right_hand_movement:
                    current_hand_data.hand_movement_state = HandMovementState.MOVEMENT_BEGIN
                else:
                    current_hand_data.hand_movement_state = HandMovementState.NO_MOVEMENT
                if right_hand_movement and not left_hand_movement:
                    current_hand_data.hand_movement_type = HandMovementType.SCROLLING
            case HandMovementState.MOVEMENT_BEGIN:
                if left_hand_movement or right_hand_movement:
                    current_hand_data.hand_movement_state = HandMovementState.IN_MOVEMENT
            case HandMovementState.IN_MOVEMENT:
                if left_hand_movement or right_hand_movement:
                    current_hand_data.hand_movement_state = HandMovementState.IN_MOVEMENT
                else:
                    current_hand_data.hand_movement_state = HandMovementState.MOVEMENT_END
                    current_hand_data.hand_movement_type = HandMovementType.NONE
            case HandMovementState.MOVEMENT_END:
                # One frame a buffer before a new movement can begin
                current_hand_data.hand_movement_state = HandMovementState.NO_MOVEMENT
            case state if state is None:
                current_hand_data.hand_movement_state = HandMovementState.NO_MOVEMENT

    # TODO check for MOVEMENT_END if yes -> calc distance between start and end and check HandMovementType,
    #  then accordingly send recognized gesture and distance to observers

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
                scroll_command = self.recognize_y_movement(previous_wrist_y, wrist_y_right * frame_height,
                                                           frame_height)

        return scroll_command

    def update(self, observable, *args, **kwargs):
        metadata: FrameMetadata = kwargs["metadata"]
        hand_data_buffer = kwargs["hand_data_buffer"]
        scroll_command: ScrollData | None = None
        frame = kwargs["frame"]
        frame_height = metadata.height
        hand_landmarks_left, hand_landmarks_right = None, None

        # If only one frame is stored don't do anything
        if not len(hand_data_buffer) < 2:
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

            if hand_landmarks_right or hand_landmarks_left:
                self.determine_hand_movement_state(hand_data_buffer, hand_landmarks_right, hand_landmarks_left,
                                               previous_hand_landmarks_right, previous_hand_landmarks_left,
                                               frame_height)
                # print(hand_data_buffer[-1].hand_movement_state, hand_data_buffer[-1].hand_movement_type)

                scroll_command = self.calculate_movement_command(frame_height, hand_landmarks_right,
                                                             kwargs,
                                                             scroll_command)

                if hand_landmarks_right and previous_hand_landmarks_right:
                    current_wrist_right = hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
                    previous_wrist_right = previous_hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
                    euclidean_distance_right = self.get_euclidean_distance(current_wrist_right, previous_wrist_right)
                    right_distance_str = f"Right Distance: {euclidean_distance_right:.2f}"

                if hand_landmarks_left and previous_hand_landmarks_left:
                    current_wrist_left = hand_landmarks_left.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
                    previous_wrist_left = previous_hand_landmarks_left.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
                    euclidean_distance_left = self.get_euclidean_distance(current_wrist_left, previous_wrist_left)
                    left_distance_str = f"Left Distance: {euclidean_distance_left:.2f}"

                print(f"time between frames: {time_between_frames:.2f}", end=" ")
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