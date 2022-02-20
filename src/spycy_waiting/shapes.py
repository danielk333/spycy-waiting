from .config import color


BORDER_CORNER = '┌┐┘└'
BORDER_VERT = '│'
BORDER_HORIZ = '─'


class Shape:
    SIZE = None
    TEXTURE = None

    def __init__(self, pos, color):
        # Pos is upper left corner
        self.pos = pos
        self.color = color

    def draw(self, win, x, y, h, w):
        yp = y + self.pos[0]
        xp = x + self.pos[1]
        if xp > w or yp > h:
            return

        if yp > 0:
            row0 = 0
        else:
            row0 = -yp
            yp = y
        row1 = self.SIZE[0] if yp + self.SIZE[0] < h else h - yp + 1

        if xp > 0:
            col0 = 0
        else:
            col0 = -xp
            xp = x
        col1 = self.SIZE[1] if xp + self.SIZE[1] < w else w - xp

        for row in range(row0, row1):
            win.addstr(
                yp + row, 
                xp, 
                self.TEXTURE[row][col0:col1], 
                color(self.color),
            )


class Player(Shape):
    SIZE = (2, 1)
    TEXTURE = (
        '█',
        '█',
    )


class Invader(Shape):
    SIZE = (2, 5)
    TEXTURE = (
        ' ██ ',
        '█  █',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction = 1


def box(win, y, x, h, w):

    win.addstr(y, x, BORDER_CORNER[0])
    win.addstr(y, x + w - 1, BORDER_CORNER[1])
    win.addstr(y + h - 1, x + w - 1, BORDER_CORNER[2])
    win.addstr(y + h - 1, x, BORDER_CORNER[3])

    win.addstr(y, x + 1, BORDER_HORIZ*(w - 2))
    win.addstr(y + 1, x + w - 1, BORDER_VERT*(h - 2))
    win.addstr(y + h - 1, x + 1, BORDER_HORIZ*(w - 2))
    win.addstr(y + 1, x, BORDER_VERT*(h - 2))
