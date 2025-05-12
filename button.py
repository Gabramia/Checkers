import pygame
import os

class Button:
    def __init__(self, name, pos):
        self.name = name
        self.images = {
            "normal": pygame.image.load(os.path.join("assets", f"btn_{name}.png")),
            "hover": pygame.image.load(os.path.join("assets", f"btn_{name}_hover.png")),
            "press": pygame.image.load(os.path.join("assets", f"btn_{name}_press.png")),
        }
        self.image = self.images["normal"]
        self.rect = self.image.get_rect(center=pos)
        self.clicked = False
        

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse):
            if click:
                self.image = self.images["press"]
                self.clicked = True
            else:
                if self.clicked:
                    self.clicked = False
                    return True
                self.image = self.images["hover"]
        else:
            self.image = self.images["normal"]

        screen.blit(self.image, self.rect)
        return False
