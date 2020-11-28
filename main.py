from data import Data
from pygame import *
import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.font as font
import pygame.image as image
import pygame.transform as transform
import pygame.time as time
import pygame.mouse as mouse
import copy
from helpers import add_tuple_list, add_tuples
from consts import COLOR1, COLOR2, PIECE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE
from images import images
from game_helpers import get_piece_player, get_tile_color

data = Data()


pygame.init()
font.init()
f = pygame.font.Font("seguisym.ttf", 64)
valid_moves_called = 0


def lighten_tile(tile):
    s = pygame.Surface((TILE_SIZE, TILE_SIZE),
                       pygame.SRCALPHA)   # per-pixel alpha
    s.fill((0, 255, 0, 50))
    data.screen.blit(s, (tile[1] * TILE_SIZE, tile[0] * TILE_SIZE))


def update_hovered_tile():
    data.hovered_tile = (
        int(data.mouse_pos[1]/TILE_SIZE), int(data.mouse_pos[0]/TILE_SIZE))


def hover_tile(i, j):
    dark = pygame.Surface((TILE_SIZE, TILE_SIZE),
                          flags=pygame.SRCALPHA)
    dark.fill((25, 25, 25, 0))
    data.screen.blit(dark, (j * TILE_SIZE, i * TILE_SIZE),
                     special_flags=pygame.BLEND_RGBA_SUB)


def select_tile(i, j):
    dark = pygame.Surface((TILE_SIZE, TILE_SIZE),
                          flags=pygame.SRCALPHA)
    dark.fill((0, 0, 0, 0))
    data.screen.blit(dark, (j * TILE_SIZE, i * TILE_SIZE),
                     special_flags=pygame.BLEND_RGBA_SUB)


def move_piece(initial, final):
    piece = data.game[initial[0]][initial[1]]
    iy, ix = initial
    fy, fx = final
    if can_piece_move(piece, initial, final):
        data.game[fy][fx] = data.game[iy][ix]
        data.game[iy][ix] = -1
        data.turn = int(not bool(data.turn))
        update_tile_of_players()


def get_tile_value(tile):
    if(tile[0] > 7 or tile[1] > 7 or tile[1] < 0 or tile[0] < 0):
        return None
    return data.game[tile[0]][tile[1]]


def get_moves_in_dir(initial, directions):
    moves = []
    for d in directions:
        is_way_open = True
        tile = (initial[0], initial[1])
        i = 0
        while is_way_open:
            i += 1
            tile = add_tuples(tile, d)

            tile_value = get_tile_value(tile)
            if tile_value == None:
                is_way_open = False
            elif tile_value != -1:
                moves.append(tile)
                is_way_open = False
            else:
                moves.append(tile)

            if(i > 100):
                break
    return moves


def add_opposite_dirs(arr):
    return arr + list(map(lambda d: (-d[0], -d[1]), arr))


def get_tile_player(tile):
    return get_piece_player(get_tile_value(tile))


def get_valid_moves(piece, initial, check_free=True):
    # valid_moves_called += 1
    y, x = initial
    res = []
    original_piece = piece
    piece = piece % 6
    player = get_piece_player(get_tile_value(initial))
    if initial == (None, None):
        return []
    if piece == 0:
        dirs = add_opposite_dirs([(1, 0), (0, 1), (1, 1), (1, -1)])
        res = list(map(lambda d: add_tuples(d, initial), dirs))
    elif piece == 1:
        dirs = [(1, 1), (-1, -1), (-1, 1), (1, -1),
                (1, 0), (-1, 0), (0, 1), (0, -1)]
        res = get_moves_in_dir(initial, dirs)
    elif piece == 2:
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        res = get_moves_in_dir(initial, dirs)
    elif piece == 3:
        dirs = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
        res = get_moves_in_dir(initial, dirs)
    elif piece == 4:
        dirs = add_opposite_dirs([(2, 1), (1, 2), (-2, 1), (-1, 2)])
        res = list(map(lambda d: add_tuples(d, initial), dirs))

    elif piece == 5:
        d = -1 if player == 0 else 1
        initial_row = 6 if player == 0 else 1
        not_moved = initial[0] == initial_row
        first_tile = add_tuples(initial, (d, 0))
        first_tile_value = get_tile_value(first_tile)
        if(first_tile_value == -1):
            res.append(first_tile)
            second_tile = add_tuples(initial, (d * 2, 0))
            second_tile_value = get_tile_value(second_tile)
            if(second_tile_value == -1 and not_moved):
                res.append(second_tile)

        diagonals = [(d, -d), (d, d)]
        for dia in diagonals:
            new_tile = add_tuples(initial, dia)
            tile_player = get_tile_player(new_tile)
            if(tile_player != data.turn and tile_player != -1):
                res.append(new_tile)

    res = list(filter(lambda tile: get_tile_value(tile) != None, res))
    res = list(filter(lambda tile: get_piece_player(
        get_tile_value(tile)) != player, res))
    if(check_free):
        data.temp_game = copy.deepcopy(data.game)

        # if piece == 0:
        #     print(res)
        res = list(
            filter(lambda tile: not is_move_giving_check(initial, tile), res))
        # if piece == 0:
        #     print(res)
        data.game = copy.deepcopy(data.temp_game)
    return res


