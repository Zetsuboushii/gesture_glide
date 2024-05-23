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
INTER_FRAME_MOVEMENT_DETECTION_RELATIVE_DISTANCE_THRESHOLD = 0.05


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
        self.previous_thumb_index_distance = None
        self.hand_start_time = None

    def get_past_comparison_hand(self, hand_data_array):
        return next(x.results for x in hand_data_array if x.time > time.time() - DELTA_TIME)

    def get_hand_landmark(self, hands, target_handedness: Handedness):
        if hands.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(hands.multi_hand_landmarks, hands.multi_handedness):
                if handedness.classification[0].label == target_handedness.value:
                    return hand_landmarks
        return None

    def get_euclidean_distance(self, a, b):
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)

    def determine_hand_movement_state(self, hand_data_array, hand_landmarks_right, hand_landmarks_left,
                                      previous_hand_landmarks_right, previous_hand_landmarks_left, height):
        distance_threshold = INTER_FRAME_MOVEMENT_DETECTION_RELATIVE_DISTANCE_THRESHOLD * height

        current_hand_data = hand_data_array[-1]
        previous_hand_data = hand_data_array[-2]

        current_wrist_right = hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
        current_wrist_left = hand_landmarks_left.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]

        previous_wrist_right = previous_hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
        previous_wrist_left = previous_hand_landmarks_left.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]

        euclidean_distance_right = self.get_euclidean_distance(current_wrist_right, previous_wrist_right)
        euclidean_distance_left = self.get_euclidean_distance(current_wrist_left, previous_wrist_left)

        left_hand_movement, right_hand_movement = False, False

        if euclidean_distance_right > distance_threshold:
            right_hand_movement = True
        if euclidean_distance_left > distance_threshold:
            left_hand_movement = True

        match previous_hand_data.hand_movement_state:
            case HandMovementState.NO_MOVEMENT:
                if left_hand_movement or right_hand_movement:
                    current_hand_data.hand_movement_state = HandMovementState.MOVEMENT_BEGIN
                if right_hand_movement and not left_hand_movement:
                    current_hand_data.hand_movement_type = HandMovementType.SCROLLING
                if left_hand_movement and right_hand_movement:
                    current_hand_data.hand_movement_type = HandMovementType.ZOOMING
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

    # TODO check for MOVEMENT_END if yes -> calc distance between start and end and check HandMovementType,
    #  then accordingly send recognized gesture and distance to observers

    def recognize_y_movement(self, previous_y, current_y, height) -> ScrollData | None:
        # Recognizes significant vertical hand movement for scrolling action
        movement_distance = abs(current_y - previous_y)
        # TODO maybe adjust threshold if needed
        movement_threshold = 0.20 * height  # 20% of the frame height
        if movement_distance > movement_threshold:
            return ScrollData(ScrollDirection.UP if current_y < previous_y else ScrollDirection.DOWN, movement_distance)

    def recognize_zoom_movement(self, previous_distance, current_distance) -> ZoomData | None:
        # Recognizes changes in the distance between thumb and index finger for zooming
        distance_change = abs(current_distance - previous_distance)
        zoom_threshold = 0.05  # Change this threshold as needed
        if distance_change > zoom_threshold:
            return ZoomData(False if current_distance > previous_distance else True, distance_change)

    def update(self, observable, *args, **kwargs):
        metadata: FrameMetadata = kwargs["metadata"]
        current_hand_data = kwargs["hand_data_buffer"][-1].results
        frame = kwargs["frame"]
        scroll_command: ScrollData | None = None
        zoom_command: ZoomData | None = None

        frame_height = metadata.height

        hand_landmarks_right = self.get_hand_landmark(current_hand_data, Handedness.RIGHT)
        hand_landmarks_left = self.get_hand_landmark(current_hand_data, Handedness.LEFT)

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

            thumb_tip = hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks_right.landmark[self.mp_wrapper.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            current_thumb_index_distance = self.get_euclidean_distance(thumb_tip, index_tip)

            # TODO change to work with frame array like scrolling
            if self.previous_thumb_index_distance is not None:
                zoom_command = self.recognize_zoom_movement(self.previous_thumb_index_distance,
                                                            current_thumb_index_distance)

            self.previous_thumb_index_distance = current_thumb_index_distance

        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks_right,
                                                  self.mp_wrapper.mp_hands.HAND_CONNECTIONS)
        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks_left,
                                                  self.mp_wrapper.mp_hands.HAND_CONNECTIONS)

        send_scroll_command = False
        send_zoom_command = False
        if scroll_command is not None:
            print(f"Sending scroll command: {scroll_command}")
            send_scroll_command = True
        if zoom_command is not None and zoom_command.scale > 0.15:
            print(f"Sending zoom command: {zoom_command}")
            send_zoom_command = True

        self.notify_observers(scroll_command=scroll_command if send_scroll_command else None,
                              zoom_command=zoom_command if send_zoom_command else None,
                              scroll_overlay=frame,
                              zoom_overlay=frame)
