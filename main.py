import pygame
import sys
from board import Board
from button import Button  # NEW: moved to button.py

# Initialize Pygame and create the window
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Checkers")
icon = pygame.image.load("assets/black_king.png")
pygame.display.set_icon(icon)

# Load background and font
bg_img = pygame.image.load("assets/bg.jpg")
title_font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 50)

# Game state
MENU = "menu"
GAME = "game"
END = "end"
state = MENU

# Buttons and board
btn_2player = Button("2player", (300, 250))
btn_easy = Button("easy", (300, 350))
btn_hard = Button("hard", (300, 450))
board = None
winner = None

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and state == GAME:
            board.handle_click(event.pos)

    screen.fill((255, 255, 255))

    if state == MENU:
        scaled_bg = pygame.transform.scale(bg_img, (600, 600))
        screen.blit(scaled_bg, (0, 0))
        title_text = title_font.render("CHECKERS", True, (255, 255, 255))
        title_x = (600 - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, 80))

        if btn_2player.draw(screen):
            board = Board()
            state = GAME
        btn_easy.draw(screen)
        btn_hard.draw(screen)

    elif state == GAME:
        board.draw(screen)
        winner = board.check_win()  # <- You'll add this to board.py
        if winner:
            state = END

    elif state == END:
        scaled_bg = pygame.transform.scale(bg_img, (600, 600))
        screen.blit(scaled_bg, (0, 0))
        msg = f"{winner.upper()} WINS!"
        end_text = title_font.render(msg, True, (255, 255, 255))
        screen.blit(end_text, (50, 260))
        pygame.display.flip()
        pygame.time.delay(3000)
        state = MENU
        board = None
        winner = None

    pygame.display.flip()

pygame.quit()
sys.exit()
