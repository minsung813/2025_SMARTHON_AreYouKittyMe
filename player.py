# player.py
import pygame
import pathlib
from settings import *

# ─ assets 폴더 경로 ─
ASSETS = pathlib.Path(__file__).parent / "assets"

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # ─ 이미지 로드 및 크기 통일 (100x80) ─
        idle_img     = pygame.image.load(ASSETS / "cat_idle.png").convert_alpha()
        walk_l_img1  = pygame.image.load(ASSETS / "cat_walk_L.png").convert_alpha()
        walk_l_img2  = pygame.image.load(ASSETS / "cat_walk_L2.png").convert_alpha()
        walk_r_img1  = pygame.image.load(ASSETS / "cat_walk_R.png").convert_alpha()
        walk_r_img2  = pygame.image.load(ASSETS / "cat_walk_R2.png").convert_alpha()

        self.idle_img    = pygame.transform.scale(idle_img, (100, 80))
        self.walk_l_imgs = [
            pygame.transform.scale(walk_l_img1, (100, 80)),
            pygame.transform.scale(walk_l_img2, (100, 80))
        ]
        self.walk_r_imgs = [
            pygame.transform.scale(walk_r_img1, (100, 80)),
            pygame.transform.scale(walk_r_img2, (100, 80))
        ]

        self.image = self.idle_img
        self.rect = self.image.get_rect(topleft=(x, y))

        # ─ 상태값 초기화 ─
        self.vel_y = 0
        self.jumping = False
        self.walk_frame = 0
        self.walk_timer = 0

    def update(self, keys, platforms):
        dx = 0

        # ─ 이동 및 점프 입력 처리 ─
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += PLAYER_SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and not self.jumping:
            self.vel_y = PLAYER_JUMP_POWER
            self.jumping = True

        # ─ 중력 적용 ─
        self.vel_y += GRAVITY
        dy = self.vel_y

        self.rect.x += dx
        self.rect.y += dy

        # ─ 플랫폼 충돌 처리 ─
        for platform in platforms:
            if not getattr(platform, "can_land", True):
                continue
            # ✅ TimedPlatform의 visible 체크 추가
            if hasattr(platform, "visible") and not platform.visible:
                continue
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.jumping = False
                self.vel_y = 0


        # ─ 화면 경계 제한 ─
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.top > SCREEN_HEIGHT:
            print("게임 오버! 바닥 밑으로 떨어짐.")

        # ─ 애니메이션 처리 ─
        if dx == 0:
            self.image = self.idle_img
        else:
            self.walk_timer += 1
            if self.walk_timer >= 6:
                self.walk_timer = 0
                self.walk_frame = (self.walk_frame + 1) % 2

            if dx < 0:
                self.image = self.walk_l_imgs[self.walk_frame]
            else:
                self.image = self.walk_r_imgs[self.walk_frame]
