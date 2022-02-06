import random
import pkg_resources

from cursedspace import Panel

from . import shapes
from .config import color

class Wordle(Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with pkg_resources.resource_stream('spycy_waiting.data', 'wordle_words.txt') as fh:
            self.words = [line.strip() for line in fh]
        self.target_word = None

    def handle_input(self, key):
        if key.value.isalpha():
            pass
        elif key == "<enter>":
            pass

    def update_state(self):
        pass

    def setup(self):
        pass

    def paint(self, **kwargs):
        super().paint(clear=True)
        pass
