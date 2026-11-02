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
        #Amplitude Label
        self.amplitude_label = pyglet.text.Label("Amplitude is: 0.0", 
        font_size=18, x=150, y=300, 
        anchor_x="center", anchor_y="center"
        ) #Places the text at x=400, y=300 and displays 0.0 if nothing is working currently
        #Border(?)
        self.batch = pyglet.graphics.Batch()
        self.border_line = shapes.Line (x = 0, x2 = 1920, y= 325, y2=325, thickness = 10, color = (50, 225, 30), batch = self.batch)
        #Bars (WIP) Intent is to have user select how many bars they want (How?)
        self.bars = []
        x = 200
        for i in range(5):
            bar = shapes.Rectangle (x, y = 400, width = 100, height = 200, color = (0, 255, 0), batch = self.batch)
            self.bars.append(bar)
            x = x + 120
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
        font_size=18, x=150, y=250, 
        anchor_x="center", anchor_y="center"
        )


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
        self.amplitude_label.text = f"Amplitude is  {audio_features["amplitude"]:.6f}"#Takes info from audio_features(specifically amplitude to 6 figures) and displays it.
        self.fps_label.text = f"FPS is {fps:.1f}"
        #Amplitude changing colour of bar.
        amplitude = audio_features["amplitude"]
        red = int(255 * amplitude)
        for i in range(len(self.bars)):
            self.bars[i].height = amplitude * 500  # Scale the bar height based on amplitude
            self.bars[i].color = (red, 0, 0) #Temp black for start.
        # print(f"delta time is {delta_time} seconds") #Used to check it was getting an actual output.
         
    def render(self) -> None:
        self.window.clear()
        # time.sleep(0.03) #Added due to
        self.amplitude_label.draw()
        self.fps_label.draw()
        self.batch.draw()
        self.window.flip()

    def teardown(self) -> None:
        self.audio_player.pause()
        self.audio_player.delete()
        self.window.close()
