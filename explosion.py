# explosion.py
import pygame, pathlib
from settings import FPS

ASSETS = pathlib.Path(__file__).parent / "assets"

class Explosion(pygame.sprite.Sprite):
    """0.3초 동안만 화면에 나타나는 폭발 이펙트"""
    def __init__(self, pos, size=128):
        super().__init__()
        img = pygame.image.load(ASSETS / "explosion.png").convert_alpha()
        img = pygame.transform.scale(img, (size, size))
        self.image = img
        self.rect  = self.image.get_rect(center=pos)
        self.timer = int(0.3 * FPS)     # 0.3초간 유지

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()                # 자동 소멸