# def get_under_attack_tiles(temp_game, turn):
#     opponent_pieces = [0, 1, 2, 3, 4, 5] if turn == 1 else [6, 7, 8, 9, 10, 11]
#     opponent_piece_tiles = []
#     for i in range(0, 8):
#         for j in range(0, 8):
#             if data.game[i][j] in opponent_pieces:
#                 opponent_piece_tiles.append((i, j))

#     attacked_tiles = list(map(lambda tile: get_valid_moves(
#         get_tile_value(tile), tile, False), opponent_piece_tiles))


def is_king_under_attack(king_tile):
    # global data.game
    ky, kx = king_tile
    king = data.temp_game[ky][kx]
    opponent_piece_tiles = data.tiles_of_players[0] if data.turn == 1 else data.tiles_of_players[1]

    attacked_tiles = list(map(lambda tile: get_valid_moves(
        data.game[tile[0]][tile[1]], tile, False), opponent_piece_tiles))
    # print(king_tile)
    lightened_tiles = []
    for tile_list in attacked_tiles:
        # for t in tile_list:
        #     lightened_tiles.append(t)
        if king_tile in tile_list:
            # print("True")
            # print(tile_list, tile_list)
            return True
    return False


def is_move_giving_check(initial, final):
    king = 0 if data.turn == 0 else 6
    king_tile = (None, None)

    data.game = copy.deepcopy(data.temp_game)
    data.game[final[0]][final[1]] = data.game[initial[0]][initial[1]]
    data.game[initial[0]][initial[1]] = -1

    for i in range(0, 8):
        for j in range(0, 8):
            if data.game[i][j] == king:
                king_tile = (i, j)
    print(king_tile)
    return is_king_under_attack(king_tile)


def can_piece_move(piece, initial, final):
    iy, ix = initial
    fy, fx = final
    valid_moves = get_valid_moves(piece, initial)
    for move in valid_moves:
        if(final == move):
            data.selected_tile = (None, None)
            return True
    return False


def on_tile_click():
    i, j = data.hovered_tile
    tile1_player = get_piece_player(data.game[i][j])
    # print(player, data.game[i][j])

    if data.selected_tile == (None, None):
        if(data.game[i][j] == -1):
            return 0
        elif(tile1_player != data.turn):
            return 0
        else:
            data.selected_tile = (data.hovered_tile[0], data.hovered_tile[1])
    else:
        if data.hovered_tile == data.selected_tile:
            data.selected_tile = (None, None)

        elif tile1_player != data.turn:
            move_piece(data.selected_tile, data.hovered_tile)

        else:
            data.selected_tile = (data.hovered_tile[0], data.hovered_tile[1])


def draw_board():
    h, k = data.selected_tile
    moves = []
    if data.selected_tile != (None, None):
        selected_piece_value = data.game[h][k]
        moves = get_valid_moves(
            selected_piece_value, data.selected_tile)
    for i in range(0, 8):
        for j in range(0, 8):
            piece_value = data.game[i][j]
            color = get_tile_color(i, j)
            # Draw rectangle
            start_x = j * TILE_SIZE
            start_y = i * TILE_SIZE
            draw.rect(data.screen, color, pygame.Rect(
                start_x, start_y, TILE_SIZE, TILE_SIZE))
            if(piece_value != -1):
                piece_image = images[piece_value]
                image_x = start_x + (TILE_SIZE - PIECE_SIZE)/2
                image_y = start_y + (TILE_SIZE - PIECE_SIZE)/2
                data.screen.blit(piece_image, (image_x, image_y))

            if((i, j) == data.selected_tile):
                select_tile(i, j)
            elif ((i, j) == data.hovered_tile):
                hover_tile(i, j)

            else:

                if (i, j) in moves:
                    # print(i, j, "selected")
                    lighten_tile((i, j))
                else:
                    dark = pygame.Surface((TILE_SIZE, TILE_SIZE),
                                          flags=pygame.SRCALPHA)
                    dark.fill((50, 50, 50, 0))
                    data.screen.blit(dark, (j * TILE_SIZE, i * TILE_SIZE),
                                     special_flags=pygame.BLEND_RGBA_SUB)


def update_tile_of_players():
    for i in range(0, 8):
        for j in range(0, 8):
            tile_player = get_tile_player((i, j))
            if tile_player == 0 or tile_player == 1:
                data.tiles_of_players[tile_player].append((i, j))


def update_game():
    # print("updated")
    draw_board()
    pygame.display.update()
    # print(valid_moves_called)


print(data.is_running)
while data.is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            data.is_running = False

        if event.type == pygame.MOUSEMOTION:
            data.mouse_pos = pygame.mouse.get_pos()
            update_hovered_tile()
            update_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if(mouse.get_pressed() == (1, 0, 0)):
                on_tile_click()
                update_game()
