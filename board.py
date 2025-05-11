import pygame
import os
from piece import Piece

class Board:
    def __init__(self):
        self.rows = 8
        self.cols = 8
        self.square_size = 65
        self.offset = 40

        self.board_img = pygame.image.load(os.path.join("assets", "board.png"))
        self.move_circle = pygame.image.load(os.path.join("assets", "possible_move.png"))

        self.font = pygame.font.SysFont("arial", 20)
        self.selected_square = None
        self.valid_moves = []
        self.valid_jump_paths = []
        self.turn = "black"

        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self._place_pieces()


    def unflip_pos(self, pos, game_mode=None, player_color=None):
        row, col = self.pos_to_index(pos, flip_board=True)
        return self.index_to_pos(row, col)


    def pos_to_index(self, pos, flip_board=False):
        col = ord(pos[0].upper()) - ord('A')
        row = 8 - int(pos[1])
        if flip_board:
            row = 7 - row
            col = 7 - col
        return row, col


    def index_to_pos(self, row, col):
        return chr(col + ord('A')) + str(8 - row)

    def _place_pieces(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if (row + col) % 2 != 0:
                    if row < 3:
                        self.board[row][col] = Piece("red")
                    elif row > 4:
                        self.board[row][col] = Piece("black")

    def get_square_under_mouse(self, pos, game_mode=None, player_color=None):
        mx, my = pos
        col = (mx - self.offset) // self.square_size
        row = (my - self.offset) // self.square_size

        if (game_mode == "2player" and self.turn == "red") or (game_mode in ("easy", "hard") and player_color == "red"):
            row = 7 - row
            col = 7 - col

        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.index_to_pos(row, col)
        return None

    def handle_click(self, pos, game_mode=None, player_color=None):
        square = self.get_square_under_mouse(pos, game_mode, player_color)
        if square is None:
            return

        row, col = self.pos_to_index(square)
        piece = self.board[row][col]
        current_color = self.turn
        jumpables = self.get_all_jumpable_positions(current_color)

        if self.selected_square:
            if square in self.valid_moves:
                sel_row, sel_col = self.pos_to_index(self.selected_square)
                selected_piece = self.board[sel_row][sel_col]

                selected_path = None
                for chain in self.valid_jump_paths:
                    if chain["end"] == square:
                        selected_path = chain["path"]
                        break

                if selected_path:
                    r, c = sel_row, sel_col
                    for jump_r, jump_c in selected_path:
                        mid_r = (r + jump_r) // 2
                        mid_c = (c + jump_c) // 2
                        self.board[mid_r][mid_c] = None
                        self.board[jump_r][jump_c] = selected_piece
                        self.board[r][c] = None
                        r, c = jump_r, jump_c

                    if selected_piece.color == "red" and r == 7:
                        selected_piece.make_king()
                    elif selected_piece.color == "black" and r == 0:
                        selected_piece.make_king()

                    self.turn = "black" if self.turn == "red" else "red"

                else:
                    self.board[row][col] = selected_piece
                    self.board[sel_row][sel_col] = None

                    if selected_piece.color == "red" and row == 7:
                        selected_piece.make_king()
                    elif selected_piece.color == "black" and row == 0:
                        selected_piece.make_king()

                    self.turn = "black" if self.turn == "red" else "red"

                self.selected_square = None
                self.valid_moves = []
                self.valid_jump_paths = []

            elif piece and piece.color == current_color:
                if square in jumpables:
                    self.selected_square = square
                    self.valid_jump_paths = jumpables[square]
                    self.valid_moves = [chain["end"] for chain in self.valid_jump_paths]
                else:
                    self.selected_square = None
                    self.valid_moves = []
                    self.valid_jump_paths = []
            else:
                self.selected_square = None
                self.valid_moves = []
                self.valid_jump_paths = []

        else:
            if piece and piece.color == current_color:
                if square in jumpables:
                    self.selected_square = square
                    self.valid_jump_paths = jumpables[square]
                    self.valid_moves = [chain["end"] for chain in self.valid_jump_paths]
                elif not jumpables:
                    self.selected_square = square
                    self.valid_moves = self.get_valid_moves(square)
                    self.valid_jump_paths = []

    def get_all_jump_chains(self, square):
        row, col = self.pos_to_index(square)
        piece = self.board[row][col]
        chains = []

        def recurse(r, c, path, visited):
            found = False
            directions = [(1, -1), (1, 1)] if piece.color == "red" else [(-1, -1), (-1, 1)]
            if piece.is_king:
                directions += [(-d[0], -d[1]) for d in directions]

            for dr, dc in directions:
                mid_r, mid_c = r + dr, c + dc
                jump_r, jump_c = r + dr * 2, c + dc * 2
                if (0 <= jump_r < self.rows and 0 <= jump_c < self.cols and
                    (jump_r, jump_c) not in visited and
                    self.board[jump_r][jump_c] is None and
                    self.board[mid_r][mid_c] and
                    self.board[mid_r][mid_c].color != piece.color):
                    found = True
                    recurse(jump_r, jump_c, path + [(jump_r, jump_c)], visited | {(jump_r, jump_c)})

            if not found and path:
                end_pos = self.index_to_pos(path[-1][0], path[-1][1])
                chains.append({
                    "end": end_pos,
                    "path": path
                })

        recurse(row, col, [], set())
        return chains

    def get_all_jumpable_positions(self, color):
        options = {}
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    pos = self.index_to_pos(row, col)
                    chains = self.get_all_jump_chains(pos)
                    if chains:
                        options[pos] = chains
        return options

    def get_valid_moves(self, square):
        moves = []
        row, col = self.pos_to_index(square)
        piece = self.board[row][col]
        if not piece:
            return moves

        directions = [(1, -1), (1, 1)] if piece.color == "red" else [(-1, -1), (-1, 1)]
        if piece.is_king:
            directions += [(-d[0], -d[1]) for d in directions]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] is None:
                moves.append(self.index_to_pos(r, c))
        return moves

    def draw(self, screen, game_mode=None, flip_board=None, player_color=None):
        if flip_board is None:
            flip_board = (game_mode == '2player' and self.turn == 'red') or (game_mode in ("easy", "hard") and player_color == 'red')
        screen.blit(self.board_img, (0, 0))

        for i in range(self.rows):
            label = self.font.render(str(i+1) if flip_board else str(8 - i), True, (0, 0, 0))
            y = self.offset + i * self.square_size + self.square_size // 2 - label.get_height() // 2
            screen.blit(label, (10, y))
            #screen.blit(label, (600 - 25, y))

        for j in range(self.cols):
            label = self.font.render(chr(ord('H') - j) if flip_board else chr(ord('A') + j), True, (0, 0, 0))
            x = self.offset + j * self.square_size + self.square_size // 2 - label.get_width() // 2
            #screen.blit(label, (x, 10))
            screen.blit(label, (x, 600 - 25))

        if self.selected_square:
            row, col = self.pos_to_index(self.selected_square)
            if flip_board:
                row = 7 - row
                col = 7 - col
            x = self.offset + col * self.square_size
            y = self.offset + row * self.square_size
            pygame.draw.rect(screen, (255, 255, 0), (x, y, self.square_size, self.square_size), 3)

        for pos in self.valid_moves:
            row, col = self.pos_to_index(pos)
            if flip_board:
                row = 7 - row
                col = 7 - col
            x = self.offset + col * self.square_size + (self.square_size - self.move_circle.get_width()) // 2
            y = self.offset + row * self.square_size + (self.square_size - self.move_circle.get_height()) // 2
            screen.blit(self.move_circle, (x, y))

        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board[row][col]
                if piece:
                    draw_row = 7 - row if flip_board else row
                    draw_col = 7 - col if flip_board else col
                    x = self.offset + draw_col * self.square_size
                    y = self.offset + draw_row * self.square_size
                    piece.draw(screen, x, y)

    def check_win(self):
        red_left = black_left = 0
        red_moves = black_moves = 0

        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board[row][col]
                if piece:
                    pos = self.index_to_pos(row, col)
                    if piece.color == "red":
                        red_left += 1
                        if self.get_valid_moves(pos) or self.get_all_jump_chains(pos):
                            red_moves += 1
                    elif piece.color == "black":
                        black_left += 1
                        if self.get_valid_moves(pos) or self.get_all_jump_chains(pos):
                            black_moves += 1

        if red_left == 0 or red_moves == 0:
            return "black"
        elif black_left == 0 or black_moves == 0:
            return "red"
        return None
