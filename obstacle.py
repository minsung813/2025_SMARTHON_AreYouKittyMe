import pygame, pathlib
from settings import GRAVITY, SCREEN_HEIGHT, FPS
from platform import Platform

ASSETS = pathlib.Path(__file__).parent / "assets"

class FallingObstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w=60, h=60, color=None, image=None):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        # ─ 이미지 or 단색 ─
        if image:
            img_path = pathlib.Path(image)
            if not img_path.is_absolute():          # 상대경로면 assets에 붙이기
                img_path = ASSETS / img_path

            tex = pygame.image.load(img_path).convert_alpha()
            tex = pygame.transform.scale(tex, (w, h))
            self.image.blit(tex, (0, 0))
        else:
            self.image.fill(color or (200, 30, 30))

        self.rect  = self.image.get_rect(center=(x, y))
        self.vel_y = 0

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class GroundSpike(pygame.sprite.Sprite):
    def __init__(self, x, ground_y,
                 rise_px=60, rise_speed=8, wait_sec=1.2):

        super().__init__()

        # ── 1) 전체 이미지 불러오기 ───────────────
        full_img = pygame.image.load(ASSETS / "snake.png").convert_alpha()

        # ── 2) 필요하면 크기 조정 ───────────────
        #  예: 가로 60px 고정, 세로 비율 유지
        target_w = 60
        scale = target_w / full_img.get_width()
        full_img = pygame.transform.smoothscale(
            full_img,
            (target_w, int(full_img.get_height() * scale))
        )

        self.full = full_img           # 원본 전체 Surface 보관
        self.crop_h = 2                # 처음엔 2px만 보여 주기
        self.image = self.full.subsurface(
            pygame.Rect(0,
                        self.full.get_height() - self.crop_h,
                        self.full.get_width(),
                        self.crop_h)
        )

        self.rect = self.image.get_rect(midbottom=(x, ground_y))
        self.target_y = ground_y - rise_px
        self.speed    = rise_speed
        self.state    = "rising"
        self.wait     = int(wait_sec * FPS)

    def _refresh_crop(self):
        h = self.full.get_height()
        self.image = self.full.subsurface(
            pygame.Rect(0, h - self.crop_h, self.full.get_width(), self.crop_h)
        )

    def update(self):
        if self.state == "rising":
            step = min(self.speed, self.rect.y - self.target_y)
            self.rect.y  -= step
            self.crop_h  += step
            self._refresh_crop()
            if self.rect.y <= self.target_y:
                self.state = "waiting"

        elif self.state == "waiting":
            self.wait -= 1
            if self.wait <= 0:
                self.kill()

class FallingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=(0, 255, 0)):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.falling = False
        self.speed = 5

    def update(self, player):
        # 밟으면 낙하 시작
        if not self.falling and self.rect.colliderect(player.rect):
            if player.rect.bottom <= self.rect.top + 10:
                self.falling = True
        if self.falling:
            self.rect.y += self.speed

class TimedPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=None):
        super().__init__()
        self.base_image = pygame.Surface((w, h), pygame.SRCALPHA)
        color = color or Platform.DEFAULT_COLOR # ✅ 수정 완료
        self.base_image.fill(color)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

        self.timer = 0
        self.triggered = False
        self.visible = True
        self.can_land = True
        self.alpha = 255

    def trigger(self):
        self.triggered = True
        self.timer = 0

    def update(self):
        if not self.triggered:
            return

        self.timer += 1
        t = self.timer % int(FPS * 6)

        if t < FPS * 2:       self.visible = False
        elif t < FPS * 3:   self.visible = True
        elif t < FPS * 4:   self.visible = False
        else:                 self.visible = True

        if self.visible and self.alpha < 255:
            self.alpha += 15
            if self.alpha > 255: self.alpha = 255
        elif not self.visible and self.alpha > 0:
            self.alpha -= 15
            if self.alpha < 0: self.alpha = 0

        # ★ 이 부분이 꼭 필요함!
        self.image.set_alpha(self.alpha)


