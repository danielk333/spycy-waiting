import curses
import pathlib
import configparser

try:
    from xdg import BaseDirectory
except ImportError:
    BaseDirectory = None

from cursedspace import colors

PROGRAMNAME = 'spycy_waiting'
HOME = pathlib.Path.home()
CONFIGDIR = HOME / ".config"
if BaseDirectory is not None:
    CONFIGDIR = pathlib.Path(BaseDirectory.save_config_path(PROGRAMNAME) or CONFIGDIR)
CONFIGFILE = (CONFIGDIR / (PROGRAMNAME + ".conf")).resolve()

DEFAULT_CONFIG = {
    'General': {
        'text-color': '1, 0',
        'title-color': '2, 0',
        'help-color': '11, 0',
        'default-background-color': '0',
    },
    'Wordle': {
        'correct-letter-color': '9, 11',
        'correct-place-color': '9, 4',
    },
    'Crusaders': {
        'player-color': '2, 0',
        'enemy-color': '11, 0',
    },
}

config = configparser.ConfigParser(interpolation=None)
config.read_dict(DEFAULT_CONFIG)
if CONFIGFILE.exists() and CONFIGFILE.is_file():
    config.read([CONFIGFILE])

with open('/home/danielk/git/spycy-waiting/spycy_waiting.conf', 'w') as configfile:
    config.write(configfile)

DEFAULT_BACKGROUND = config.getint('General', 'default-background-color')

COLOR_MAPPING = {}
for category in config:
    for key in config[category]:
        if not key.endswith('-color') or key.startswith('default'):
            continue

        _col = [int(x.strip()) for x in config.get(category, key).split(',')]
        if len(_col) == 1:
            _col.append(DEFAULT_BACKGROUND)
        COLOR_MAPPING[key.replace('-color', '')] = _col

COLORS = {key: colors.ColorPair(*x) for key, x in COLOR_MAPPING.items()}


def color(key):
    return colors.attr(COLORS[key])
