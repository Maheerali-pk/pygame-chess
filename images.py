from consts import PIECE_SIZE, TILE_SIZE
import pygame
import pygame.image as image
import pygame.transform as transform
images = []
for i in range(1, 13):
    img = image.load(f"./imgs/{i}.png")
    img = transform.scale(img, (PIECE_SIZE, PIECE_SIZE))
    images.append(img)
