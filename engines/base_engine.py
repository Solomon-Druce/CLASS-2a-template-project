"""Shared lifecycle every rendering engine implements, plus the run loop itself.

The loop/timing/frame-budget mechanism is identical across all three engine
tiers on purpose (Lecture 07: the render loop is the general, engine-agnostic
principle; the specific drawing API is not). `run()` is deliberately not
overridable, so subclasses can't accidentally diverge from that shared
contract while filling in engine-specific behaviour.
"""

import time
from abc import ABC, abstractmethod
from collections.abc import Callable

# Shared across all three stub engines so the "blank window" baseline looks
# the same regardless of which tier a student has chosen.
BACKGROUND_COLOR = (18, 18, 18)


class BaseEngine(ABC):
    def __init__(self, width: int, height: int, title: str, target_fps: int = 60) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.target_fps = target_fps

    @abstractmethod
    def setup(self) -> None:
        """Create the window/rendering context. Called once, before the loop starts."""

    @abstractmethod
    def handle_events(self) -> bool:
        """Poll input/window events for this frame.

        Return False to end the run loop (window close, Esc key, etc).
        """

    @abstractmethod
    def update(self, audio_features: dict, delta_time: float) -> None:
        """Advance state for this frame using the latest audio feature values."""

    @abstractmethod
    def render(self) -> None:
        """Draw the current frame."""

    @abstractmethod
    def teardown(self) -> None:
        """Release engine resources on exit (close window/context)."""

    def run(self, feature_source: Callable[[], dict]) -> None:
        """Owns the engine lifecycle: setup once, loop until handle_events()
        returns False, then teardown. Do not override this method — every
        engine tier shares this exact loop.
        """
        frame_duration = 1.0 / self.target_fps
        previous_frame = time.perf_counter()
        self.setup()
        try:
            running = True
            fps = 0.0
            fps_timer = time.perf_counter()
            frame_count = 0 #For FPS
            while running:
                frame_start = time.perf_counter()
                delta_time = frame_start - previous_frame
                previous_frame = frame_start #Added for Workshop 4
                delta_time = min(delta_time, 0.05) #Caps it to 50ms

                running = self.handle_events()
                if not running:
                    break

                audio_features = feature_source()
                self.update(audio_features, delta_time, fps) #Delta time added for workshop 4
                self.render()
                frame_count += 1 #For task.
                elapsed_fps = time.perf_counter() - fps_timer

                if elapsed_fps >= 1.0:
                    # print(f"Average FPS: {frame_count / elapsed_fps:.2f}") #Code to test it prints FPS.

                    fps = frame_count / elapsed_fps
                    frame_count = 0
                    fps_timer = time.perf_counter() #Keeps FPS counter.

                elapsed = time.perf_counter() - frame_start
                remaining = frame_duration - elapsed
                if remaining > 0:
                    time.sleep(remaining)
        finally:
            self.teardown()
