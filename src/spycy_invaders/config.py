from cursedspace import colors

# refresh time in s
UPDATE_RATE = 0.300

COLOR_MAPPING = {
    'text': (1, 0), 
    'title': (2, 0),
    'player': (2, 0),
    'enemy': (3, 0),
    'terrain': (4, 0),
    'shot': (5, 0),
}
COLORS = {key: colors.ColorPair(*x) for key, x in COLOR_MAPPING.items()}


def color(key):
    return colors.attr(COLORS[key])
