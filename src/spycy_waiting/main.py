import argparse
import subprocess
import threading
import shlex
import random
import time
import curses
import cursedspace
from cursedspace import Application, Key, Panel, Grid, ProgressBar

from .config import color, UPDATE_RATE
from . import shapes

def read_pipe(proc, output):
    for line in iter(proc.stdout.readline, b''):
        if len(line) > 0:
            output.append(line)


class Process(Panel):
    def __init__(self, app, cmd, **kwargs):
        super().__init__(app, **kwargs)
        self.cmd = cmd
        self.process = None
        self.reader = None

    def init(self):
        self.process = subprocess.Popen(
            self.cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            shell=True,
        )
        self.content = []

        self.reader = threading.Thread(
            target=read_pipe, 
            args=(self.process, self.content),
        )
        self.reader.start()


    def paint(self, **kwargs):
        super().paint(clear=False)

        if self.process is None:
            self.init()

        title_attr = curses.A_BOLD | curses.A_UNDERLINE | color('title')

        y, x, h, w = self.content_area()
        if self.reader.is_alive():
            status = 'Process: Running...'
        else:
            status = 'Process: Finished'
        status = status.center(w, ' ')
        self.win.addstr(y, x, status[:w], title_attr)
        h -= 1
        y += 1

        if len(self.content) > h:
            num = h
            for j in range(len(self.content) - h):
                self.content.pop(0)
        else:
            num = len(self.content)

        for j in range(num):
            s = self.content[j].strip()
            self.win.addstr(y + j, x, s[:w])
        self.win.noutrefresh()


class FightInvaders(Panel):
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


class Game(Application):
    def __init__(self, cmd):
        super().__init__()
        self.grid = Grid(self, rows=1, cols=2)

        self.grid.add_panel(
            0, 0, 
            key='game', 
            panel_class=FightInvaders,
        )
        self.grid.add_panel(
            0, 1, 
            key='proc', 
            panel_class=Process,
            args=(cmd, ),
        )
        self.next_move = 0
        self.shot = False

        for panel in self.grid.panels:
            panel.border = cursedspace.Panel.BORDER_ALL

    def draw(self):
        self.grid.paint()
        curses.doupdate()

    def update_state(self):
        y, x, h, w = self.grid['game'].content_area()
        p = self.grid['game'].player
        
        pop_inds = []
        for si, s in enumerate(self.grid['game'].shots):
            s[0] -= 1
            if s[0] < y:
                pop_inds.append(si)
        for si in pop_inds[::-1]:
            self.grid['game'].shots.pop(si)


        if self.shot:
            self.grid['game'].shots.append([
                h - 4,
                p.pos[1] + p.SIZE[1]//2 + 1,
            ])
            self.shot = False

        p.pos[1] += self.next_move
        self.next_move = 0

        for inv in self.grid['game'].invaders:
            if inv.pos[1] + inv.direction > w - inv.SIZE[1]:
                inv.direction = -1
            elif inv.pos[1] + inv.direction < 0:
                inv.direction = 1
            
            inv.pos[1] += inv.direction


    def main(self):
        self.resize()
        self.screen.timeout(int(UPDATE_RATE*1e3))
        self.show_cursor(False)

        self.grid['game'].setup()
        t0 = time.monotonic()

        while True:
            self.draw()
            
            key = self.read_key()

            if key == Key.RESIZE:
                self.resize()
            elif key == "<left>":
                self.next_move = -1
            elif key == "<right>":
                self.next_move = 1
            elif key == "<down>":
                self.next_move = 0
            elif key == "<up>":
                self.shot = True
            elif key in [Key.ESCAPE, "q", "^C"]:
                break

            t1 = time.monotonic()
            dt = t1 - t0
            if dt > UPDATE_RATE:
                t0 = t1
                self.update_state()
            else:
                time.sleep((UPDATE_RATE - dt)*0.5)
                

    def resize(self):
        height, width = self.size()
        self.grid.resize(height, width)


def run():

    parser = argparse.ArgumentParser(description='Fight off the invaders!')
    parser.add_argument('-q', '--auto-quit', action='store_true', help='X')
    parser.add_argument('--test', default=1.0, type=float, help='X')
    parser.add_argument('cmd', type=str, help='The command to execute while blastin')

    args = parser.parse_args()

    cmd = shlex.split(args.cmd)

    invasion = Game(
        cmd = cmd,
    )

    invasion.run()

    c = invasion.grid['proc'].content
    while invasion.grid['proc'].reader.is_alive():
        while len(c) > 0:
            print(c.pop(0).decode().strip())
    while len(c) > 0:
        print(c.pop(0).decode().strip())
    
    if invasion.grid['proc'].reader is not None:
        invasion.grid['proc'].reader.join()