import pygame
import sys
import random

# 初期化
pygame.init()

# 画面サイズ
WIDTH, HEIGHT = 600, 400

# 色の定義
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# パドルの設定
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 10
paddle_x = (WIDTH - PADDLE_WIDTH) // 2
paddle_y = HEIGHT - 20

# ボールの設定
BALL_RADIUS = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = 5
ball_speed_y = 5

# ブロックの設定
BLOCK_WIDTH, BLOCK_HEIGHT = 50, 20
block_rows = 4
block_cols = 12
blocks = []

for row in range(block_rows):
    for col in range(block_cols):
        block = pygame.Rect(col * BLOCK_WIDTH, row * BLOCK_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT)
        blocks.append(block)

# ゲームウィンドウの作成
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ブロック崩しゲーム")

# ゲームの状態管理
game_started = False

# ゲームループ
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_started = True

    if game_started:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= 5
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - PADDLE_WIDTH:
            paddle_x += 5

        # ボールの移動
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # 壁との衝突判定
        if ball_x - BALL_RADIUS < 0 or ball_x + BALL_RADIUS > WIDTH:
            ball_speed_x = -ball_speed_x

        if ball_y - BALL_RADIUS < 0:
            ball_speed_y = -ball_speed_y

        # パドルとの衝突判定
        if (
            paddle_x < ball_x < paddle_x + PADDLE_WIDTH
            and paddle_y < ball_y < paddle_y + PADDLE_HEIGHT
        ):
            ball_speed_y = -ball_speed_y

        # ブロックとの衝突判定
        for block in blocks:
            if block.colliderect(pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, 2 * BALL_RADIUS, 2 * BALL_RADIUS)):
                blocks.remove(block)
                ball_speed_y = -ball_speed_y

        # 画面描画
        screen.fill(WHITE)
        pygame.draw.rect(screen, RED, (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.circle(screen, BLUE, (ball_x, ball_y), BALL_RADIUS)

        for block in blocks:
            pygame.draw.rect(screen, RED, block)

    else:
        # ゲームが開始していない場合の表示
        font = pygame.font.Font(None, 36)
        text = font.render("Press SPACE to start", True, RED)
        screen.blit(text, (WIDTH // 4, HEIGHT // 2))

    pygame.display.flip()

    # フレームレート設定
    pygame.time.Clock().tick(60)
