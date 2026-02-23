import pygame
from platform import Platform
from player import Player
from obstacle import FallingObstacle, GroundSpike, FallingPlatform, TimedPlatform
from explosion import Explosion
from settings import GRAVITY, SCREEN_HEIGHT, SCREEN_WIDTH, FPS, COLOR_BG
from level_data import LEVELS
from ending import run_ending, reset_ending
from starting import StartScreen

# ———— 게임 상태 변수 ————
game_state         = "START"
stage              = 0
trap_fired         = False
player_in_trigger  = False
was_on_second_plat = False

# ———— 스프라이트 그룹 ————
platforms          = pygame.sprite.Group()
obstacles          = pygame.sprite.Group()
player_group       = pygame.sprite.GroupSingle()
effects            = pygame.sprite.Group()
falling_platforms  = pygame.sprite.Group()
timed_platforms    = pygame.sprite.Group()

def load_level(idx: int):
    conf = LEVELS[idx]
    platforms.empty()
    player_group.empty()
    falling_platforms.empty()
    timed_platforms.empty()

    for i, item in enumerate(conf["platforms"]):
        x, y, w, h = item[:4]
        color = image = None
        can_land = True
        for extra in item[4:]:
            if isinstance(extra, tuple):  color = extra
            elif isinstance(extra, str):  image = extra
            elif isinstance(extra, bool): can_land = extra

        # Stage 3의 5번째 발판(i==4)을 TimedPlatform으로
        if idx == 2 and i == 4:
            timed_platforms.add(TimedPlatform(x, y, w, h))
        else:
            platforms.add(Platform(x, y, w, h, color, image, can_land))

    for item in conf.get("falling_platforms", []):
        x, y, w, h = item
        falling_platforms.add(FallingPlatform(x, y, w, h))

    player = Player(*conf["player_start"])
    player_group.add(player)
    return player

def restart_level():
    global player, trap_fired, player_in_trigger, was_on_second_plat
    player = load_level(stage)
    obstacles.empty()
    effects.empty()
    trap_fired = False
    player_in_trigger = False
    was_on_second_plat = False

def start_game():
    global stage, game_state
    stage = 0
    restart_level()
    game_state = "PLAY"

# ———— 초기화 ————
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level Devil Clone")
clock = pygame.time.Clock()
start_screen = StartScreen(screen)

