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

pygame.init()
font.init()
f = pygame.font.Font("seguisym.ttf", 64)
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 600
TILE_SIZE = SCREEN_WIDTH/8
PIECE_SIZE = 50

COLOR1 = (245, 245, 245, 0)
COLOR2 = (181, 101, 29, 0)
mouse_pos = (0, 0)
images = []

hovered_tile = (None, None)
selected_tile = (None, None)
turn = 0
lightened_tiles = []
temp_game = []


def add_tuples(tuple1, tuple2):
    res = []
    for i in range(len(tuple1)):
        res.append(tuple1[i] + tuple2[i])
    return tuple(res)


def load_images():
    for i in range(1, 13):
        img = image.load(f"./imgs/{i}.png")
        transform.scale(img, (PIECE_SIZE, PIECE_SIZE))
        images.append(img)


screen = display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH))
is_running = True
game = [
    [8, 10,  9,  7,  6,  9, 10,  8],
    [11, 11, 11, 11, 11, 11, 11, 11],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [5,  5,  5,  5,  5,  5,  5,  5],
    [2,  4,  3,  1,  0,  3,  4,  2],
]


load_images()


def lighten_tile(tile):
    s = pygame.Surface((TILE_SIZE, TILE_SIZE),
                       pygame.SRCALPHA)   # per-pixel alpha
    s.fill((0, 255, 0, 50))
    screen.blit(s, (tile[1] * TILE_SIZE, tile[0] * TILE_SIZE))


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


def update_hovered_tile():
    global hovered_tile
    hovered_tile = (
        int(mouse_pos[1]/TILE_SIZE), int(mouse_pos[0]/TILE_SIZE))


def hover_tile(i, j):
    dark = pygame.Surface((TILE_SIZE, TILE_SIZE),
                          flags=pygame.SRCALPHA)
    dark.fill((25, 25, 25, 0))
    screen.blit(dark, (j * TILE_SIZE, i * TILE_SIZE),
                special_flags=pygame.BLEND_RGBA_SUB)


def select_tile(i, j):
    dark = pygame.Surface((TILE_SIZE, TILE_SIZE),
                          flags=pygame.SRCALPHA)
    dark.fill((0, 0, 0, 0))
    screen.blit(dark, (j * TILE_SIZE, i * TILE_SIZE),
                special_flags=pygame.BLEND_RGBA_SUB)


def move_piece(initial, final):
    global turn
    piece = game[initial[0]][initial[1]]
    iy, ix = initial
    fy, fx = final
    if can_piece_move(piece, initial, final):
        game[fy][fx] = game[iy][ix]
        game[iy][ix] = -1
        turn = int(not bool(turn))


def get_tile_value(tile):
    if(tile[0] > 7 or tile[1] > 7 or tile[1] < 0 or tile[0] < 0):
        return None
    return game[tile[0]][tile[1]]


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
    global game
    global temp_game
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
            if(tile_player != turn and tile_player != -1):
                res.append(new_tile)

    res = list(filter(lambda tile: get_tile_value(tile) != None, res))
    res = list(filter(lambda tile: get_piece_player(
        get_tile_value(tile)) != player, res))
    if(check_free):
        temp_game = copy.deepcopy(game)

        if piece == 0:
            print(res)
        res = list(
            filter(lambda tile: not is_move_giving_check(initial, tile), res))
        if piece == 0:
            print(res)
        game = copy.deepcopy(temp_game)
    return res


def get_under_attack_tiles(temp_game, turn):
    opponent_pieces = [0, 1, 2, 3, 4, 5] if turn == 1 else [6, 7, 8, 9, 10, 11]
    opponent_piece_tiles = []
    for i in range(0, 8):
        for j in range(0, 8):
            if game[i][j] in opponent_pieces:
                opponent_piece_tiles.append((i, j))

    attacked_tiles = list(map(lambda tile: get_valid_moves(
        get_tile_value(tile), tile, False), opponent_piece_tiles))


