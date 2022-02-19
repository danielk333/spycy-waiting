import curses

from cursedspace import colors


COLOR_MAPPING = {
    'text': (1, 0), 
    'title': (2, 0),
    'key': (11, 0),
    'crus_player': (2, 0),
    'crus_enemy': (3, 0),
    'crus_terrain': (4, 0),
    'word_correct_letter': (9, 11),
    'word_correct_place': (9, 4),
}
COLORS = {key: colors.ColorPair(*x) for key, x in COLOR_MAPPING.items()}

BORDER_CORNER = '┌┐┘└'
BORDER_VERT = '│'
BORDER_HORIZ = '─'


def color(key):
    return colors.attr(COLORS[key])


def box(win, y, x, h, w):

    win.addstr(y, x, BORDER_CORNER[0])
    win.addstr(y, x + w - 1, BORDER_CORNER[1])
    win.addstr(y + h - 1, x + w - 1, BORDER_CORNER[2])
    win.addstr(y + h - 1, x, BORDER_CORNER[3])

    win.addstr(y, x + 1, BORDER_HORIZ*(w - 2))
    win.addstr(y + 1, x + w - 1, BORDER_VERT*(h - 2))
    win.addstr(y + h - 1, x + 1, BORDER_HORIZ*(w - 2))
    win.addstr(y + 1, x, BORDER_VERT*(h - 2))
