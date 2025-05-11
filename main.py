import pygame
import sys
from board import Board
from button import Button
from bot import make_bot_move
from recorder import MatchRecorder

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Checkers")
icon = pygame.image.load("assets/black_king.png")
pygame.display.set_icon(icon)

# Load background and font
bg_img = pygame.image.load("assets/bg.jpg")
title_font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 50)
input_font = pygame.font.SysFont("arial", 24)

# Game states
MENU = "menu"
SIDE_SELECT = "side_select"
GAME = "game"
END = "end"
NAME_INPUT = "name_input"
state = MENU

# Mode trackers
game_mode = None
selected_mode = None
player_color = "black"
waiting_for_bot = False
bot_delay_timer = 0
BOT_DELAY_MS = 600
flip_pause_timer = 0
FLIP_PAUSE_MS = 300
pending_flip = False

name_black = ""
name_red = ""
active_input = None

# Buttons and board
btn_2player = Button("2player", (300, 250))
btn_easy = Button("easy", (300, 350))
btn_hard = Button("hard", (300, 450))
btn_red = Button("red", (300, 370))
btn_black = Button("black", (300, 470))
board = None
winner = None
recorder = None
last_selected = None

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60)

    screen.fill((255, 255, 255))

    if state == MENU:
        screen.blit(pygame.transform.scale(bg_img, (600, 600)), (0, 0))
        title_text = title_font.render("CHECKERS", True, (255, 255, 255))
        screen.blit(title_text, ((600 - title_text.get_width()) // 2, 80))

        if btn_2player.draw(screen):
            game_mode = "2player"
            state = NAME_INPUT
        elif btn_easy.draw(screen):
            selected_mode = "easy"
            game_mode = selected_mode
            state = NAME_INPUT
        elif btn_hard.draw(screen):
            selected_mode = "hard"
            game_mode = selected_mode
            state = NAME_INPUT

    elif state == NAME_INPUT:
        screen.blit(pygame.transform.scale(bg_img, (600, 600)), (0, 0))

        if game_mode == "2player":
            blk_label = input_font.render("BLACK:", True, (0, 0, 0))
            screen.blit(blk_label, (150, 150))
            pygame.draw.rect(screen, (255, 255, 255), (150, 180, 300, 40))
            screen.blit(input_font.render(name_black, True, (0, 0, 0)), (155, 190))

            red_label = input_font.render("RED:", True, (0, 0, 0))
            screen.blit(red_label, (150, 270))
            pygame.draw.rect(screen, (255, 255, 255), (150, 300, 300, 40))
            screen.blit(input_font.render(name_red, True, (0, 0, 0)), (155, 300))

            pygame.draw.rect(screen, (0, 200, 0), (200, 400, 200, 40))
            screen.blit(input_font.render("START", True, (255, 255, 255)), (260, 410))

        else:
            label = input_font.render("ENTER YOUR NAME:", True, (0, 0, 0))
            screen.blit(label, (150, 170))
            pygame.draw.rect(screen, (255, 255, 255), (150, 200, 300, 40))
            screen.blit(input_font.render(name_black, True, (0, 0, 0)), (155, 210))
            screen.blit(input_font.render("CHOOSE SIDE", True, (0, 0, 0)), (200, 290))

            red_clicked = btn_red.draw(screen)
            black_clicked = btn_black.draw(screen)
            if name_black.strip():
                if red_clicked:
                    player_color = "red"
                    board = Board()
                    board.turn = "black"
                    game_mode = selected_mode
                    recorder = MatchRecorder()
                    recorder.set_players(name_black, "BOT")
                    state = GAME
                elif black_clicked:
                    player_color = "black"
                    board = Board()
                    board.turn = "black"
                    game_mode = selected_mode
                    recorder = MatchRecorder()
                    recorder.set_players(name_black, "BOT")
                    state = GAME

    elif state == GAME:
        if pending_flip:
            flip = not ((game_mode == '2player' and board.turn == 'red') or (game_mode in ('easy', 'hard') and player_color == 'red'))
            board.draw(screen, game_mode, flip_board=flip)
            flip_pause_timer -= dt
            if flip_pause_timer <= 0:
                pending_flip = False
        else:
            flip = (game_mode == '2player' and board.turn == 'red') or (game_mode in ('easy', 'hard') and player_color == 'red')
            board.draw(screen, game_mode, flip_board=flip)

        winner = board.check_win()
        if winner:
            recorder.set_winner(winner)
            recorder.save_to_file()
            state = END
            continue

        if game_mode in ("easy", "hard") and board.turn != player_color:
            if not waiting_for_bot:
                waiting_for_bot = True
                bot_delay_timer = 0
            else:
                bot_delay_timer += dt
                if bot_delay_timer >= BOT_DELAY_MS:
                    before = board.selected_square
                    make_bot_move(board, game_mode)
                    after = board.selected_square
                    if recorder and before and not after:
                        end_square = board.valid_moves[0]
                        recorder.record_move(before, end_square)
                    waiting_for_bot = False

    elif state == END:
        screen.blit(pygame.transform.scale(bg_img, (600, 600)), (0, 0))
        msg = f"{winner.upper()} WINS!"
        end_text = title_font.render(msg, True, (255, 255, 255))
        screen.blit(end_text, (50, 260))
        pygame.display.flip()
        pygame.time.delay(3000)
        state = MENU
        board = None
        winner = None
        game_mode = None
        selected_mode = None
        waiting_for_bot = False
        name_black = ""
        name_red = ""
        active_input = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and state == NAME_INPUT:
            if active_input == "black":
                if event.key == pygame.K_BACKSPACE:
                    name_black = name_black[:-1]
                else:
                    name_black += event.unicode
            elif active_input == "red":
                if event.key == pygame.K_BACKSPACE:
                    name_red = name_red[:-1]
                else:
                    name_red += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == GAME:
                if game_mode == "2player" or board.turn == player_color:
                    last_selected = board.selected_square
                    board.handle_click(event.pos, game_mode, player_color)
                    if recorder and last_selected and not board.selected_square:
                        target = board.get_square_under_mouse(event.pos, game_mode, player_color)
                        if target:
                            recorder.record_move(last_selected, target)
                        if game_mode == "2player":
                            pending_flip = True
                            flip_pause_timer = FLIP_PAUSE_MS
                        target = board.get_square_under_mouse(event.pos, game_mode, player_color)
                        if target:
                            recorder.record_move(last_selected, target)
            elif state == NAME_INPUT:
                mx, my = pygame.mouse.get_pos()
                if game_mode == "2player":
                    if 150 < mx < 450 and 180 < my < 220:
                        active_input = "black"
                    elif 150 < mx < 450 and 290 < my < 330:
                        active_input = "red"
                    elif 200 < mx < 400 and 400 < my < 440:
                        if name_black.strip() and name_red.strip():
                            board = Board()
                            recorder = MatchRecorder()
                            recorder.set_players(name_black, name_red)
                            state = GAME
                else:
                    if 150 < mx < 450 and 200 < my < 240:
                        active_input = "black"

    pygame.display.flip()

pygame.quit()
sys.exit()