def is_king_under_attack(king_tile):
    # global game
    global game
    ky, kx = king_tile
    king = temp_game[ky][kx]
    opponent_pieces = [0, 1, 2, 3, 4, 5] if turn == 1 else [6, 7, 8, 9, 10, 11]
    # for i in range(0, 8):
    #     for j in range(0, 8):
    #         if temp_game[i][j] == king:
    #             king_tile = (i, j)
    opponent_piece_tiles = []
    for i in range(0, 8):
        for j in range(0, 8):
            if game[i][j] in opponent_pieces:
                opponent_piece_tiles.append((i, j))

    attacked_tiles = list(map(lambda tile: get_valid_moves(
        game[tile[0]][tile[1]], tile, False), opponent_piece_tiles))
    print(king_tile)
    lightened_tiles = []
    for tile_list in attacked_tiles:
        # for t in tile_list:
        #     lightened_tiles.append(t)
        if king_tile in tile_list:
            # print("True")
            print(tile_list, tile_list)
            return True
    return False


def is_move_giving_check(initial, final):
    global game
    king = 0 if turn == 0 else 6
    king_tile = (None, None)

    game = copy.deepcopy(temp_game)
    game[final[0]][final[1]] = game[initial[0]][initial[1]]
    game[initial[0]][initial[1]] = -1

    for i in range(0, 8):
        for j in range(0, 8):
            if game[i][j] == king:
                king_tile = (i, j)
    # print(king_tile)
    return is_king_under_attack(king_tile)


def can_piece_move(piece, initial, final):
    global selected_tile
    iy, ix = initial
    fy, fx = final
    valid_moves = get_valid_moves(piece, initial)
    for move in valid_moves:
        if(final == move):
            selected_tile = (None, None)
            return True
    return False


def on_tile_click():
    global selected_tile
    i, j = hovered_tile
    tile1_player = get_piece_player(game[i][j])
    # print(player, game[i][j])

    if selected_tile == (None, None):
        if(game[i][j] == -1):
            return 0
        elif(tile1_player != turn):
            return 0
        else:
            selected_tile = (hovered_tile[0], hovered_tile[1])
    else:
        if hovered_tile == selected_tile:
            selected_tile = (None, None)

        elif tile1_player != turn:
            move_piece(selected_tile, hovered_tile)

        else:
            selected_tile = (hovered_tile[0], hovered_tile[1])


def draw_board():
    global lightened_tiles
    for i in range(0, 8):
        for j in range(0, 8):
            moves = []
            piece_value = game[i][j]
            color = get_tile_color(i, j)
            # Draw rectangle
            start_x = j * TILE_SIZE
            start_y = i * TILE_SIZE
            draw.rect(screen, color, pygame.Rect(
                start_x, start_y, TILE_SIZE, TILE_SIZE))
            if(piece_value != -1):
                piece_image = images[piece_value]
                image_x = start_x + (TILE_SIZE - PIECE_SIZE)/2
                image_y = start_y + (TILE_SIZE - PIECE_SIZE)/2
                screen.blit(piece_image, (image_x, image_y))

            h, k = selected_tile
            if selected_tile != (None, None):
                selected_piece_value = game[h][k] % 6
                moves = get_valid_moves(
                    selected_piece_value, selected_tile)
            if((i, j) == selected_tile):
                select_tile(i, j)
            elif ((i, j) == hovered_tile):
                hover_tile(i, j)

            else:

                if (i, j) in moves or (i, j) in lightened_tiles:
                    # print(i, j, "selected")
                    lighten_tile((i, j))
                else:
                    dark = pygame.Surface((TILE_SIZE, TILE_SIZE),
                                          flags=pygame.SRCALPHA)
                    dark.fill((50, 50, 50, 0))
                    screen.blit(dark, (j * TILE_SIZE, i * TILE_SIZE),
                                special_flags=pygame.BLEND_RGBA_SUB)


def update_game():
    draw_board()
    pygame.display.update()


while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            update_hovered_tile()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if(mouse.get_pressed() == (1, 0, 0)):
                on_tile_click()
                update_game()
