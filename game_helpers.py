from consts import COLOR1, COLOR2


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
