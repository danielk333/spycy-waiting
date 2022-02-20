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

import cursedspace as cs

from .config import color
from .crusaders import Crusaders
from .wordle import Wordle

GAMES = OrderedDict(
    wordle = Wordle,
    crusaders = Crusaders,
)

QUIT_KEYS = [cs.Key.ESCAPE, "^Q"]


def read_pipe(proc, output, cache_file):
    for line in iter(proc.stdout.readline, b''):
        if len(line) > 0:
            output.append(line)
            cache_file.write(line)


class Process(cs.Panel):
    def __init__(self, app, cmd, **kwargs):
        self.auto_quit = kwargs.pop('auto_quit')
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
            if self.auto_quit:
                self.app.quit_now = True
            status = 'Process: Finished'
        status = status.center(w, ' ')
        help_str = 'To quit (does not abort process), press:'
        self.win.addstr(y, x, help_str[:w], color('text'))
        help_str = ' '.join([str(x) for x in QUIT_KEYS])
        self.win.addstr(y + 1, x, help_str[:w], color('help'))
        self.win.addstr(y + 2, x, status[:w], title_attr)
        h -= 3
        y += 3

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


class Game(cs.Application):
    def __init__(self, cmd, args):
        super().__init__()
        self.args = args
        self.quit_now = False

        coords = {'game': (0, 0)}
        if self.args.horizontal_split:
            grid_cfg = dict(rows=2, cols=1)
            coords['proc'] = (1, 0)
        else:
            grid_cfg = dict(rows=1, cols=2)
            coords['proc'] = (0, 1)

        self.grid = cs.Grid(self, **grid_cfg)

        self.grid.add_panel(
            *coords['game'], 
            key='game', 
            panel_class=GAMES[self.args.game],
        )
        self.grid.add_panel(
            *coords['proc'], 
            key='proc', 
            panel_class=Process,
            args=(cmd, ),
            kwargs={'auto_quit': self.args.auto_quit},
        )

        for panel in self.grid.panels:
            panel.border = cursedspace.Panel.BORDER_ALL

    def draw(self):
        self.grid.paint()
        curses.doupdate()

    def main(self):
        self.resize()
        self.screen.timeout(int(self.args.refresh_rate*1e3))
        self.show_cursor(False)

        self.grid['game'].setup()
        t0 = time.monotonic()

        while True:
            self.draw()
            
            key = self.read_key()

            if key == cs.Key.RESIZE:
                self.resize()
            elif key in (QUIT_KEYS + ["^C"]):
                break

            if self.quit_now:
                break

            self.grid['game'].handle_input(key)

            t1 = time.monotonic()
            dt = t1 - t0
            if dt > self.args.refresh_rate:
                t0 = t1
                self.grid['game'].update_state()
            else:
                time.sleep((self.args.refresh_rate - dt)*0.5)

    def cleanup(self):
        c = self.grid['proc'].content
        process_done = False if self.grid['proc'].reader.is_alive() else True

        while not process_done:
            while len(c) > 0:
                print(c.pop(0).decode().strip())
            process_done = False if self.grid['proc'].reader.is_alive() else True

        while len(c) > 0:
            print(c.pop(0).decode().strip())

        if self.args.output == sys.stdout:
            print('=== COMPLETE COMMAND OUTPUT ===\n')

        self.grid['proc'].cache_file.seek(0)
        for line in self.grid['proc'].cache_file:
            self.args.output.write(line.decode())
            
        if self.grid['proc'].reader is not None:
            self.grid['proc'].reader.join()
            self.grid['proc'].cache_file.close()

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
        '-hsplit', '--horizontal-split', 
        action='store_true', 
        help='Split the screen horizontally instead of vertically',
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
        args = args,
    )

    waiter.run()
    waiter.cleanup()
