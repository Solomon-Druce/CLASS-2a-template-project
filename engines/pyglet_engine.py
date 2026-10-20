import pyglet
from pyglet.gl import glClearColor
from pyglet.window import key
from pyglet import shapes

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
        # BaseEngine.run() owns the loop, so events are dispatched manually
        # here each frame rather than handing control to pyglet.app.run().
        self.window.dispatch_events()
        return not self._should_close

    def update(self, audio_features: dict) -> None:
        self.amplitude_label.text = f"Amplitude is  {audio_features["amplitude"]:.6f}"#Takes info from audio_features(specifically amplitude to 6 figures) and displays it.

    def render(self) -> None:
        self.window.clear()
        self.amplitude_label.draw()
        self.batch.draw()
        self.window.flip()

    def teardown(self) -> None:
        self.window.close()
