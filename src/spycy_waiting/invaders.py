from cursedspace import Panel

from . import shapes
from .config import color



class SpaceInvaders(Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = shapes.Player(None, 'player')
        self.invaders = [
            shapes.Invader(None, 'enemy')
            for j in range(3)
        ]
        self.shots = []
        self.next_move = 0
        self.shot = False

    def handle_input(self, key):
        if key == "<left>":
            self.next_move = -1
        elif key == "<right>":
            self.next_move = 1
        elif key == "<down>":
            self.next_move = 0
        elif key == "<up>":
            self.shot = True

    def update_state(self):
        y, x, h, w = self.content_area()
        p = self.player
        
        pop_inds = []
        for si, s in enumerate(self.shots):
            s[0] -= 1
            if s[0] < y:
                pop_inds.append(si)
        for si in pop_inds[::-1]:
            self.shots.pop(si)


        if self.shot:
            self.shots.append([
                h - 4,
                p.pos[1] + p.SIZE[1]//2 + 1,
            ])
            self.shot = False

        p.pos[1] += self.next_move
        self.next_move = 0

        for inv in self.invaders:
            if inv.pos[1] + inv.direction > w - inv.SIZE[1]:
                inv.direction = -1
            elif inv.pos[1] + inv.direction < 0:
                inv.direction = 1
            
            inv.pos[1] += inv.direction


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
            self.win.addstr(s[0], s[1], '↑', color('shot'))

        self.player.draw(self.win, x, y, h, w)
        self.win.noutrefresh()