# ———— 메인 루프 ————
running = True
while running:
    if game_state == "START":
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif (res := start_screen.handle_event(e)) in ("PLAY","QUIT"):
                if res == "PLAY": start_game()
                else:            running = False

        start_screen.update()
        start_screen.draw()
        pygame.display.flip()
        clock.tick(FPS)
        continue

    # 플레이 중 이벤트 처리
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if pygame.Rect(20, 20, 140, 40).collidepoint(e.pos):
                restart_level()
            elif pygame.Rect(180, 20, 140, 40).collidepoint(e.pos):
                game_state = "START"

    # 배경 채우기
    screen.fill(COLOR_BG)

    # ── Stage 3: 바닥 시각용 ‘눈속임’ 추가 ──
    if stage == 2:
        ground_y      = SCREEN_HEIGHT - 80    # 900 - 80 = 820
        ground_height = 80
        pygame.draw.rect(
            screen,
            Platform.DEFAULT_COLOR,
            pygame.Rect(0, ground_y, SCREEN_WIDTH, ground_height)
        )

    keys = pygame.key.get_pressed()
    visible_timed = [tp for tp in timed_platforms if tp.visible]
    player.update(keys, platforms.sprites() + visible_timed)

    # ── Stage 3: 2번째 발판에서 점프할 때만 TimedPlatform 트리거 ──
    if stage == 2 and timed_platforms:
        second_rect = pygame.Rect(600, 580, 150, 30)
        if second_rect.colliderect(player.rect):
            was_on_second_plat = True
        elif was_on_second_plat and (keys[pygame.K_SPACE] or keys[pygame.K_w]):
            for tp in timed_platforms:
                if not tp.triggered:
                    tp.trigger()
            was_on_second_plat = False

    # ── Stage 3: 특정 발판 교체 ──
    if stage == 2:
        for plat in list(platforms):
            if plat.rect.topleft == (300, 700) and plat.rect.size == (150, 30):
                if plat.rect.colliderect(player.rect):
                    platforms.remove(plat)
                    platforms.add(Platform(375, 700, 75, 30))

    # 레벨 설정 불러오기
    if game_state != "ENDING":
        conf = LEVELS[stage]

    # 낙하물 트랩
    if not trap_fired and conf.get("trap_type") == "fall":
        px, py, pw, ph = conf["trap_platform"]
        plat_rect = pygame.Rect(px, py, pw, ph)
        if (player.rect.bottom == plat_rect.top
            and plat_rect.left <= player.rect.centerx <= plat_rect.right):
            spawn_x = conf.get("trap_spawn_x",
                               player.rect.centerx + conf.get("trap_x_offset",50))
            obstacles.add(FallingObstacle(
                spawn_x,
                conf["trap_spawn_y"],
                conf["trap_width"],
                conf["trap_height"],
                None, "bomb.png"
            ))
            trap_fired = True

    # 땅 스파이크 트랩
    trig = conf.get("spike_trigger_rect")
    if trig:
        rect = pygame.Rect(*trig)
        if player.rect.colliderect(rect):
            if not player_in_trigger:
                obstacles.add(GroundSpike(
                    conf["spike_spawn_x"],
                    conf["spike_ground_y"]
                ))
            player_in_trigger = True
        else:
            player_in_trigger = False

    # 구덩이 트랩
    pit = conf.get("pitfall_trigger_rect")
    if pit:
        pit_rect = pygame.Rect(*pit)
        if player.rect.colliderect(pit_rect):
            for plat in list(platforms):
                if plat.rect.colliderect(pit_rect):
                    platforms.remove(plat)
            effects.add(Explosion(player.rect.center, 96))
            restart_level()

    # 기타 업데이트
    for fp in falling_platforms: fp.update(player)
    for tp in timed_platforms:   tp.update()
    obstacles.update()
    effects.update()

    # 충돌 처리
    hits = pygame.sprite.spritecollide(player, obstacles, False)
    for ob in hits:
        effects.add(Explosion(player.rect.center, 96))
        if isinstance(ob, GroundSpike) and stage in (0,1):
            restart_level(); break
        else:
            ob.kill(); restart_level(); break

    # 화면 밖 떨어짐
    if player.rect.top > SCREEN_HEIGHT:
        effects.add(Explosion(player.rect.center, 96))
        restart_level()

    # 레벨 클리어 / 엔딩 진입
    if player.rect.right >= SCREEN_WIDTH:
        if stage == len(LEVELS) - 1:
            reset_ending()
            game_state = "ENDING"
        else:
            stage += 1
            restart_level()
        continue

    # 엔딩 화면
    if game_state == "ENDING":
        run_ending(screen)
        pygame.display.flip()
        clock.tick(FPS)
        continue

    # — 렌더링 —
    platforms.draw(screen)
    falling_platforms.draw(screen)
    for tp in timed_platforms:
        if tp.visible:
            screen.blit(tp.image, tp.rect)
    obstacles.draw(screen)
    effects.draw(screen)
    player_group.draw(screen)

    # UI 버튼
    pygame.draw.rect(screen, (40,40,40), pygame.Rect(20,20,140,40), border_radius=6)
    screen.blit(
        pygame.font.SysFont(None,24).render("RESTART",True,(255,255,255)),
        (35,30)
    )
    pygame.draw.rect(screen, (40,40,40), pygame.Rect(180,20,140,40), border_radius=6)
    screen.blit(
        pygame.font.SysFont(None,24).render("HOME",True,(255,255,255)),
        (215,30)
    )

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
