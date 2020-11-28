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
from game_helpers import add_opposite_dirs, get_king_tile, get_tile_player, lighten_tile, get_piece_player, get_tile_color, get_tile_value, get_moves_in_dir
from data import data

pygame.init()
font.init()


def update_hovered_tile():
    data.hovered_tile = (
        int(data.mouse_pos[1]/TILE_SIZE), int(data.mouse_pos[0]/TILE_SIZE))


def swap_piece(initial, final):
    iy, ix = initial
    fy, fx = final
    data.game[fy][fx] = data.game[iy][ix]
    data.game[iy][ix] = -1


def move_piece(initial, final):
    piece = get_tile_value(initial)
    valid_moves = get_valid_moves(piece, initial)
    if final in valid_moves:
        data.selected_tile = (None, None)
        swap_piece(initial, final)
        data.turn = int(not bool(data.turn))
        update_tile_of_players()


def get_valid_moves(piece, initial, check_free=True, attacking_moves_only=False):
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
        # if not attacking_moves_only:
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
            piece_player = get_tile_player(initial)
            if(piece_player != tile_player and tile_player != -1):
                res.append(new_tile)

    res = list(filter(lambda tile: get_tile_value(tile) != None, res))
    res = list(filter(lambda tile: get_piece_player(
        get_tile_value(tile)) != player, res))
    if(check_free):
        data.temp_game = copy.deepcopy(data.game)
        res = list(
            filter(lambda tile: not is_move_giving_check(initial, tile), res))
        data.game = copy.deepcopy(data.temp_game)
    return res


def get_under_attack_tiles():
    pass


def is_king_under_attack(king_tile):
    ky, kx = king_tile
    king = data.temp_game[ky][kx]
    opponent_piece_tiles = data.tiles_of_players[0] if data.turn == 1 else data.tiles_of_players[1]
    attacked_tiles = list(map(lambda tile: get_valid_moves(
        data.game[tile[0]][tile[1]], tile, False, True), opponent_piece_tiles))

    for tile_list in attacked_tiles:
        if king_tile in tile_list:
            return True
    return False


def is_move_giving_check(initial, final):
    # set game to current game position
    data.game = copy.deepcopy(data.temp_game)
    swap_piece(initial, final)
    king_tile = get_king_tile()
    return is_king_under_attack(king_tile)


def on_tile_click():

    selected_tile = data.selected_tile
    hovered_tile = data.hovered_tile
    hovered_tile_value = get_tile_value(hovered_tile)
    hovered_tile_player = get_piece_player(hovered_tile_value)

    if selected_tile == (None, None):
        if hovered_tile_player == data.turn:
            data.selected_tile = copy.copy(hovered_tile)
    else:
        if hovered_tile == selected_tile:
            data.selected_tile = (None, None)

        elif hovered_tile_player != data.turn:
            move_piece(selected_tile, hovered_tile)

        else:
            data.selected_tile = copy.copy(hovered_tile)


def set_tile_brightness(tile, brightness):
    i, j = tile
    dark = pygame.Surface((TILE_SIZE, TILE_SIZE),
                          flags=pygame.SRCALPHA)
    dark.fill((brightness, brightness, brightness, 0))
    data.screen.blit(dark, (j * TILE_SIZE, i * TILE_SIZE),
                     special_flags=pygame.BLEND_RGBA_SUB)


def draw_board():

    # Get valid moves for selected tile
    selected_tile = data.selected_tile
    moves = []
    if selected_tile != (None, None):
        selected_piece_value = get_tile_value(selected_tile)
        moves = get_valid_moves(
            selected_piece_value, selected_tile)

    # Running 8 x 8 loop
    for i in range(0, 8):
        for j in range(0, 8):
            piece_value = get_tile_value((i, j))
            color = get_tile_color(i, j)
            # Draw rectangle
            start_x = j * TILE_SIZE
            start_y = i * TILE_SIZE
            draw.rect(data.screen, color, pygame.Rect(
                start_x, start_y, TILE_SIZE, TILE_SIZE))

            # Draw pieces to blocks
            if(piece_value != -1):
                piece_image = images[piece_value]
                image_x = start_x + (TILE_SIZE - PIECE_SIZE)/2
                image_y = start_y + (TILE_SIZE - PIECE_SIZE)/2
                data.screen.blit(piece_image, (image_x, image_y))

            # Managing selection and hovering
            if((i, j) == data.selected_tile):
                # select_tile(i, j)
                set_tile_brightness((i, j), 0)
            elif ((i, j) == data.hovered_tile):
                set_tile_brightness((i, j), 25)
            else:
                if (i, j) in moves:
                    lighten_tile((i, j))
                else:
                    set_tile_brightness((i, j), 50)


def update_tile_of_players():
    for i in range(0, 8):
        for j in range(0, 8):
            tile_player = get_tile_player((i, j))
            if tile_player == 0 or tile_player == 1:
                data.tiles_of_players[tile_player].append((i, j))


def update_game():
    draw_board()
    pygame.display.update()


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
