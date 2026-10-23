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
        self.position = 0
        self.window_size = 1024

    def load(self, path: str, sr: int = 22050) -> None:
        signal, _ = librosa.load(path, sr=sr)
        self.signal = signal
        self.sample_rate = sr
        return self.signal
        """Load the audio file at self.file_path via librosa, at
        self.sample_rate, and store the resulting signal on the instance.
        """
        #raise NotImplementedError

    def get_features(self, chunk_size: int = 1024) -> dict: #Chunk+size = samples to be read.
        #Amplitude
        if self.position + chunk_size > len(self.signal): #Where the next section starts. Len(self.,sginal) is total samples
            self.position = 0
        chunk = self.signal[self.position:self.position + chunk_size] #Takes the audio window in a slice. Ends before chunk_size added to selfposition
        amplitude = float(np.sqrt(np.mean(chunk ** 2))) #Calcs Root mean square (rms)
        self.position += chunk_size #Advances to the next set.
        #Hanning
        window = np.hanning(1024)
        bin = np.fft.rfft(chunk_size * window)
        np.fft.rfft(chunk_size * np.hanning(1024))
        #print(self.position, len(self.signal)) #Temp for task
        return {"amplitude": amplitude,
                "Bins": bin
                }

        #chunk = self.signal[self.position:self.position + self.window_size]
        #amplitude = float(np.sqrt(np.mean(chunk ** 2))) #Amplitude version

        #print(self.position, len(self.signal)) #Temp for task

        #self.position += self.window_size
        # amplitude = float(np.abs(chunk).mean()) #Mean
        """Extract numerical features (amplitude at minimum) from the current
        window of the loaded signal, advance the pipeline's internal read
        position accordingly, and return them as a dict[str, float].

        This return value is passed directly into engine.update().
        """
