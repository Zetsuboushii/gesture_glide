import logging
import math
import time
from typing import List

import mediapipe as mp
from mediapipe.tasks.python.components.containers import Landmark

from gesture_glide.camera_handler import FrameMetadata
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.utils import Observer, Observable, Handedness, ScrollDirection, Directions, \
    ScrollData, \
    HandMovementState, HandMovementType, HandMovementData, FrameData

# TODO maybe change delta if needed
DELTA_TIME = 0.5
# TODO keep an eye on naming !
INTER_FRAME_MOVEMENT_DETECTION_RELATIVE_SPEED_THRESHOLD = 0.10
SCROLL_COMMAND_SPEED_THRESHOLD = 0.25
HAND_TRANSFER_MAXIMUM_WRIST_DISTANCE_THRESHOLD = 0.15 # Treshold for detecting that 2 hands transferred detected side (for mono hand)
SCROLL_ENABLEMENT_SPREAD_DELTA_THRESHOLD = 93


class HandMovementRecognizer(Observer, Observable):
    last_valid_right_hand_frame_data: FrameData | None
    last_valid_left_hand_frame_data: FrameData | None

    def __init__(self, mp_wrapper: MPWrapper):
        super().__init__()
        self.mp_wrapper = mp_wrapper
        self.mp_wrapper.add_observer(self)
        self.previous_y_center_right = None
        self.last_valid_right_hand_frame_data = None
        self.last_valid_left_hand_frame_data = None

    def get_past_comparison_hand(self, hand_data_buffer):
        try:
            return next(x.results for x in hand_data_buffer if x.time > time.time() - DELTA_TIME)
        except StopIteration:
            return None

    def get_hand_spread(self, landmarks: List[Landmark]) -> float | None:
        if len(landmarks) < 2:
            return None
        combinations = [(a, b) for a in landmarks for b in landmarks if a != b]
        return sum(abs(a.x - b.x) + abs(a.y - b.y) + abs(a.z - b.z) for a, b in
                   combinations)

    def get_hand_landmark(self, mp_results, target_handedness: Handedness) -> List[Landmark] | None:
        if mp_results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(mp_results.multi_hand_landmarks,
                                                  mp_results.multi_handedness):
                if handedness.classification[0].label == target_handedness.value:
                    return hand_landmarks
        return None

    def get_euclidean_distance(self, a, b):
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)

    def calculate_movement_data(self, current_wrist: float, previous_wrist: float, time_delta):
        movement_flag = False

        x_movement = current_wrist.x - previous_wrist.x
        y_movement = current_wrist.y - previous_wrist.y

        # Determine the most dominant movement direction
        if abs(x_movement) > abs(y_movement):
            most_dominant_movement = Directions.RIGHT if x_movement > 0 else Directions.LEFT
            speed = abs(x_movement) / time_delta
        else:
            most_dominant_movement = Directions.UP if y_movement < 0 else Directions.DOWN
            speed = abs(y_movement) / time_delta

        if speed > INTER_FRAME_MOVEMENT_DETECTION_RELATIVE_SPEED_THRESHOLD:
            movement_flag = True

        return movement_flag, most_dominant_movement, speed

    def determine_hand_movement_state(self, hand_data_buffer: List[FrameData],
                                      time_delta_left: float | None,
                                      time_delta_right: float | None,
                                      hand_landmarks_right=None,
                                      hand_landmarks_left=None,
                                      previous_hand_landmarks_right=None,
                                      previous_hand_landmarks_left=None):

        current_hand_data = hand_data_buffer[-1]

        right_hand_movement_detected, right_hand_movement_direction, right_hand_speed = self.calculcate_movement_data_for_hand_with_fallback(
            previous_hand_landmarks_right, hand_landmarks_right, time_delta_right, Handedness.RIGHT)
        left_hand_movement_detected, left_hand_movement_direction, left_hand_speed = self.calculcate_movement_data_for_hand_with_fallback(
            previous_hand_landmarks_left, hand_landmarks_left, time_delta_left, Handedness.LEFT)

        logging.debug("Left movement: ", left_hand_movement_detected, end="")
        logging.debug("Right movement: ", right_hand_movement_detected, end="")
        logging.debug("Left speed: ", left_hand_speed, end="")
        logging.debug("Right speed: ", right_hand_speed, end="")

        current_hand_data.left_hand_movement_data.speed = left_hand_speed
        current_hand_data.right_hand_movement_data.speed = right_hand_speed
        current_hand_data.left_hand_movement_data.direction = left_hand_movement_direction
        current_hand_data.right_hand_movement_data.direction = right_hand_movement_direction

        self.apply_hand_movement_state_for_hand(left_hand_movement_detected,
                                                left_hand_movement_direction,
                                                hand_data_buffer, Handedness.LEFT)
        self.apply_hand_movement_state_for_hand(right_hand_movement_detected,
                                                right_hand_movement_direction,
                                                hand_data_buffer, Handedness.RIGHT)

        spread_right = self.get_hand_spread(
            hand_landmarks_right.landmark) if hand_landmarks_right else None
        spread_left = self.get_hand_spread(
            hand_landmarks_left.landmark) if hand_landmarks_left else None
        hand_data_buffer[-1].right_hand_movement_data.spread = spread_right
        hand_data_buffer[-1].left_hand_movement_data.spread = spread_left

        self.apply_mono_hand_movement_state(hand_data_buffer)

    def apply_mono_hand_movement_state(self, hand_data_buffer: List[FrameData]):
        current_left = hand_data_buffer[-1].left_hand_movement_data
        current_right = hand_data_buffer[-1].right_hand_movement_data
        previous_movement = hand_data_buffer[-2].mono_hand_movement_data

        # TODO: better name
        def did_start_scoll(spread_delta, direction: Directions):
            threshold = -SCROLL_ENABLEMENT_SPREAD_DELTA_THRESHOLD * (hand_data_buffer[-1].time - hand_data_buffer[-2].time)
            logging.debug("Spread thresh:", threshold)
            return spread_delta < threshold and direction in {
                Directions.UP, Directions.DOWN}


        if previous_movement is None or previous_movement.hand_movement_state == HandMovementState.NO_MOVEMENT:
            hand_data_buffer[-1].mono_hand_movement_data = None
            # Prioritize left hand
            if current_left.hand_movement_state != HandMovementState.NO_MOVEMENT:
                hand_data_buffer[-1].mono_hand_movement_data = current_left
            elif current_right.hand_movement_state != HandMovementState.NO_MOVEMENT:
                hand_data_buffer[-1].mono_hand_movement_data = current_right

        else:
            # TODO: Is it worth it to generalize this and make it unreadable in the process?
            previous_left = self.get_hand_landmark(hand_data_buffer[-2].results, Handedness.LEFT)
            previous_right = self.get_hand_landmark(hand_data_buffer[-2].results, Handedness.RIGHT)
            current_left = self.get_hand_landmark(hand_data_buffer[-1].results, Handedness.LEFT)
            current_right = self.get_hand_landmark(hand_data_buffer[-1].results, Handedness.RIGHT)

            # 0 is wrists' index
            previous_left_wrist = previous_left.landmark[0] if previous_left else None
            previous_right_wrist = previous_right.landmark[0] if previous_right else None
            current_left_wrist = current_left.landmark[0] if current_left else None
            current_right_wrist = current_right.landmark[0] if current_right else None

            if previous_left and current_left and self.get_euclidean_distance(previous_left_wrist,
                                                                              current_left_wrist) < HAND_TRANSFER_MAXIMUM_WRIST_DISTANCE_THRESHOLD:  # left hand moving, no transfer
                hand_data_buffer[-1].mono_hand_movement_data = hand_data_buffer[
                    -1].left_hand_movement_data
            elif previous_right and current_right and self.get_euclidean_distance(
                    previous_right_wrist,
                    current_right_wrist) < HAND_TRANSFER_MAXIMUM_WRIST_DISTANCE_THRESHOLD:  # right hand moving, no transfer
                hand_data_buffer[-1].mono_hand_movement_data = hand_data_buffer[
                    -1].right_hand_movement_data
            elif previous_left and current_right and self.get_euclidean_distance(
                    previous_left_wrist,
                    current_right_wrist) < HAND_TRANSFER_MAXIMUM_WRIST_DISTANCE_THRESHOLD:  # Left to right transfer
                hand_data_buffer[-1].mono_hand_movement_data = hand_data_buffer[
                    -1].right_hand_movement_data
            elif previous_right and current_left and self.get_euclidean_distance(
                    previous_right_wrist,
                    current_left_wrist) < HAND_TRANSFER_MAXIMUM_WRIST_DISTANCE_THRESHOLD:  # Right to left transfer
                hand_data_buffer[-1].mono_hand_movement_data = hand_data_buffer[
                    -1].left_hand_movement_data
            else:
                hand_data_buffer[-1].mono_hand_movement_data = None

        try:
            spread_delta = hand_data_buffer[-1].mono_hand_movement_data.spread - hand_data_buffer[-2].mono_hand_movement_data.spread
        except (AttributeError, TypeError): # movement data or spread None
            spread_delta = None
        logging.debug("Spread delta M: ", spread_delta, end="")
        #TODO delete print and if
        if hand_data_buffer[-1].mono_hand_movement_data is not None and hand_data_buffer[-1].mono_hand_movement_data.speed is not None and spread_delta is not None:
            if hand_data_buffer[-1].mono_hand_movement_data.speed >= SCROLL_COMMAND_SPEED_THRESHOLD and spread_delta < -SCROLL_ENABLEMENT_SPREAD_DELTA_THRESHOLD:
                print("Speed M: ",hand_data_buffer[-1].mono_hand_movement_data.speed, SCROLL_COMMAND_SPEED_THRESHOLD, end="")
                print("Delta_Spread M: ",spread_delta, SCROLL_ENABLEMENT_SPREAD_DELTA_THRESHOLD)



        if hand_data_buffer[-1].mono_hand_movement_data is not None and spread_delta is not None:
            if did_start_scoll(spread_delta, hand_data_buffer[-1].mono_hand_movement_data.direction):
                hand_data_buffer[-1].mono_hand_movement_data.hand_movement_type = HandMovementType.SCROLLING


    # TODO: Better name
    def calculcate_movement_data_for_hand_with_fallback(self, previous_landmarks, current_landmarks,
                                                        time_delta,
                                                        handedness: Handedness):
        last_valid = self.last_valid_right_hand_frame_data if handedness == Handedness.RIGHT else self.last_valid_left_hand_frame_data
        if previous_landmarks is not None and current_landmarks is not None:
            movement_detected, movement_direction, speed = self.calculate_movement_data_for_hand(
                current_landmarks, previous_landmarks, time_delta)
        elif current_landmarks is not None and last_valid is not None:
            # TODO: Refactor function call with above lines
            movement_detected, movement_direction, speed = self.calculate_movement_data_for_hand(
                current_landmarks, self.get_hand_landmark(last_valid.results, handedness),
                time_delta)
        elif last_valid is not None:
            movement_data = last_valid.get_hand_movement_data(handedness)
            speed = movement_data.speed
            movement_direction = movement_data.direction
            movement_detected = False
        else:
            speed = None
            movement_direction = None
            movement_detected = False
        return movement_detected, movement_direction, speed

    def calculate_movement_data_for_hand(self, hand_landmarks, previous_hand_landmarks, time_delta):
        current_wrist = hand_landmarks.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST]
        previous_wrist = previous_hand_landmarks.landmark[
            self.mp_wrapper.mp_hands.HandLandmark.WRIST]
        return self.calculate_movement_data(
            current_wrist, previous_wrist, time_delta)

    def apply_hand_movement_state_for_hand(self, hand_movement_detected: bool,
                                           hand_movement_direction: Directions,
                                           hand_data_buffer: List[FrameData],
                                           handedness: Handedness):
        previous_frame_data, current_frame_data = hand_data_buffer[-2], hand_data_buffer[-1]
        previous_hand_data = self.get_hand_movement_data(previous_frame_data, handedness)
        current_hand_data = self.get_hand_movement_data(current_frame_data, handedness)

        if previous_hand_data is None:
            current_hand_data.hand_movement_state = HandMovementState.NO_MOVEMENT
            current_hand_data.hand_movement_type = HandMovementType.NONE
            return

        current_hand_data.hand_movement_type = previous_hand_data.hand_movement_type
        spread_delta = current_hand_data.spread - previous_hand_data.spread if current_hand_data.spread is not None and previous_hand_data.spread is not None else None
        hand_smaller = spread_delta < SCROLL_ENABLEMENT_SPREAD_DELTA_THRESHOLD if spread_delta is not None else False
        # Current always contains valid hand data as handle_empty_current_frame_data() is called otherwise
        match previous_hand_data.hand_movement_state:
            case HandMovementState.NO_MOVEMENT:
                if hand_movement_detected:
                    current_hand_data.hand_movement_state = HandMovementState.MOVEMENT_BEGIN
                    if hand_smaller and hand_movement_direction in {Directions.UP, Directions.DOWN}:
                        current_hand_data.hand_movement_type = HandMovementType.SCROLLING
                else:
                    current_hand_data.hand_movement_state = HandMovementState.NO_MOVEMENT
            case HandMovementState.MOVEMENT_BEGIN:
                if hand_movement_detected:
                    current_hand_data.hand_movement_state = HandMovementState.IN_MOVEMENT
                    if hand_smaller:
                        current_hand_data.hand_movement_type = HandMovementType.SCROLLING
                else:
                    current_hand_data.hand_movement_state = HandMovementState.QUASI_END
            case HandMovementState.IN_MOVEMENT:
                if hand_movement_detected:
                    current_hand_data.hand_movement_state = HandMovementState.IN_MOVEMENT
                    if hand_smaller:
                        current_hand_data.hand_movement_type = HandMovementType.SCROLLING
                else:
                    current_hand_data.hand_movement_state = HandMovementState.QUASI_END
            case HandMovementState.QUASI_END:
                if hand_movement_detected:
                    current_hand_data.hand_movement_state = HandMovementState.IN_MOVEMENT
                else:
                    if all(self.get_hand_movement_data(frame_data,
                                                       handedness).hand_movement_state == HandMovementState.QUASI_END
                           for
                           frame_data in hand_data_buffer[-4:-2]):
                        current_hand_data.hand_movement_state = HandMovementState.MOVEMENT_END
                        current_hand_data.hand_movement_type = HandMovementType.NONE
                    else:
                        current_hand_data.hand_movement_state = HandMovementState.QUASI_END
            case HandMovementState.MOVEMENT_END:
                # One frame buffer before a new movement can begin
                current_hand_data.hand_movement_state = HandMovementState.NO_MOVEMENT
                current_hand_data.hand_movement_type = HandMovementType.NONE
            case state if state is None:
                current_hand_data.hand_movement_state = HandMovementState.NO_MOVEMENT
                current_hand_data.hand_movement_type = HandMovementType.NONE

    def get_hand_movement_data(self, frame_data: FrameData,
                               handedness: Handedness) -> HandMovementData:
        """Get the movement data for the hand specified by `handedness` in the given frame"""
        return frame_data.left_hand_movement_data if handedness == Handedness.LEFT else frame_data.right_hand_movement_data

    def calculate_movement_command(self, hand_data_buffer: List[FrameData]):
        current = hand_data_buffer[-1]
        if current.mono_hand_movement_data is None:
            return None
        if current.mono_hand_movement_data.hand_movement_type == HandMovementType.SCROLLING and current.mono_hand_movement_data.speed >= SCROLL_COMMAND_SPEED_THRESHOLD:
            return ScrollData(
                ScrollDirection.UP if current.mono_hand_movement_data.direction == Directions.UP else ScrollDirection.DOWN,
                current.mono_hand_movement_data.speed)
        return None

    def update(self, observable, *args, **kwargs):
        metadata: FrameMetadata = kwargs["metadata"]
        hand_data_buffer: List[FrameData] = kwargs["hand_data_buffer"]
        scroll_command: ScrollData | None = None
        frame = kwargs["frame"]
        frame_height = metadata.height
        hand_landmarks_left, hand_landmarks_right = None, None

        current_hand_data = hand_data_buffer[-1].results

        current_time = hand_data_buffer[-1].time
        time_between_frames_left = current_time - self.last_valid_left_hand_frame_data.time if self.last_valid_left_hand_frame_data is not None else None
        time_between_frames_right = current_time - self.last_valid_right_hand_frame_data.time if self.last_valid_right_hand_frame_data is not None else None

        hand_landmarks_right = self.get_hand_landmark(current_hand_data, Handedness.RIGHT)
        hand_landmarks_left = self.get_hand_landmark(current_hand_data, Handedness.LEFT)
        previous_hand_landmarks_right = self.get_hand_landmark(
            self.last_valid_right_hand_frame_data.results,
            Handedness.RIGHT) if self.last_valid_right_hand_frame_data else None
        previous_hand_landmarks_left = self.get_hand_landmark(
            self.last_valid_left_hand_frame_data.results,
            Handedness.LEFT) if self.last_valid_left_hand_frame_data else None


        right_distance_str = ""
        left_distance_str = ""

        # Initialize with default values which will be overridden (by reference) later when determining the current frame's state
        hand_data_buffer[-1].left_hand_movement_data = HandMovementData(Handedness.LEFT,
                                                                        HandMovementState.NO_MOVEMENT,
                                                                        HandMovementType.NONE, None,
                                                                        None, None)
        hand_data_buffer[-1].right_hand_movement_data = HandMovementData(Handedness.RIGHT,
                                                                         HandMovementState.NO_MOVEMENT,
                                                                         HandMovementType.NONE,
                                                                         None,
                                                                         None, None)

        self.determine_hand_movement_state(hand_data_buffer, time_between_frames_left,
                                           time_between_frames_right,
                                           hand_landmarks_right,
                                           hand_landmarks_left,
                                           previous_hand_landmarks_right,
                                           previous_hand_landmarks_left)

        if hand_landmarks_right:
            self.last_valid_right_hand_frame_data = hand_data_buffer[-1]
        if hand_landmarks_left:
            self.last_valid_left_hand_frame_data = hand_data_buffer[-1]

        movement_state_str_r = f"R: {hand_data_buffer[-1].right_hand_movement_data.hand_movement_state.name}"
        movement_state_str_l = f"L: {hand_data_buffer[-1].left_hand_movement_data.hand_movement_state.name}"
        movement_state_str_m = f"M: {hand_data_buffer[-1].mono_hand_movement_data.hand_movement_state.name if hand_data_buffer[-1].mono_hand_movement_data else None}"

        scroll_command = self.calculate_movement_command(hand_data_buffer)
        if time_between_frames_left:
            logging.debug(f"L-tbf: {time_between_frames_left:.3f}", end=" ")
        if time_between_frames_right:
            logging.debug(f"R-tbf: {time_between_frames_right:.3f}", end=" ")
        if movement_state_str_r:
            logging.debug(movement_state_str_r, end=" ")
        if movement_state_str_l:
            logging.debug(movement_state_str_l, end=" ")
        if movement_state_str_m:
            logging.debug(movement_state_str_m, end=" ")
        if right_distance_str:
            logging.debug(right_distance_str, end=" ")
        if left_distance_str:
            logging.debug(left_distance_str)

        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks_right,
                                                  self.mp_wrapper.mp_hands.HAND_CONNECTIONS)
        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks_left,
                                                  self.mp_wrapper.mp_hands.HAND_CONNECTIONS)

        send_scroll_command = False
        if scroll_command is not None:
            logging.debug(f"Sending scroll command: {scroll_command}")
            send_scroll_command = True

        self.notify_observers(scroll_command=scroll_command if send_scroll_command else None,
                              scroll_overlay=frame)
