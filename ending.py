# ending.py
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

pygame.font.init()
font_big = pygame.font.SysFont(None, 72)
font_small = pygame.font.SysFont(None, 36)

credits = [
    "Thanks for playing!",
    "",
    "Made by: SAMSUNGKIM",
    "Music: SAMSUNGKIM",
    "Sound Effects: SAMSUNGKIM",
    "Art: SAMSUNGKIM",
    "",
    "See you next time!"
]

ending_timer = 0  # 내부 상태 유지용

def run_ending(screen):
    global ending_timer
    screen.fill((0, 0, 0))
    ending_timer += 1

    # ─ "CLEAR!" 문구 (3초간) ─
    if ending_timer < 180:
        clear_text = font_big.render("CLEAR!", True, (255, 255, 0))
        screen.blit(clear_text, clear_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

    # ─ 크레딧 올라가기 ─
    start_y = SCREEN_HEIGHT + 300 - ending_timer
    for i, line in enumerate(credits):
        text = font_small.render(line, True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, start_y + i * 40))

def reset_ending():
    global ending_timer
    ending_timer = 0
