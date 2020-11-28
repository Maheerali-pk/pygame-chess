import copy
from types import SimpleNamespace

from pygame import display

from consts import SCREEN_HEIGHT, SCREEN_WIDTH, initial_game


class Data:
    hovered_tile = (None, None)
    selected_tile = (None, None)
    turn = 0
    tiles_of_players = [[], []]
    temp_game = []
    game = copy.deepcopy(initial_game)
    mouse_pos = (0, 0)
    is_running = True
    screen = display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH))


data = Data()
