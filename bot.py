import random
from piece import Piece

def evaluate_board(board):
    red_score = 0
    black_score = 0
    for row in board.board:
        for piece in row:
            if piece:
                value = 3 if piece.is_king else 1
                if piece.color == "red":
                    red_score += value
                else:
                    black_score += value
    return black_score - red_score

def get_all_moves(board, color):
    moves = []
    jumpables = board.get_all_jumpable_positions(color)
    if jumpables:
        for start_pos, chains in jumpables.items():
            for chain in chains:
                moves.append((start_pos, chain["path"]))
        return moves, True
    else:
        for row in range(board.rows):
            for col in range(board.cols):
                piece = board.board[row][col]
                if piece and piece.color == color:
                    start_pos = board.index_to_pos(row, col)
                    for end_pos in board.get_valid_moves(start_pos):
                        moves.append((start_pos, [board.pos_to_index(end_pos)]))
        return moves, False

def simulate_move(original_board, start_pos, path, color):
    from_pos = original_board.pos_to_index(start_pos)
    selected_piece = original_board.board[from_pos[0]][from_pos[1]]

    class MockBoard:
        pass
    board = MockBoard()
    board.rows = original_board.rows
    board.cols = original_board.cols
    board.board = [[piece and Piece(piece.color, piece.is_king) for piece in row] for row in original_board.board]
    board.pos_to_index = original_board.pos_to_index
    board.index_to_pos = original_board.index_to_pos
    board.get_valid_moves = original_board.get_valid_moves
    board.get_all_jump_chains = original_board.get_all_jump_chains
    board.get_all_jumpable_positions = original_board.get_all_jumpable_positions
    board.check_win = original_board.check_win
    board.turn = "red" if color == "black" else "black"

    r, c = from_pos
    for move_r, move_c in path:
        mid_r = (r + move_r) // 2
        mid_c = (c + move_c) // 2
        if abs(move_r - r) == 2:
            board.board[mid_r][mid_c] = None
        board.board[move_r][move_c] = board.board[r][c]
        board.board[r][c] = None
        r, c = move_r, move_c

    piece = board.board[r][c]
    if piece.color == "red" and r == 7:
        piece.make_king()
    elif piece.color == "black" and r == 0:
        piece.make_king()

    return board

def minimax(board, depth, maximizing, color):
    if depth == 0 or board.check_win():
        return evaluate_board(board), None

    all_moves, _ = get_all_moves(board, color)
    best_move = None

    if maximizing:
        max_eval = float('-inf')
        for move in all_moves:
            temp_board = simulate_move(board, move[0], move[1], color)
            eval, _ = minimax(temp_board, depth - 1, False, "red" if color == "black" else "black")
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in all_moves:
            temp_board = simulate_move(board, move[0], move[1], color)
            eval, _ = minimax(temp_board, depth - 1, True, "red" if color == "black" else "black")
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move

def make_bot_move(board, difficulty):
    depth = 2 if difficulty == "easy" else 5
    _, best_move = minimax(board, depth, True, board.turn)
    if best_move:
        board.selected_square = best_move[0]
        board.valid_jump_paths = [{"end": board.index_to_pos(*best_move[1][-1]), "path": best_move[1]}]
        board.valid_moves = [board.index_to_pos(*best_move[1][-1])]

        # Convert move target to pixel coordinates for handle_click
        end_square = board.valid_moves[0]
        row, col = board.pos_to_index(end_square)
        x = board.offset + col * board.square_size + board.square_size // 2
        y = board.offset + row * board.square_size + board.square_size // 2
        board.handle_click((x, y))
