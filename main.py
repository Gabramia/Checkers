import pygame
import sys
from board import Board
from button import Button
from bot import make_bot_move  # NEW: bot AI

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Checkers")
icon = pygame.image.load("assets/black_king.png")
pygame.display.set_icon(icon)

# Load background and font
bg_img = pygame.image.load("assets/bg.jpg")
title_font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 50)

# Game states
MENU = "menu"
GAME = "game"
END = "end"
state = MENU

# Mode tracker
game_mode = None  # "2player", "easy", "hard"
waiting_for_bot = False
bot_delay_timer = 0
BOT_DELAY_MS = 600

# Buttons and board
btn_2player = Button("2player", (300, 250))
btn_easy = Button("easy", (300, 350))
btn_hard = Button("hard", (300, 450))
board = None
winner = None

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and state == GAME:
            if game_mode == "2player" or board.turn != "red":  # prevent human clicks when bot should play
                board.handle_click(event.pos)

    screen.fill((255, 255, 255))

    if state == MENU:
        scaled_bg = pygame.transform.scale(bg_img, (600, 600))
        screen.blit(scaled_bg, (0, 0))
        title_text = title_font.render("CHECKERS", True, (255, 255, 255))
        title_x = (screen.get_width() - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, 80))

        if btn_2player.draw(screen):
            board = Board()
            game_mode = "2player"
            state = GAME
        elif btn_easy.draw(screen):
            board = Board()
            game_mode = "easy"
            state = GAME
        elif btn_hard.draw(screen):
            board = Board()
            game_mode = "hard"
            state = GAME

    elif state == GAME:
        board.draw(screen,game_mode)

        # Check for winner
        winner = board.check_win()
        if winner:
            state = END
            continue

        # Check if bot has valid moves
        if game_mode in ("easy", "hard") and board.turn == "red":
            jumpables = board.get_all_jumpable_positions("red")
            any_valid = False
            for row in range(board.rows):
                for col in range(board.cols):
                    piece = board.board[row][col]
                    if piece and piece.color == "red":
                        pos = board.index_to_pos(row, col)
                        if board.get_valid_moves(pos) or board.get_all_jump_chains(pos):
                            any_valid = True
            if not any_valid:
                winner = "black"
                state = END
                continue

            if not waiting_for_bot:
                waiting_for_bot = True
                bot_delay_timer = 0
            else:
                bot_delay_timer += dt
                if bot_delay_timer >= BOT_DELAY_MS:
                    make_bot_move(board, game_mode)
                    waiting_for_bot = False

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
        game_mode = None
        waiting_for_bot = False

    pygame.display.flip()

pygame.quit()
sys.exit()
