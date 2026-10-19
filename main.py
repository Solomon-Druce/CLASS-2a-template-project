"""Wires the audio pipeline and rendering engine together and runs the app.

ENGINE and AUDIO_FILE are fixed, version-controlled choices, not runtime
options — committing to one engine tier and one audio file is a project
decision, not something to toggle per run.
"""
import numpy as np
from collections.abc import Callable

from audio.pipeline import AudioPipeline
from engines.base_engine import BaseEngine
from engines.modern_gl_engine import ModernGLEngine
from engines.pygame_engine import PygameEngine
from engines.pyglet_engine import PygletEngine

# Set this to whichever engine tier your project uses. See the README for
# how/why this is a one-time project decision, not a runtime toggle.
ENGINE: type[BaseEngine] = PygletEngine

AUDIO_FILE = "audio/CGA.mp3"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "CLASS-2a Project"
TARGET_FPS = 60


def run_engine_only() -> None:
    """Runs the chosen engine with no audio pipeline involved.

    Optional helper for checking your engine in isolation — run_full_app()
    already falls back to a blank feature source until AudioPipeline is
    implemented, so you don't need this to get started.
    """
    engine = ENGINE(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, title=WINDOW_TITLE, target_fps=TARGET_FPS)
    engine.run(feature_source=lambda: {})


NOT_IMPLEMENTED_MESSAGE = "AudioPipeline not implemented yet -- running with a blank feature source."


def tolerate_not_implemented(get_features: Callable[[], dict]) -> Callable[[], dict]:
    """Wraps get_features so a NotImplementedError yields {} for that frame.

    The message is printed once, not every frame. Only NotImplementedError is
    caught — any other exception (e.g. running off the end of the audio)
    still propagates so you can see it.
    """
    warned = False

    def feature_source(chunk_size = 1024) -> dict:
        nonlocal warned
        try:
            return get_features(chunk_size)
        except NotImplementedError:
            if not warned:
                print(NOT_IMPLEMENTED_MESSAGE)
                warned = True
            return {}

    return feature_source


def run_full_app():
    engine = ENGINE(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, title=WINDOW_TITLE, target_fps=TARGET_FPS)

    pipeline = AudioPipeline(file_path=AUDIO_FILE)
    try:

        signal = pipeline.load(path=AUDIO_FILE)
        #Prints info here. Test 1
        print("number of Sr", pipeline.sample_rate) #Sample Rate (Set to 22050)
        print("Number of samples: ", signal.shape) #How many samples are in it (Total).
        print("Duration", signal.shape[0] / pipeline.sample_rate) #Duration of the audio. Total samples divided by SR
        print("Signal", signal) #Prints audio array.
        #Test 2
        start = int(149 * pipeline.sample_rate) #Selects window at 149 seconds and calcs.
        window = signal[start:start + 1024] #Takes sample from previous starting position, and goes 1024 samples before stopping
        peak = float(np.max(np.abs(window))) #Calculate Peak here
        rms = float(np.sqrt(np.mean(window ** 2))) #RMS here
        print(f"Start sample: {start}") #Prints start sample
        print(f"Peak: {peak:.6f} | RMS: {rms:.6f}") #Prints RMS and peak (both 6 figure)

        pipeline.position = 0
        num_windows = len(signal) // pipeline.window_size #Divides total sample count by 1024 + rounds down
        print(f"Complete Windows are {num_windows}")
        min_amplitude = float("inf")
        max_amplitude = float("-inf")
        min_call = 0 #Base values
        max_call = 0 #Base values
        for i in range (num_windows):
            features = pipeline.get_features() #Grabs features.
            amplitude = features["amplitude"] #Gets amplitude from get-features
            call_number = i + 1 #loops

            if amplitude < min_amplitude: #replaces min amp with new amplitude if lower
                min_amplitude = amplitude
                min_call = call_number #stores call number

            if amplitude > max_amplitude: #Replaces max amp with the new amplitude if its higher
                max_amplitude = amplitude
                max_call = call_number #Stores call number

        print(f"Minimum is {min_amplitude:.6f} (call {min_call})") #prints min
        print(f"Max is {max_amplitude:.6f} (call {max_call})") #Prints max

        pipeline.position = 0
        previous_amplitude = None
        largest_jump = 0
        jump_frame = 0

        for i in range(200): #NOTE TO SELF: CHANGE CHUNK_SIZE VALUE FOR TESTS.
            features = pipeline.get_features() #Grabs get_features from pipeline.py
            amplitude = features['amplitude'] #Gets amplitude from get-features
            print(f"frame{i + 1}: {amplitude:.6f}")#Prints the frame (+1) with the amplitude to 6 dec figures

            if previous_amplitude is not None: #Checks if amplitude exists to compare to.
                jump = abs(amplitude - previous_amplitude)# subtracts previous frame using current frame amplitue. Takes absolute (abs) value
                if jump > largest_jump: #checks current vs largest jump. If true, runs
                    largest_jump = jump
                    jump_frame = i + 1 #Records frame it happened

            previous_amplitude = amplitude
        print(f"Biggest jump: {largest_jump:.6f} at {jump_frame}") #Shows biggest jump (to 6 figs) along with specific frame jump


        # 20 loop call from previous task
        # pipeline.position = 0 #Resets position.
        # for i in range(20): #Loops 20 times.
        #     features = pipeline.get_features()
        #     print(f"Call {i + 1}: {features['amplitude']:.6f}") 

        pipeline.position = 0
        feature_source = tolerate_not_implemented(pipeline.get_features)
    except NotImplementedError:
        print(NOT_IMPLEMENTED_MESSAGE)
        feature_source = lambda: {}

    engine.run(feature_source=feature_source)


if __name__ == "__main__":
    run_full_app()
