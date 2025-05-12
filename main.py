import pygame
import sys
from board import Board
from button import Button
from bot import make_bot_move
from recorder import MatchRecorder
from piece import Piece


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
back_rect = back_label.get_rect(topright=(590, 10))



# Game states
MENU = "menu"
REPLAY_MENU = "replay_menu""menu"
SIDE_SELECT = "side_select"
GAME = "game"
END = "end"
NAME_INPUT = "name_input"
state = MENU
REPLAY_VIEWER = "replay_viewer"

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
replay_flip_board = False

name_black = ""
name_red = ""
active_input = None
replay_data = None
replay_index = 0
last_replay_page = 0

# Buttons and board
btn_replay_left = Button("arrow_left", (30, 300))
btn_replay_right = Button("arrow_right", (570, 300))
replay_files = []
replay_page = 0
just_entered_history = True
replay_data = []
btn_2player = Button("2player", (300, 250))
btn_easy = Button("easy", (300, 350))
btn_hard = Button("hard", (300, 450))
btn_red = Button("red", (300, 370))
btn_black = Button("black", (300, 470))
btn_step_back = Button("arrow_small_left", (0, 0))
btn_step_forward = Button("arrow_small_right", (0, 0))
board = None
winner = None
recorder = None
last_selected = None

#helper function
def load_replay_state_at(index):
    global board
    states = replay_data.get("states", [])
    if 0 <= index < len(states):
        snapshot_data = states[index]
        snapshot = snapshot_data["board"]  # <-- now inside a dict
        board.board = []

        for row in snapshot:
            new_row = []
            for cell in row:
                if cell is None:
                    new_row.append(None)
                else:
                    kind, color = cell.split("-")
                    new_row.append(Piece(color, is_king=(kind == "K")))
            while len(new_row) < 8:
                new_row.append(None)
            board.board.append(new_row)
        while len(board.board) < 8:
            board.board.append([None] * 8)

        board.turn = snapshot_data.get("turn", "black")  # <-- restore turn info

    board.selected_square = None
    board.valid_moves = []
    board.valid_jump_paths = []








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
            just_entered_history = True


    elif state == NAME_INPUT:
        screen.blit(pygame.transform.scale(bg_img, (600, 600)), (0, 0))
        screen.blit(back_label, back_rect)
        if pygame.mouse.get_pressed()[0] and back_rect.collidepoint(pygame.mouse.get_pos()):
            state = MENU
            name_black = ""
            name_red = ""
            active_input = None
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
                    recorder.set_players("BOT", name_black)  # BOT = black, player = red
                    recorder.record_state(board)
                    state = GAME

                elif black_clicked:
                    player_color = "black"
                    board = Board()
                    board.turn = "black"
                    game_mode = selected_mode
                    recorder = MatchRecorder()
                    recorder.set_players(name_black, "BOT")  # player = black, BOT = red
                    recorder.record_state(board)
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
                    start_pos = board.selected_square
                    make_bot_move(board, game_mode)
                    end_pos = board.selected_square
                    if recorder and start_pos and not end_pos:
                        end_square = board.valid_moves[0]
                        recorder.record_state(board)
                    waiting_for_bot = False
        screen.blit(back_label, back_rect)
        if pygame.mouse.get_pressed()[0] and back_rect.collidepoint(pygame.mouse.get_pos()):
            state = MENU
            name_black = ""
            name_red = ""
            active_input = None
            continue




    elif state == REPLAY_MENU:
        screen.blit(pygame.transform.scale(bg_img, (600, 600)), (0, 0))
        title_font_big = pygame.font.SysFont("arial", 32, bold=True)
        title = title_font_big.render("Replays", True, (0, 0, 0))
        screen.blit(title, (230, 10))  # Top spacing
        screen.blit(back_label, back_rect)
        if pygame.mouse.get_pressed()[0] and back_rect.collidepoint(pygame.mouse.get_pos()):
            state = MENU
            name_black = ""
            name_red = ""
            active_input = None
            continue


        import os, json
        if just_entered_history:
            replay_files = sorted(os.listdir("replays"), reverse=True)
            replay_files = [f for f in replay_files if f.endswith(".json")]
            just_entered_history = False


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

            # Assign players to correct sides (based on who is BOT)
            if data["player_red"].upper() == "BOT":
                player_black = data["player_red"]
                player_red = data["player_black"]
            else:
                player_black = data["player_black"]
                player_red = data["player_red"]

            # Format labels for display
            label_black = "EASY" if player_black.upper() == "BOT" and "easy" in file.lower() else (
                        "HARD" if player_black.upper() == "BOT" else player_black)

            label_red = "EASY" if player_red.upper() == "BOT" and "easy" in file.lower() else (
                        "HARD" if player_red.upper() == "BOT" else player_red)

            # Draw white box
            y_offset = top_margin + i * (box_height + vertical_gap)
            pygame.draw.rect(screen, (255, 255, 255), (70, y_offset, 460, box_height))

            # Black side (left)
            screen.blit(black_king_icon, (80, y_offset + 15))
            screen.blit(input_font.render(label_black, True, (0, 0, 0)), (80, y_offset + 75))

            # Red side (right)
            screen.blit(red_king_icon, (460, y_offset + 15))
            red_name_surface = input_font.render(label_red, True, (0, 0, 0))
            red_name_x = 520 - red_name_surface.get_width()
            screen.blit(red_name_surface, (red_name_x, y_offset + 75))

            # Center info
            winner = data["winner"]
            date = file.split("_")[0] + " " + file.split("_")[1].replace("-", ":")
            screen.blit(input_font.render(date, True, (0, 0, 0)), (230, y_offset + 10))
            screen.blit(input_font.render("Winner is:", True, (0, 0, 0)), (245, y_offset + 40))
            winner_font = pygame.font.SysFont("arial", 28, bold=True)
            screen.blit(winner_font.render(winner.upper(), True, (0, 0, 0)), (245, y_offset + 65))

            box_rect = pygame.Rect(70, y_offset, 460, box_height)
            if pygame.mouse.get_pressed()[0] and box_rect.collidepoint(pygame.mouse.get_pos()):
                with open(os.path.join("replays", file), "r") as f:
                    replay_data = json.load(f)
                # Determine if red should be on bottom or top
                is_2player = "BOT" not in [replay_data["player_black"].upper(), replay_data["player_red"].upper()]
                if is_2player:
                    replay_flip_board = False  # Red starts on top in 2p, flip to always black on bottom
                else:
                    # Bot match: flip if red was the player (BOT was black)
                    replay_flip_board = replay_data["player_red"].upper() == replay_data.get("player_name", "").upper()


                replay_index = 0
                last_replay_page = replay_page
                board = Board()
                load_replay_state_at(replay_index)
                board.turn = "black"  # default starting turn
                state = REPLAY_VIEWER
                pygame.time.wait(150)  # prevent double click spam

        # Arrows and Page Number
        if btn_replay_left.draw(screen):
            if replay_page > 0:
                replay_page -= 1

        if btn_replay_right.draw(screen):
            max_page = (len(replay_files) - 1) // 4
            if replay_page < max_page:
                replay_page += 1
        page_label = input_font.render(f"PAGE: [{replay_page + 1}]", True, (255, 200, 0))
        screen.blit(page_label, (240, 570))


    elif state == REPLAY_VIEWER:
        screen.blit(pygame.transform.scale(bg_img, (600, 600)), (0, 0))

        try:
            # draw current board
            board.draw(screen, game_mode="replay", flip_board=replay_flip_board)

        except Exception as e:
            print("[REPLAY ERROR]", e)
            state = MENU
            pygame.display.flip()
            continue

        # MENU (top-left)
        menu_label = input_font.render("MENU", True, (0, 0, 0))
        menu_rect = menu_label.get_rect(topleft=(10, 10))
        screen.blit(menu_label, menu_rect)
        if pygame.mouse.get_pressed()[0] and menu_rect.collidepoint(pygame.mouse.get_pos()):
            state = MENU
            pygame.display.flip()
            continue

        # BACK (top-right)
        back_label = input_font.render("BACK", True, (0, 0, 0))
        back_rect = back_label.get_rect(topright=(590, 10))
        screen.blit(back_label, back_rect)
        if pygame.mouse.get_pressed()[0] and back_rect.collidepoint(pygame.mouse.get_pos()):
            state = REPLAY_MENU
            replay_page = last_replay_page
            just_entered_history = True
            pygame.event.clear(pygame.MOUSEBUTTONDOWN)
            pygame.time.wait(100)
            pygame.display.flip()
            continue

        # Replay Step Arrows
        btn_step_back.rect.center = (270, 20)
        btn_step_forward.rect.center = (330, 20)

        btn_step_back.draw(screen)
        load_replay_state_at(replay_index)  # ✅ Update immediately

        btn_step_forward.draw(screen)
        load_replay_state_at(replay_index)  # ✅ Update immediately





    elif state == END:
        screen.blit(pygame.transform.scale(bg_img, (600, 600)), (0, 0))

        # Safely get winner name from recorder
        if recorder:
            winner_name = recorder.player_black if winner == "black" else recorder.player_red
        else:
            winner_name = winner.upper()

        # Render WINNER title and name
        winner_label = title_font.render("WINNER:", True, (0, 0, 0))
        winner_name_label = title_font.render(winner_name.upper(), True, (255, 0, 0))

        screen.blit(winner_label, ((600 - winner_label.get_width()) // 2, 180))
        screen.blit(winner_name_label, ((600 - winner_name_label.get_width()) // 2, 250))

        # Return to menu button
        pygame.draw.rect(screen, (0, 200, 0), (200, 350, 200, 50))
        menu_label = input_font.render("RETURN TO MENU", True, (255, 255, 255))
        screen.blit(menu_label, ((600 - menu_label.get_width()) // 2, 365))

        mx, my = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and 200 < mx < 400 and 350 < my < 400:
            state = MENU
            board = None
            winner = None
            game_mode = None
            selected_mode = None
            waiting_for_bot = False
            name_black = ""
            name_red = ""
            active_input = None
            replay_data = None
            recorder = None
            pygame.event.clear(pygame.MOUSEBUTTONDOWN)
            pygame.time.wait(100)




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
                        if target and target != last_selected:
                            recorder.record_state(board)
                            if game_mode == "2player":
                                pending_flip = True
                                flip_pause_timer = FLIP_PAUSE_MS
            elif state == REPLAY_VIEWER:
                if btn_step_forward.rect.collidepoint(event.pos):
                    current_turn = replay_data["states"][replay_index]["turn"]
                    while replay_index + 1 < len(replay_data["states"]):
                        replay_index += 1
                        if replay_data["states"][replay_index]["turn"] != current_turn:
                            break
                    load_replay_state_at(replay_index)

                elif btn_step_back.rect.collidepoint(event.pos):
                    current_turn = replay_data["states"][replay_index]["turn"]
                    while replay_index - 1 >= 0:
                        replay_index -= 1
                        if replay_data["states"][replay_index]["turn"] != current_turn:
                            break
                    load_replay_state_at(replay_index)


            elif state == NAME_INPUT:
                mx, my = pygame.mouse.get_pos()
                if game_mode == "2player":
                    if 150 < mx < 450 and 180 < my < 220:
                        active_input = "black"
                    elif 150 < mx < 450 and 300 < my < 340:
                        active_input = "red"
                    elif 200 < mx < 400 and 400 < my < 440:
                        if name_black.strip() and name_red.strip():
                            board = Board()
                            recorder = MatchRecorder()
                            recorder.set_players(name_black, name_red)
                            recorder.record_state(board)  # Save initial state
                            state = GAME
                else:
                    if 150 < mx < 450 and 200 < my < 240:
                        active_input = "black"

    pygame.display.flip()

pygame.quit()
sys.exit()