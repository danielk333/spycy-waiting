import random
import pkg_resources
import curses

import cursedspace as cs
from cursedspace import Key

from .config import color, box


class Wordle(cs.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with pkg_resources.resource_stream(
                    'spycy_waiting.data', 
                    'wordle_words.txt',
                ) as fh:
            self.words = [line.decode().lower().strip() for line in fh]

    def areas(self):
        y, x, h, w = self.content_area()
        info = [y, x, 4, w]
        play = [y + 4, x, 3*7, w]
        return info, play

    def paint(self, **kwargs):
        super().paint(clear=True)
        info, play = self.areas()
        y, x, h, w = info

        info_str = 'Correct letter, not position'.center(w, ' ')
        self.win.addstr(y, x, info_str[:w], color('word_correct_letter'))
        info_str = 'Correct letter AND position'.center(w, ' ')
        self.win.addstr(y + 1, x, info_str[:w], color('word_correct_place'))

        title_attr = curses.A_BOLD | curses.A_UNDERLINE | color('text')
        self.win.addstr(y + 2, x, ' '*w, title_attr)

        y, x, h, w = play

        target = f'Target ({self.word_len} letters):'.center(w, ' ')
        self.win.addstr(y, x, target, color('title'))
        guess_str = '_'*self.word_len
        guess_str = guess_str.center(w, ' ')
        self.win.addstr(y + 1, x, guess_str[:w], color('title'))

        for ind in range(self.max_guesses):
            if ind < self.word_len:
                col = 0
            else:
                col = 1
            boxw = self.word_len + 4
            boxy = y + 3 + (ind - col*self.word_len)*3
            boxx = x + boxw*col + (w - boxw*2)//2
            box(
                self.win, 
                y = boxy, 
                x = boxx, 
                h = 3, 
                w = boxw,
            )
            if ind == self.current_guess:
                self.win.addstr(
                    boxy + 1, 
                    boxx + 2, 
                    self.text, 
                    color('text'),
                )
            else:
                guess_str = self.guesses[ind]
                for cind, (tchar, gchar) in enumerate(zip(self.target_word, guess_str)):
                    if gchar == tchar:
                        g_attr = color('word_correct_place')
                    elif gchar in self.target_word:
                        g_attr = color('word_correct_letter')
                    else:
                        g_attr = color('text')

                    self.win.addstr(
                        boxy + 1,
                        boxx + 2 + cind,
                        gchar,
                        g_attr,
                    )

        y_last = y + 6 + self.max_guesses*3

        for ind in range(len(self.scores)):
            if ind + 1 >= h:
                break
            score_str = self.scores[ind].center(w, ' ')
            self.win.addstr(y_last + ind, x, score_str, color('text'))

        self.win.noutrefresh()

    def handle_input(self, key):
        if key == Key.RETURN:
            self.do_update = True
            return

        if key in [Key.HOME, "^A"]:
            self.cursor = 0
        elif key in [Key.LEFT]:
            self.cursor = max(0, self.cursor-1)
        elif key in [Key.BACKSPACE, "^H"] and self.cursor > 0:
            self.text = self.text[:self.cursor-1] + self.text[self.cursor:]
            self.cursor -= 1
        elif key in ["^U"]:
            self.text = self.text[self.cursor:]
            self.cursor = 0
        elif key in [Key.DELETE] and len(self.text[self.cursor:]) > 0:
            self.text = self.text[:self.cursor] + self.text[self.cursor+1:]
        elif self.cursor == self.word_len:
            return
        elif key in [Key.END, "^E"]:
            self.cursor = len(self.text)
        elif key in [Key.RIGHT]:
            self.cursor = min(len(self.text), self.cursor+1)
        elif len(str(key)) == 1:
            if str(key) != ' ':
                self.text = self.text[:self.cursor] + str(key) + self.text[self.cursor:]
                self.cursor += 1

    def update_state(self):
        if not self.do_update:
            return
        self.do_update = False

        if len(self.text) != self.word_len:
            return

        if self.text not in self.words:
            self.text = ''
            self.cursor = 0
            return

        self.guesses[self.current_guess] = self.text
        self.current_guess += 1

        if self.text.lower() == self.target_word:
            self.reset_and_record = True
            self.score = str(self.current_guess)
        elif self.current_guess >= self.max_guesses:
            self.reset_and_record = True
            self.score = 'Fail'

        if self.reset_and_record:
            self.scores.append(f'{self.target_word}: {self.score}')
            self.reset()
        else:
            self.text = ''
            self.cursor = 0

    def reset(self):
        index = random.randint(0, len(self.words) - 1)
        self.target_word = self.words[index]
        self.word_len = len(self.target_word)
        self.max_guesses = self.word_len*2
        self.guesses = ['_'*self.word_len for x in range(self.max_guesses)]
        self.current_guess = 0
        self.text = ''
        self.cursor = 0
        self.reset_and_record = False
        self.do_update = False

    def setup(self):
        self.reset()
        self.scores = []