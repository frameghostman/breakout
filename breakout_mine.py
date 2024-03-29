import pygame
import sys

# 初期化
pygame.init()
score = 0
lives = 3  # 残機の初期値

# 画面サイズ
WIDTH, HEIGHT = 600, 400

# 色の定義
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# ゲームウィンドウの作成
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# パドルサイズ
PADDLE_WIDTH, PADDLE_HEIGHT = 200, 10

# パドル位置
paddle_x = (WIDTH - PADDLE_WIDTH) // 2
paddle_y = HEIGHT - 50

# ボールサイズ
BALL_RADIUS = 30
ball_speed_x = 5
ball_speed_y = 5

# ボール位置
BALL_RADIUS = 20
ball_x = (WIDTH - BALL_RADIUS) // 2
ball_y = HEIGHT - 80

# ブロック設定
BLOCK_WIDTH, BLOCK_HEIGHT, BLOCK_SPACE = 45, 20, 5
block_colors = ["RED", "GOLD", "ORANGE", "PINK"]
block_rows = 4
block_cols = 12
blocks = []

# ゲーム状態
page = "title"

# initialize
def gameinit():
    global paddle_x, paddle_y, ball_x, ball_y, score, lives

    # スコア初期化
    score = 0

    # 残機の初期値
    if lives <= 0:
        lives = 3

    # ボール位置
    BALL_RADIUS = 20
    ball_x = (WIDTH - BALL_RADIUS) // 2
    ball_y = HEIGHT - 80

    # パドル位置
    paddle_x = (WIDTH - PADDLE_WIDTH) // 2
    paddle_y = HEIGHT - 50

    # ブロック配列
    blocks.clear()
    for row in range(block_rows):
        for col in range(block_cols):
            block = [pygame.Rect(col * (BLOCK_SPACE + BLOCK_WIDTH), row * (BLOCK_SPACE + BLOCK_HEIGHT), BLOCK_WIDTH, BLOCK_HEIGHT), block_colors[row]]
            blocks.append(block)

# title
def title():
    global page
    screen.fill(pygame.Color("BLACK"))
    font = pygame.font.Font(None, 50)
    text = font.render("PRESS SPACE TO START", True, pygame.Color("WHITE"))
    screen.blit(text, (100, 100))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        page = "main"

def gamestage():
    global score, page, paddle_x, paddle_y, ball_x, ball_y, ball_speed_x, ball_speed_y, lives

    # パドル操作
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] and paddle_x < WIDTH - PADDLE_WIDTH:
        paddle_x += 5
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= 5
    
    # ボールの移動
    ball_x -= ball_speed_x
    ball_y -= ball_speed_y

    # 壁との衝突判定
    if ball_x - BALL_RADIUS < 0 or ball_x + BALL_RADIUS > WIDTH:
        ball_speed_x = -ball_speed_x
    if ball_y - BALL_RADIUS < 0 or ball_y + BALL_RADIUS > HEIGHT:
        ball_speed_y = -ball_speed_y

    # パドルとの衝突判定
    if (
        paddle_x < ball_x < paddle_x + PADDLE_WIDTH
        and paddle_y < ball_y + BALL_RADIUS < paddle_y + PADDLE_HEIGHT
    ):
        ball_speed_y = -ball_speed_y

    # ブロックとの衝突判定 colliderect
    for block in blocks:
        if block[0].colliderect(pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, 2*BALL_RADIUS, 2*BALL_RADIUS)):
            blocks.remove(block)
            ball_speed_y = -ball_speed_y
            score += 1

    # ゲームオーバー判定
    if ball_y + BALL_RADIUS > HEIGHT:
        lives -= 1
        if lives <= 0:
            page = "gameover"
        else:
            gameinit()  # リトライ

    # 画面描画
    screen.fill(pygame.Color("NAVY"))
    pygame.draw.rect(screen, pygame.Color("CYAN"), (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, pygame.Color("CYAN"), (ball_x, ball_y), BALL_RADIUS)
    font = pygame.font.Font(None, 30)
    text = font.render("SCORE: " + str(score) + "   LIVES: " + str(lives), True, pygame.Color("RED"))
    screen.blit(text, (10, 250))

    for block in blocks:
        pygame.draw.rect(screen, block[1], block[0])

# game over
def gameover():
    global score, page, lives
    screen.fill(pygame.Color("NAVY"))
    font = pygame.font.Font(None, 100)
    text = font.render("GAME OVER", True, pygame.Color("RED"))
    screen.blit(text, (100, 100))
    font = pygame.font.Font(None, 50)
    text = font.render("YOUR SCORE IS " + str(score), True, pygame.Color("GOLD"))
    screen.blit(text, (100, 200))
    font = pygame.font.Font(None, 50)
    text = font.render("PRESS SPACE TO RETRY", True, pygame.Color("RED"))
    screen.blit(text, (100, 300))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        gameinit()
        page = "main"

def gameclear():
    global page
    screen.fill(pygame.Color("BLACK"))
    font = pygame.font.Font(None, 50)
    text = font.render("CONGRATULATIONS!", True, pygame.Color("WHITE"))
    screen.blit(text, (100, 100))
    font = pygame.font.Font(None, 50)
    text = font.render("YOU CLEARED THE GAME", True, pygame.Color("WHITE"))
    screen.blit(text, (100, 150))
    text = font.render("PRESS SPACE TO RESTART", True, pygame.Color("WHITE"))
    screen.blit(text, (100, 200))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        gameinit()
        page = "main"

# ゲームループ
gameinit()
while True:
    # フレームレート設定
    pygame.time.Clock().tick(60)

    if page == "title":
        title()
    elif page == "gameover":
        gameover()
    elif len(blocks) == 0:  # ブロックがなくなったらゲームクリア
        gameclear()
    else:
        gamestage()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
