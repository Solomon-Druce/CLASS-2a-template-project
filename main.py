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

    def feature_source() -> dict: #chunk_size = 1024 inside feature_source.
        nonlocal warned
        try:
            return get_features() #chunk_size inside.
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

        #print(f"Total energy is {total_energy:.12e}") Added for task, probably deleted later.

        pipeline.position = 0
        feature_source = tolerate_not_implemented(
            lambda: pipeline.get_features(engine.audio_player.time)
        ) #Lambda used to delay call until feature_source called.
    except NotImplementedError:
        print(NOT_IMPLEMENTED_MESSAGE)
        feature_source = lambda: {}

    engine.run(feature_source=feature_source)


if __name__ == "__main__":
    run_full_app()
