import os
import json
from datetime import datetime

class MatchRecorder:
    def __init__(self):
        self.moves = []
        self.player_black = None
        self.player_red = None
        self.winner = None

    def set_players(self, black, red):
        self.player_black = black
        self.player_red = red

    def record_move(self, start_pos, end_pos):
        move = f"{start_pos}-{end_pos}"
        if not self.moves or self.moves[-1] != move:
            self.moves.append(move)


    def set_winner(self, winner_color):
        self.winner = winner_color

    def save_to_file(self):
        if not os.path.exists("replays"):
            os.makedirs("replays")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"replays/{timestamp}_{self.player_black}_vs_{self.player_red}.json"

        data = {
            "player_black": self.player_black,
            "player_red": self.player_red,
            "moves": self.moves,
            "winner": self.winner
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"[Recorder] Saved replay to {filename}")
