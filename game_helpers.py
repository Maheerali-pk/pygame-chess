from copy import copy

import pygame
from helpers import add_tuples
from consts import COLOR1, COLOR2, TILE_SIZE
from data import data


def get_piece_player(num):
    if(num == None):
        return None
    if num == -1:
        return -1
    res = 1 if num >= 6 else 0
    return res


def get_tile_color(i, j):
    is_even = (i + j) % 2 == 0
    color = COLOR1 if is_even else COLOR2
    return color


def get_moves_in_dir(initial, directions):
    moves = []
    for d in directions:
        is_way_open = True
        tile = copy(initial)
        while is_way_open:
            tile = add_tuples(tile, d)
            tile_value = get_tile_value(tile)
            if tile_value == None:
                is_way_open = False
            elif tile_value != -1:
                moves.append(tile)
                is_way_open = False
            else:
                moves.append(tile)
    return moves


def get_tile_value(tile):
    for val in list(tile):
        if(val > 7 or val < 0):
            return None
    return data.game[tile[0]][tile[1]]


def lighten_tile(tile):
    s = pygame.Surface((TILE_SIZE, TILE_SIZE),
                       pygame.SRCALPHA)   # per-pixel alpha
    s.fill((0, 255, 0, 50))
    data.screen.blit(s, (tile[1] * TILE_SIZE, tile[0] * TILE_SIZE))


def add_opposite_dirs(arr):
    return arr + list(map(lambda d: (-d[0], -d[1]), arr))


def get_tile_player(tile):
    return get_piece_player(get_tile_value(tile))


def get_king_tile():
    king = 0 if data.turn == 0 else 6
    for i in range(0, 8):
        for j in range(0, 8):
            if data.game[i][j] == king:
                return (i, j)


def swap_piece(initial, final):
    iy, ix = initial
    fy, fx = final
    data.game[fy][fx] = data.game[iy][ix]
    data.game[iy][ix] = -1
