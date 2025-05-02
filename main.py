import pygame
import sys
from board import Board  # Import the Board class from board.py

# Initialize Pygame and create the window
pygame.init()

icon = pygame.image.load("assets/black_king.png")
pygame.display.set_icon(icon)

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Checkers")

# Create the board
board = Board()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            board.handle_click(event.pos)  # NEW: handle mouse clicks

    screen.fill((255, 255, 255))  # White background

    board.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
