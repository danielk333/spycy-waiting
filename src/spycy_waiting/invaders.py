from . import shapes
from cursedspace import Panel


class SpaceInvaders(Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = shapes.Player(None, 'player')
        self.invaders = [
            shapes.Invader(None, 'enemy')
            for j in range(3)
        ]
        self.shots = []


    def setup(self):
        inv_num = len(self.invaders)
        y, x, h, w = self.content_area()

        for i, inv in enumerate(self.invaders):
            inv.pos = [3, x + i*w//inv_num]
        self.player.pos = [h - 2, (w + self.player.SIZE[1])//2]


    def paint(self, **kwargs):
        super().paint(clear=True)
        
        y, x, h, w = self.content_area()

        for inv in self.invaders:
            inv.draw(self.win, x, y, h, w)

        for s in self.shots:
            self.win.addstr(s[0], s[1], shapes.Shot, color('shot'))

        self.player.draw(self.win, x, y, h, w)
        self.win.noutrefresh()
