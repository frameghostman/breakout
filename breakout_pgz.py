import pgzrun

WIDTH = 800
HEIGHT = 600
TITLE = "brickbreaker"
barrect = Rect(400,500,100,20)
ballrect = Rect(400,450,10,10)
vx = 8
vy = -8
blocks = []
for yy in range(4):
	for xx in range(7):
		blocks.append(Rect(50 + xx*100, 40 + yy*50, 80, 30))
page = "play"
score = 0

def gamestage():
    global vx, vy
    global page
    global score
    screen.clear()
    screen.draw.filled_rect(barrect, "CYAN")
    if ballrect.y < 0:
        vy = -vy
    if ballrect.x < 0 or 800 - 10 < ballrect.x:
        vx = -vx
    if barrect.colliderect(ballrect):
        vy = -vy
    if ballrect.y > 600:
        page = "gameover"
    ballrect.x += vx
    ballrect.y += vy
    screen.draw.filled_circle((ballrect.x, ballrect.y), ballrect.w, "CYAN")
    n = 0
    for block in blocks:
        screen.draw.filled_rect(block,"GOLD")
        if block.colliderect(ballrect):
            vy = -vy
            blocks[n] = Rect(0, 0, 0, 0)
            score += 1
            if score >= 28:
                page = "gameclear"
        n += 1

def gameover():
    screen.clear()
    screen.draw.text("GAME OVER", (100, 200), color = 'RED', fontsize=150)

def gameclear():
    screen.clear()
    screen.draw.text("GAME CLEAR", (60, 200), color = 'GOLD', fontsize=150)

def on_mouse_move(pos):
    x, y = pos
    barrect.x = x - 50

def update():
    global page
    if page == 'play':
        gamestage()
    elif page == 'gameover':
        gameover()
    else:
        gameclear()

pgzrun.go()