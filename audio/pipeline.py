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
        self.previous_magnitude = np.zeros(self.window_size // 2 + 1) #Array of 513 zeros
        #Setting for normalisation
        self.amp_high = 0
        self.mid_high = 0
        self.bass_high = 0
        self.treble_high = 0
        self.centroid_high = 0
        self.onset_high = 0


    def load(self, path: str, sr: int = 22050) -> None:
        signal, _ = librosa.load(path, sr=sr)
        self.signal = signal
        self.sample_rate = sr
        return self.signal
        """Load the audio file at self.file_path via librosa, at
        self.sample_rate, and store the resulting signal on the instance.
        """
        #raise NotImplementedError

    def get_features(self, playback_time: float, chunk_size: int = 1024) -> dict: #Chunk+size = samples to be read.
        #Ideas:
        #Add playback_time: float to get_features to keep track of that?
        #make self position based on playback time multiplied by sample_rate?
        #Keep the loop directly below "amplitude" (Make it look nicer tho)
        
        #Amplitude
        self.position = int(playback_time * self.sample_rate)
        if self.position + chunk_size > len(self.signal):
            self.position = 0

        chunk = self.signal[self.position:self.position + chunk_size]
        amplitude = float(np.sqrt(np.mean(chunk ** 2)))

        #Noramlisation

        #Workshop 3, task1+2
        window = np.hanning(chunk_size)
        spectrum = np.fft.rfft(chunk * window)
        magnitude = np.abs(spectrum)
        bass_edge = int(250 * chunk_size / self.sample_rate)
        treble_edge = int(2000 * chunk_size / self.sample_rate)
        bass_energy = np.sum(magnitude[:bass_edge] ** 2)
        mid_energy = np.sum(magnitude[bass_edge:treble_edge] ** 2)
        treble_energy = np.sum(magnitude[treble_edge:] ** 2)
        frequencies = np.fft.rfftfreq(chunk_size, d=1 / self.sample_rate)
        centroid = np.sum(frequencies * magnitude) / np.sum(magnitude)
        #Task 3, part 3
        onset = np.sum(np.maximum(0, magnitude - self.previous_magnitude))
        self.previous_magnitude = magnitude.copy()

        #Calculate the high
        self.amp_high = max(self.amp_high, amplitude)
        self.bass_high = max(self.bass_high, bass_energy)
        self.mid_high = max(self.mid_high, mid_energy)
        self.treble_high = max(self.treble_high, treble_energy)
        self.centroid_high = max(self.centroid_high, centroid)
        self.onset_high = max(self.onset_high, onset)

        print(self.amp_high, self.bass_high, self.mid_high, self.treble_high,self.centroid_high, self.onset_high)
        #print(self.position, len(self.signal)) #Temp for task
        return {"amplitude": amplitude,
                "Bass": float(bass_energy),
                "mid energy": float(mid_energy),
                "treble energy": float(treble_energy),
                "centroid": float(centroid),
                "onset": float(onset),

                #Returns maximums for later.
                "amplitude_high": self.amp_high,
                "bass_high": self.bass_high,
                "mid_high": self.mid_high,
                "treble_high": self.treble_high,
                "centroid_high": self.centroid_high,
                "onset_high": self.onset_high
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
