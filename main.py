"""Wires the audio pipeline and rendering engine together and runs the app.

ENGINE and AUDIO_FILE are fixed, version-controlled choices, not runtime
options — committing to one engine tier and one audio file is a project
decision, not something to toggle per run.
"""
import numpy as np
from collections.abc import Callable
import librosa

from audio.pipeline import AudioPipeline
from engines.base_engine import BaseEngine
from engines.modern_gl_engine import ModernGLEngine
from engines.pygame_engine import PygameEngine
from engines.pyglet_engine import PygletEngine

# Set this to whichever engine tier your project uses. See the README for
# how/why this is a one-time project decision, not a runtime toggle.
ENGINE: type[BaseEngine] = PygletEngine

AUDIO_FILE = "audio/CGA.mp3"
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
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
  # Test that get_features() is implemented, not just load()
        signal = pipeline.load(path=AUDIO_FILE)
        #Prints info here. Test 1
        # print("number of Sr", pipeline.sample_rate) #Sample Rate (Set to 22050)
        # print("Number of samples: ", signal.shape) #How many samples are in it (Total).
        # print("Duration", signal.shape[0] / pipeline.sample_rate) #Duration of the audio. Total samples divided by SR
        # print("Signal", signal) #Prints audio array.
        #Test 2
        # start = int(30 * pipeline.sample_rate) #Selects window at 149 seconds and calcs.
        # window = signal[start:start + 1024] #Takes sample from previous starting position, and goes 1024 samples before stopping
        # peak = float(np.max(np.abs(window))) #Calculate Peak here
        # rms = float(np.sqrt(np.mean(window ** 2))) #RMS here
        # print(f"Start sample: {start}") #Prints start sample
        # print(f"Peak: {peak:.6f} | RMS: {rms:.6f}") #Prints RMS and peak (both 6 figure)

        # pipeline.position = 0
        # num_windows = len(signal) // pipeline.window_size #Divides total sample count by 1024 + rounds down
        # print(f"Complete Windows are {num_windows}")
        # min_amplitude = float("inf")
        # max_amplitude = float("-inf")
        # min_call = 0 #Base values
        # max_call = 0 #Base values
        # for i in range (num_windows):
        #     features = pipeline.get_features() #Grabs features.
        #     amplitude = features["amplitude"] #Gets amplitude from get-features
        #     call_number = i + 1 #loops

        #     if amplitude < min_amplitude: #replaces min amp with new amplitude if lower
        #         min_amplitude = amplitude
        #         min_call = call_number #stores call number

        #     if amplitude > max_amplitude: #Replaces max amp with the new amplitude if its higher
        #         max_amplitude = amplitude
        #         max_call = call_number #Stores call number

        # print(f"Minimum is {min_amplitude:.6f} (call {min_call})") #prints min
        # print(f"Max is {max_amplitude:.6f} (call {max_call})") #Prints max

        # pipeline.position = 0
        # previous_amplitude = None
        # largest_jump = 0
        # jump_frame = 0

        # for i in range(2): #NOTE TO SELF: CHANGE CHUNK_SIZE VALUE FOR TESTS.
        #     features = pipeline.get_features() #Grabs get_features from pipeline.py
        #     amplitude = features['amplitude'] #Gets amplitude from get-features
        #     print(f"frame{i + 1}: {amplitude:.6f}")#Prints the frame (+1) with the amplitude to 6 dec figures

        #     if previous_amplitude is not None: #Checks if amplitude exists to compare to.
        #         jump = abs(amplitude - previous_amplitude)# subtracts previous frame using current frame amplitue. Takes absolute (abs) value
        #         if jump > largest_jump: #checks current vs largest jump. If true, runs
        #             largest_jump = jump
        #             jump_frame = i + 1 #Records frame it happened

        #     previous_amplitude = amplitude
        # print(f"Biggest jump: {largest_jump:.6f} at {jump_frame}") #Shows biggest jump (to 6 figs) along with specific frame jump
        
        #workshop 3, part 1 +2
        start = int(30 * pipeline.sample_rate)
        window = signal[start:start + 1024]
        result = np.fft.rfft(window * np.hanning(1024))
        magnitude = np.abs(result) #Takes portions starting at 30 secs, uses fft to discover strongest frequency
        bin_1_frequency = 1* pipeline.sample_rate / 1024 # 1st bin freqncy
        last_bin = len(magnitude) - 1 
        last_bin = last_bin * pipeline.sample_rate / 1024 #last bin frequency
        strongest_bin = np.argmax(magnitude[1:513]) + 1
        strongest_mag = magnitude[strongest_bin]
        frequency = strongest_bin * pipeline.sample_rate / 1024

        print(f"Bin count: {len(magnitude)}")#513
        print(f"1st bin Frequncy is {bin_1_frequency}hz")#21.5332 hz
        print(f"last bin frequency is {last_bin:.6f}hz") ##11025hz
        print(f"strongest bin {strongest_bin}")
        print(f"strongest_frequency {frequency:.6f}hz")
        print(f"strongest magnitude {strongest_mag:.6f}")

        pipeline.position = 0
        for i in range(50):
            features = pipeline.get_features()

            if (i + 1) % 10 == 0:
                print(i + 1, features)

        #workshop 3, prt3
        pipeline.position = 0
        pipeline.previous_magnitude = np.zeros(pipeline.window_size // 2 + 1)
        onsets = []
        num_windows = len(signal) // pipeline.window_size

        for i in range(num_windows):
            position = pipeline.position
            features = pipeline.get_features()
            time = position / pipeline.sample_rate
            onsets.append((features["onset"], time))

        onsets.sort(reverse=True)

        selected = []
        for strong, time in onsets:
            if all(abs(time - existing_time) >= 0.5
                   for _, existing_time in selected):
                selected.append((strong, time))

            if len(selected) == 5:
                break

        for strength, time in selected:
            print(f"Onset is {strength:.6f}, Time is {time:.6f} (seconds)")

        detected_onsets = librosa.onset.onset_detect(y=signal, sr=pipeline.sample_rate, units="time")
        print("librosa onset time is", detected_onsets)

        #task 15 (workshop 3, part 3)

        pipeline.position = 0
        chunk = signal[:pipeline.window_size] # Takes 1024 samples from audio beginning. Saves as "Chunk"
        window = np.hanning(pipeline.window_size) #Hanning is 1024, not hardcoded this time.
        windowed_chunk = chunk * window #Chunk x Window grants windowed chunk
        sample_energy = np.sum(windowed_chunk ** 2) #Gets sample energy
        magnitude = abs(np.fft.rfft(chunk * window))
        bass_edge = int(250 * pipeline.window_size / pipeline.sample_rate)
        treble_edge = int(2000 * pipeline.window_size / pipeline.sample_rate)

        #Total energy | Should be adding up bass/treble/middle group?
        # presumably its something along the lines of [:bassedge] for lower, [bassedge:treble] for mid and [trebleedge:] for high? with magnitude([]) ** 2 for each one?
        # Total is low + mid + high = high?
        low_energy = np.sum(magnitude[:bass_edge] ** 2)
        mid_energy = np.sum(magnitude[bass_edge:treble_edge] ** 2)
        high_energy = np.sum(magnitude[treble_edge:] ** 2)
        total_energy = low_energy + mid_energy + high_energy

        print(f"Total energy is {total_energy:.12e}")
        #Print the difference

        #Change this to a function?
        #Feature_source()? then get it to return audio_player.time?
        #Keep the except for now(?)
        pipeline.position = 0
        feature_source = tolerate_not_implemented(pipeline.get_features)
    except NotImplementedError:
        print(NOT_IMPLEMENTED_MESSAGE)
        feature_source = lambda: {}

    engine.run(feature_source=feature_source)


if __name__ == "__main__":
    run_full_app()
