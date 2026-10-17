import librosa
import numpy as np

class AudioPipeline:

    """Loads an audio file and extracts features from it, frame by frame.

    Both load() and get_features() are stubs you must implement yourself —
    that's intentional, not an oversight. This unit is about the whole
    pipeline (data source -> feature extraction -> real-time rendering), not
    just feature extraction handed to you pre-solved.
    """

    def __init__(self, file_path: str, sample_rate: int = 22050) -> None:
        self.file_path = file_path
        self.sample_rate = sample_rate

    def load(self, path: str, sr: int = 22050) -> None:
        signal, _ = librosa.load(path, sr=sr)
        self.signal = signal
        self.sample_rate = sr
        return self.signal
        """Load the audio file at self.file_path via librosa, at
        self.sample_rate, and store the resulting signal on the instance.
        """
        #raise NotImplementedError

    def get_features(self, chunk_size: int = 1024) -> dict:
        middle = len(self.signal) // 2 #Gives total number of samples. Dividing by 2 lets me use midpoint.
        start = middle - chunk_size // 2 #Start is at 512 samples
        window = self.signal[start:start + chunk_size] #Slicing. Samples up to start.
        peak = float(np.max(np.abs(window))) #abs handles negative samples.
        rms = float(np.sqrt(np.mean( window ** 2)))
        return{"peak": peak, "rms": rms}
        # for start in range(0, len(self.signal), chunk_size):
        #     amplitude = float(np.abs(chunk_size).mean())
        #     return amplitude
        """Extract numerical features (amplitude at minimum) from the current
        window of the loaded signal, advance the pipeline's internal read
        position accordingly, and return them as a dict[str, float].

        This return value is passed directly into engine.update().
        """
        raise NotImplementedError
