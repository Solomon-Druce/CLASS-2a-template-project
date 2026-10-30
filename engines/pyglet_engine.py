import time
import pyglet
from pyglet.gl import glClearColor
from pyglet.window import key
from pyglet import shapes
from pyglet import clock

from engines.base_engine import BACKGROUND_COLOR, BaseEngine


_BG = tuple(c / 255 for c in BACKGROUND_COLOR) + (1.0,)


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
            bar = shapes.Rectangle (x, y = 400, width = 100, height = 300, color = (0, 255, 0), batch = self.batch)
            self.bars.append(bar)
            x = x + 120
        #Audio playing (forgot earlier)
        self.audio_source = pyglet.media.load("audio/CGA.mp3", streaming = False)
        self.audio_player = pyglet.media.Player()
        self.audio_player.volume = 0.1 #Volume control.
        self.audio_player.queue(self.audio_source)
        self.audio_player.play()
        #Time since last frame

        @self.window.event
        def on_close():
            self._should_close = True
            return pyglet.event.EVENT_HANDLED

        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.ESCAPE:
                self._should_close = True
                return pyglet.event.EVENT_HANDLED

    # def run(self) -> None:
    #     self.setup()
    #     while self.running:
    #         delta_time = self.clock.tick()
    #         self.handle_input()
    #         self.update(delta_time)
    #         self.render()
    #     self.teardown()

    def handle_events(self) -> bool:
        # BaseEngine.run() owns the loop, so events are dispatched manually
        # here each frame rather than handing control to pyglet.app.run().
        self.window.dispatch_events()
        return not self._should_close

    #New function for audio features?
    #Playback time equal to audio_player time
    #gets info from get_features(playback time) to keep them in sync?

    def update(self, audio_features: dict) -> None:
        self.amplitude_label.text = f"Amplitude is  {audio_features["amplitude"]:.6f}"#Takes info from audio_features(specifically amplitude to 6 figures) and displays it.
        for i in range(len(self.bars)):
            self.bars[i].height = audio_features["amplitude"] * 500  # Scale the bar height based on amplitude
        # delta_time = clock.schedule_interval(1)  # Get the time since the last frame
        # self.handle_events()
        # self.update(delta_time)
        # self.render()
        # print(f"Delta time: {delta_time:.6f} seconds")  # Print the delta time for each frame

    def render(self) -> None:
        self.window.clear()
        time.sleep(0.03)
        self.amplitude_label.draw()
        self.batch.draw()
        self.window.flip()

    def teardown(self) -> None:
        self.audio_player.pause()
        self.audio_player.delete()
        self.window.close()
