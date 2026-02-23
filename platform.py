# platform.py
import pygame
import pathlib
from settings import *

ASSETS = pathlib.Path(__file__).parent / "assets"

class Platform(pygame.sprite.Sprite):
    """사각형 플랫폼.

    Args:
        x, y, w, h: 위치·크기(px)
        color:      (R,G,B) 값. 색·이미지 둘 중 하나만 쓰면 됨.
        image:      이미지 파일 이름 또는 Path. 지정하면 그 이미지를 타일 크기에 맞춰 넣음.
        can_land:   플레이어가 위에 설 수 있는지 여부.
    """

    DEFAULT_COLOR = (0, 255, 0)

    def __init__(self, x: int, y: int, w: int, h: int,
                 color: tuple | None = None,
                 image: str | pathlib.Path | None = None,
                 can_land: bool = True):
        super().__init__()

        # 표면 생성
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        if image:
            img_path = (ASSETS / image) if isinstance(image, str) else pathlib.Path(image)
            tex = pygame.image.load(img_path).convert_alpha()
            tex = pygame.transform.scale(tex, (w, h))
            self.image.blit(tex, (0, 0))
        else:
            self.image.fill(color or self.DEFAULT_COLOR)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.can_land = can_land

        # ✅ 사라지는 플랫폼용 visible 속성 추가 (기본값은 True)
        self.visible = True
