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
black_king_icon = pygame.image.load("assets/black_king.png")
red_king_icon = pygame.image.load("assets/red_king.png")
bg_img = pygame.image.load("assets/bg.jpg")
title_font = pygame.font.Font("assets/fonts/PressStart2P.ttf", 50)
input_font = pygame.font.SysFont("arial", 24)
back_label = input_font.render("Back", True, (0, 0, 0))
back_rect = back_label.get_rect(bottomright=(590, 25))



# Game states
MENU = "menu"
REPLAY_MENU = "replay_menu""menu"
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
btn_replay_left = Button("arrow_left", (30, 300))
btn_replay_right = Button("arrow_right", (570, 300))
replay_files = []
replay_page = 0
replay_data = []
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
        history_label = input_font.render("History", True, (255, 255, 255))
        history_rect = history_label.get_rect(bottomright=(590, 590))
        screen.blit(history_label, history_rect)
        if pygame.mouse.get_pressed()[0] and history_rect.collidepoint(pygame.mouse.get_pos()):
            state = REPLAY_MENU

    elif state == NAME_INPUT:
        screen.blit(pygame.transform.scale(bg_img, (600, 600)), (0, 0))
        screen.blit(back_label, back_rect)
        if pygame.mouse.get_pressed()[0] and back_rect.collidepoint(pygame.mouse.get_pos()):
            state = MENU
            continue

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
                    recorder.set_players(name_black, selected_mode.upper())
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
        screen.blit(back_label, back_rect)
        if pygame.mouse.get_pressed()[0] and back_rect.collidepoint(pygame.mouse.get_pos()):
            state = MENU
            continue



    elif state == REPLAY_MENU:
        screen.blit(pygame.transform.scale(bg_img, (600, 600)), (0, 0))
        title_font_big = pygame.font.SysFont("arial", 32, bold=True)
        title = title_font_big.render("Replays", True, (0, 0, 0))
        screen.blit(title, (230, 10))  # Top spacing
        screen.blit(back_label, back_rect)
        if pygame.mouse.get_pressed()[0] and back_rect.collidepoint(pygame.mouse.get_pos()):
            state = MENU
            continue

        import os, json
        if not replay_files:
            replay_files[:] = sorted(os.listdir("replays"), reverse=True)
            replay_files = [f for f in replay_files if f.endswith(".json")]

        box_height = 110
        top_margin = 50
        vertical_gap = 15  # Increased spacing between boxes
        max_display = 4

        for i in range(max_display):
            idx = replay_page * max_display + i
            if idx >= len(replay_files):
                break

            file = replay_files[idx]
            with open(os.path.join("replays", file), "r") as f:
                data = json.load(f)

            black = data["player_black"]
            if black.upper() == "BOT":
                black = "EASY" if "easy" in file.lower() else "HARD"
            red = data["player_red"]
            if red.upper() == "BOT":
                red = "EASY" if "easy" in file.lower() else "HARD"
            winner = data["winner"]
            date = file.split("_")[0] + " " + file.split("_")[1].replace("-", ":")

            y_offset = top_margin + i * (box_height + vertical_gap)
            pygame.draw.rect(screen, (255, 255, 255), (70, y_offset, 460, box_height))

            # Black Side (Left)
            screen.blit(black_king_icon, (80, y_offset + 10))
            screen.blit(input_font.render(black, True, (0, 0, 0)), (90, y_offset + 75))  # 10px inside box edge

            # Red Side (Right)
            red_icon_x = 470
            red_text_x = 470 + 50 - input_font.size(red)[0]  # So name ends before box edge
            screen.blit(red_king_icon, (red_icon_x, y_offset + 10))
            screen.blit(input_font.render(red, True, (0, 0, 0)), (red_text_x, y_offset + 75))

            # Center info
            screen.blit(input_font.render(date, True, (0, 0, 0)), (230, y_offset + 10))
            screen.blit(input_font.render("Winner is:", True, (0, 0, 0)), (245, y_offset + 40))
            winner_font = pygame.font.SysFont("arial", 28, bold=True)
            screen.blit(winner_font.render(winner.upper(), True, (0, 0, 0)), (245, y_offset + 65))

        # Arrows and Page Number
        btn_replay_left.draw(screen)
        btn_replay_right.draw(screen)
        page_label = input_font.render(f"PAGE: [{replay_page + 1}]", True, (255, 200, 0))
        screen.blit(page_label, (240, 570))



    elif state == END:
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
