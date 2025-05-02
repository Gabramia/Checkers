import pygame
import os

class Piece:
    red_piece_img = pygame.image.load(os.path.join("assets", "red_piece.png"))
    black_piece_img = pygame.image.load(os.path.join("assets", "black_piece.png"))
    red_king_img = pygame.image.load(os.path.join("assets", "red_king.png"))
    black_king_img = pygame.image.load(os.path.join("assets", "black_king.png"))

    def __init__(self, color, is_king=False):
        self.color = color
        self.is_king = is_king

    def make_king(self):
        self.is_king = True

    def get_image(self):
        if self.color == "red":
            return self.red_king_img if self.is_king else self.red_piece_img
        else:
            return self.black_king_img if self.is_king else self.black_piece_img

    def draw(self, screen, x, y):
        img = self.get_image()
        offset_x = (65 - img.get_width()) // 2
        offset_y = (65 - img.get_height()) // 2
        screen.blit(img, (x + offset_x, y + offset_y))

    def __repr__(self):
        return f"{'K' if self.is_king else 'P'}-{self.color}"
