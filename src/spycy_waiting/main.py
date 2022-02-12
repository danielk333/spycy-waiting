import argparse
import subprocess
import threading
import shlex
import time
import sys
import curses
import cursedspace
import tempfile
from collections import OrderedDict

from cursedspace import Application, Key, Panel, Grid

from .config import color
from .crusaders import Crusaders
from .wordle import Wordle

GAMES = OrderedDict(
    crusaders = Crusaders,
    wordle = Wordle,
)


def read_pipe(proc, output, cache_file):
    for line in iter(proc.stdout.readline, b''):
        if len(line) > 0:
            output.append(line)
            cache_file.write(line)


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

        self.cache_file = tempfile.TemporaryFile()

        self.reader = threading.Thread(
            target=read_pipe, 
            args=(
                self.process, 
                self.content,
                self.cache_file,
            ),
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
            if self.app.auto_quit:
                self.app.quit_now = True
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


class Game(Application):
    def __init__(self, cmd, game, auto_quit, refresh_rate):
        super().__init__()
        self.auto_quit = auto_quit
        self.refresh_rate = refresh_rate
        self.quit_now = False
        self.grid = Grid(self, rows=1, cols=2)

        self.grid.add_panel(
            0, 0, 
            key='game', 
            panel_class=GAMES[game],
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
        self.screen.timeout(int(self.refresh_rate*1e3))
        self.show_cursor(False)

        self.grid['game'].setup()
        t0 = time.monotonic()

        while True:
            self.draw()
            
            key = self.read_key()

            if key == Key.RESIZE:
                self.resize()
            elif key in [Key.ESCAPE, "q", "^C"]:
                break

            if self.quit_now:
                break

            self.grid['game'].handle_input(key)

            t1 = time.monotonic()
            dt = t1 - t0
            if dt > self.refresh_rate:
                t0 = t1
                self.grid['game'].update_state()
            else:
                time.sleep((self.refresh_rate - dt)*0.5)
                
    def resize(self):
        height, width = self.size()
        self.grid.resize(height, width)


def run():

    GAME_LIST = list(GAMES.keys())

    parser = argparse.ArgumentParser(description='Wait excitingly!')
    parser.add_argument(
        '-q', '--auto-quit', 
        action='store_true', 
        help='Quit game automatically when process finishes',
    )
    parser.add_argument(
        '-r', '--refresh-rate', 
        default=0.3, 
        choices=GAME_LIST, help='Time in seconds between game refreshes',
    )
    parser.add_argument(
        '-g', '--game', 
        default=GAME_LIST[0], 
        choices=GAME_LIST, help='Game to play',
    )
    parser.add_argument(
        '-o', '--output', 
        type=argparse.FileType('w'), 
        default=sys.stdout, 
        help='Output process communication to this file, otherwise to stdout',
    )
    parser.add_argument(
        'cmd', 
        type=str, 
        help='The command to execute while blastin',
    )

    args = parser.parse_args()

    cmd = shlex.split(args.cmd)

    waiter = Game(
        cmd = cmd,
        game = args.game,
        auto_quit = args.auto_quit,
        refresh_rate = args.refresh_rate,
    )

    waiter.run()
    
    c = waiter.grid['proc'].content
    if waiter.grid['proc'].reader.is_alive():
        while waiter.grid['proc'].reader.is_alive():
            while len(c) > 0:
                print(c.pop(0).decode().strip())
        while len(c) > 0:
            print(c.pop(0).decode().strip())
    
    if args.output == sys.stdout:
        print('=== COMMAND OUTPUT ===\n')

    waiter.grid['proc'].cache_file.seek(0)
    for line in waiter.grid['proc'].cache_file:
        args.output.write(line.decode())
    
    if waiter.grid['proc'].reader is not None:
        waiter.grid['proc'].reader.join()
        waiter.grid['proc'].cache_file.close()
