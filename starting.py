# starting.py

import pygame
import random
from player import Player
from platform import Platform
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_BTN_BG, COLOR_BTN_HOVER, COLOR_BTN_TEXT


class StartScreen:
    def __init__(self, screen):
        self.screen = screen

        # 텍스트
        self.font_big = pygame.font.SysFont(None, 48)
        self.font_title = pygame.font.SysFont(None, 160)
        self.title_text = "Are you kitty me?"
        self.title_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 220]
        self.title_target = self.title_pos.copy()

        # 버튼
        self.PLY_W, self.PLY_H = 220, 80
        self.PLY_X = (SCREEN_WIDTH - self.PLY_W) // 2 + 50
        self.PLY_Y = (SCREEN_HEIGHT - self.PLY_H) // 2 + 80
        self.rect_play = pygame.Rect(self.PLY_X, self.PLY_Y, self.PLY_W, self.PLY_H)
        self.rect_quit = pygame.Rect(self.PLY_X + self.PLY_W + 40, self.PLY_Y, self.PLY_W, self.PLY_H)
        self.label_play = self.font_big.render("PLAY", True, COLOR_BTN_TEXT)
        self.label_quit = self.font_big.render("QUIT", True, COLOR_BTN_TEXT)

        # 고양이
        self.cat_flipped = False
        self.cat = Player(300, 740)
        self.cat_group = pygame.sprite.GroupSingle(self.cat)

        # 플랫폼
        self.platform = Platform(0, 820, 1600, 80, (0, 255, 0))
        self.platform_group = pygame.sprite.Group(self.platform)

    def is_hovered(self, rect):
        return rect.collidepoint(pygame.mouse.get_pos())

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect_play.collidepoint(event.pos):
                return "PLAY"
            elif self.rect_quit.collidepoint(event.pos):
                return "QUIT"
        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()

        # 타이틀 도망 효과
        if self.font_title.render(self.title_text, True, (0, 0, 0)).get_rect(center=self.title_pos).collidepoint(mouse_pos):
            self.title_target = [
                random.randint(200, SCREEN_WIDTH - 200),
                random.randint(100, SCREEN_HEIGHT // 2)
            ]
        self.title_pos[0] += (self.title_target[0] - self.title_pos[0]) * 0.12
        self.title_pos[1] += (self.title_target[1] - self.title_pos[1]) * 0.12

        # 고양이 뒤집기
        if self.cat.rect.collidepoint(mouse_pos):
            if not self.cat_flipped:
                self.cat.image = pygame.transform.flip(self.cat.image, False, True)
                self.cat_flipped = True
        else:
            if self.cat_flipped:
                self.cat.image = pygame.transform.flip(self.cat.image, False, True)
                self.cat_flipped = False

    def draw(self):
        self.screen.fill(COLOR_BG)
        self.platform_group.draw(self.screen)
        self.cat_group.draw(self.screen)

        # 타이틀 그리기
        label_title = self.font_title.render(self.title_text, True, (0, 0, 0))
        title_rect = label_title.get_rect(center=self.title_pos)
        self.screen.blit(label_title, title_rect)

        # 버튼 그리기
        for rect, label in [(self.rect_play, self.label_play), (self.rect_quit, self.label_quit)]:
            color = COLOR_BTN_HOVER if self.is_hovered(rect) else COLOR_BTN_BG
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            self.screen.blit(label, label.get_rect(center=rect.center))
