import argparse
import subprocess
import threading
import shlex
import curses
import cursedspace
from cursedspace import Application, Key, Panel, colors, Grid, ProgressBar

# refresh time in ms
UPDATE_RATE = 300

COLOR_MAPPING = {
    'text': (1, 0), 
    'title': (2, 0),
    'player': (2, 0),
    'enemy': (3, 0),
    'terrain': (4, 0),
}
COLORS = {key: colors.ColorPair(*x) for key, x in COLOR_MAPPING.items()}


#SHAPES = {
#    'invader':'''
# ██
#█  █
#''',
#'player':'''
#  █
#█████
#'''
#}


def color(key):
    return colors.attr(COLORS[key])


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
        super().paint(clear=True)

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


class Invaders(Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paint(self, clear=False):
        super().paint(clear)
        self.win.addstr(1, 1, "HELLO")
        self.win.noutrefresh()


class Game(Application):
    def __init__(self, cmd):
        super().__init__()
        self.grid = Grid(self, rows=1, cols=2)

        self.grid.add_panel(
            0, 0, 
            key='game', 
            panel_class=Invaders,
        )
        self.grid.add_panel(
            0, 1, 
            key='proc', 
            panel_class=Process,
            args=(cmd, ),
        )

        for panel in self.grid.panels:
            panel.border = cursedspace.Panel.BORDER_ALL

    def draw(self):
        self.grid.paint()
        curses.doupdate()

    def main(self):
        self.resize()
        self.screen.timeout(UPDATE_RATE)
        self.show_cursor(False)

        while True:
            self.draw()
            
            key = self.read_key()

            if key == Key.RESIZE:
                self.resize()
            elif key in [Key.ESCAPE, "q", "^C"]:
                break

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
