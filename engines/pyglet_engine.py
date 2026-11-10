import pyglet
from pyglet.gl import glClearColor
from pyglet.window import key
from pyglet import shapes
import time
from engines.base_engine import BACKGROUND_COLOR, BaseEngine

_BG = tuple(c / 255 for c in BACKGROUND_COLOR) + (1.0,)

USE_DELTA_TIME = True

class PygletEngine(BaseEngine):
    def setup(self) -> None:
        self.window = pyglet.window.Window(self.width, self.height, caption=self.title)
        self._should_close = False
        glClearColor(*_BG)
        self.batch = pyglet.graphics.Batch()
        self.border_line = shapes.Line (x = 0, x2 = 1920, y= 325, y2=325, thickness = 10, color = (50, 225, 30), batch = self.batch)
        #Bars creation into a List.
        self.bars = []
        x = 300
        for i in range(5):
            bar = shapes.Rectangle (x, y = 400, 
            width = 200, height = 200, 
            color = (0, 255, 0), 
            batch = self.batch)
            self.bars.append(bar)
            x = x + 250 #Sets them a distance apart for each iteration of it until all 5 are created.
        #Audio playing (forgot earlier)
        self.audio_source = pyglet.media.load("audio/CGA.mp3", streaming = False)
        self.audio_player = pyglet.media.Player()
        self.audio_player.volume = 0.1 #Volume control.
        self.audio_player.queue(self.audio_source)
        self.audio_player.loop = True
        # self.audio_player.seek(250) #Added to ensure the song loops.
        self.audio_player.play()
        #FPS label
        self.fps_label = pyglet.text.Label("FPS is: 0.0", 
        font_size=18, x=1850, y=1050, 
        anchor_x="center", anchor_y="center")
        #Mass Labels for each one to get a better visual.
        self.amplitude_label = pyglet.text.Label("Amplitude is: 0.0", 
        font_size=18, x=400, y=300, 
        anchor_x="center", anchor_y="center")
        self.bass_label = pyglet.text.Label("??? is: 0.0",
        font_size = 18, x = 650, y = 300,
        anchor_x = "center", anchor_y = "center")
        self.trebel_label = pyglet.text.Label("??? is: 0.0",
        font_size = 18, x = 900, y = 300,
        anchor_x = "center", anchor_y = "center")
        self.centroid_label = pyglet.text.Label("??? is: 0.0",
        font_size = 18, x = 1150, y = 300,
        anchor_x = "center", anchor_y = "center")
        self.onset_label = pyglet.text.Label("??? is: 0.0",
        font_size = 18, x = 1400, y = 300,
        anchor_x = "center", anchor_y = "center")
        self.high_amp_label = pyglet.text.Label("??? is: 0.0", 
        font_size=18, x=250, y=250, 
        anchor_x="center", anchor_y="center")
        self.high_bass_label = pyglet.text.Label("??? is: 0.0", 
        font_size=18, x=250, y=200, 
        anchor_x="center", anchor_y="center")
        self.high_treble_label = pyglet.text.Label("??? is: 0.0", 
        font_size=18, x=250, y=150, 
        anchor_x="center", anchor_y="center")
        self.high_centroid_label = pyglet.text.Label("??? is: 0.0", 
        font_size=18, x=250, y=100, 
        anchor_x="center", anchor_y="center")
        self.high_onset_label = pyglet.text.Label("??? is: 0.0", 
        font_size=18, x=250, y=50, 
        anchor_x="center", anchor_y="center")

        @self.window.event
        def on_close():
            self._should_close = True
            return pyglet.event.EVENT_HANDLED

        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.ESCAPE:
                self._should_close = True
                return pyglet.event.EVENT_HANDLED

    def handle_events(self) -> bool:
        pyglet.clock.tick()
        pyglet.app.platform_event_loop.dispatch_posted_events()
        # BaseEngine.run() owns the loop, so events are dispatched manually
        # here each frame rather than handing control to pyglet.app.run().
        self.window.dispatch_events()
        return not self._should_close

    #New function for audio features?
    #Playback time equal to audio_player time
    #gets info from get_features(playback time) to keep them in sync?

    def update(self, audio_features: dict, delta_time: float, fps) -> None:
        amplitude = audio_features["amplitude"]
        bass = audio_features["Bass"]
        treble = audio_features["treble energy"]
        centroid = audio_features["centroid"]
        onset = audio_features["onset"]
        amplitude_high = audio_features["amplitude_high"]
        bass_high = audio_features["bass_high"]
        treble_high = audio_features["treble_high"]
        centroid_high = audio_features["centroid_high"]
        onset_high = audio_features["onset_high"]
        #Normalisation for energy stuff
        amp_normal = min(amplitude / amplitude_high, 1.0) if amplitude_high > 0 else 0
        bass_normal = min(bass / bass_high, 1.0) if bass_high > 0 else 0
        treble_normal = min(treble / treble_high, 1.0) if treble_high > 0 else 0
        centroid_normal = min(centroid / centroid_high, 1.0) if centroid_high > 0 else 0
        onset_normal = min(onset / onset_high, 1.0) if onset_high > 0 else 0
        #Labels part 2
        self.amplitude_label.text = f"Amplitude is {amp_normal:.2f}"#Takes info from audio_features(specifically amplitude to 6 figures) and displays it.
        self.fps_label.text = f"FPS is {fps:.1f}"
        self.bass_label.text = f"Bass is {bass_normal:.2f}"
        self.trebel_label.text = f"Treble is {treble_normal:.2f}"
        self.centroid_label.text = f"Centroid is {centroid_normal:.2f}"
        self.onset_label.text = f"Onset is {onset_normal:.2f}"
        self.high_amp_label.text = f"Highest recorded amplitude is {audio_features["amplitude_high"]:.6f}"
        self.high_bass_label.text = f"Highest recorded Bass is {audio_features["bass_high"]:.6f}"
        self.high_treble_label.text = f"Highest recorded Treble is {audio_features["treble_high"]:.6f}"
        self.high_centroid_label.text = f"Highest recorded Centroid is {audio_features["centroid_high"]:.6f}"
        self.high_onset_label.text = f"Highest recorded Onset is {audio_features["onset_high"]:.6f}"
        #Amplitude changing colour of bar.
        self.bars[0].height = amp_normal * 400  # Scale the bar height based on amplitude
        self.bars[1].height = bass_normal * 400
        self.bars[2].height = treble_normal * 400
        self.bars[3].height = centroid_normal * 400 
        self.bars[4].height = onset_normal * 400
        #Colour determination v2
        amp_green = int(255 * amp_normal)
        bass_green = int(255 * bass_normal)
        treble_green = int(255 * treble_normal)
        centroid_green = int(255 * centroid_normal)
        onset_green = int(255 * onset_normal)
        #Determines colors for the bars based upon energy
        self.bars[0].color = (50, amp_green, 50)
        self.bars[1].color = (50, bass_green, 50)
        self.bars[2].color = (50, treble_green, 50)
        self.bars[3].color = (50, centroid_green, 50)
        self.bars[4].color = (50, onset_green, 50)
        # self.bars[1].color = (0, 0, blue)
            
        # print(f"delta time is {delta_time} seconds") #Used to check it was getting an actual output.
         
    def render(self) -> None:
        self.window.clear()
        # time.sleep(0.03) #Added due to task. Will be removed later.
        self.amplitude_label.draw()
        self.fps_label.draw()
        self.bass_label.draw()
        self.trebel_label.draw()
        self.centroid_label.draw()
        self.onset_label.draw()
        self.high_amp_label.draw()
        self.high_bass_label.draw()
        self.high_centroid_label.draw()
        self.high_onset_label.draw()
        self.high_treble_label.draw()
        self.batch.draw()
        self.window.flip()

    def teardown(self) -> None:
        self.audio_player.pause()
        self.audio_player.delete()
        self.window.close()
