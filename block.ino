#include <TFT_eSPI.h>

TFT_eSPI tft;
TFT_eSprite spr = TFT_eSprite(&tft); // バッファ

// パドルの定義
#define PADDLE_WIDTH 40
#define PADDLE_HEIGHT 10
int paddleX = 150;
int paddleY = 200;

// ボールの定義
#define BALL_RADIUS 10
int ballX = 120;
int ballY = 120;
int ball_speed_X = 5;
int ball_speed_Y = 5;

// ブロックの定義
#define BLOCK_WIDTH 32
#define BLOCK_HEIGHT 10
#define BLOCK_COLS 10
#define BLOCK_ROWS 4
bool blocks[BLOCK_ROWS][BLOCK_COLS];

// ゲームの状態
String gameState = "title";

void gameinit() {
  // ゲームの初期化処理
  ballX = 120;
  ballY = 120;
  paddleX = 150;
  paddleY = 200;

  // ブロックの初期化
  for (int row = 0; row < BLOCK_ROWS; row++) {
    for (int col = 0; col < BLOCK_COLS; col++) {
      blocks[row][col] = true;
    }
  }
}

void title() {
  // タイトル画面の描画処理
  spr.fillSprite(TFT_BLACK);
  spr.setTextColor(TFT_WHITE);
  spr.setTextSize(2);
  spr.drawString("PRESS A TO START", 50, 100);
  spr.pushSprite(0, 0);
  // タイトル画面の描画処理を追加
  spr.pushSprite(0, 0); // LCDに描画
  // タイトル画面からの遷移判定を追加
  if (digitalRead(WIO_KEY_A) == LOW) {
    gameState = "main";
  }
}

void gamestage() {
  // Move the paddle based on button input
  if(digitalRead(WIO_5S_RIGHT) == LOW && paddleX < 320 - PADDLE_WIDTH) {
    paddleX = paddleX + 5;
  }
  if(digitalRead(WIO_5S_LEFT) == LOW && paddleX > 0) {
    paddleX = paddleX - 5;
  }

  // ボールの移動
  ballX += ball_speed_X;
  ballY += ball_speed_Y;

  // 壁との衝突判定
  if(ballX - BALL_RADIUS < 0 || ballX + BALL_RADIUS > 320) {
    ball_speed_X = -ball_speed_X;
  }
  if(ballY - BALL_RADIUS < 0 || ballY + BALL_RADIUS > 240) {
    ball_speed_Y = -ball_speed_Y;
  }

  // パドルとの衝突判定
  if(paddleX < ballX && ballX < paddleX + PADDLE_WIDTH && paddleY < ballY + BALL_RADIUS && ballY + BALL_RADIUS < paddleY + PADDLE_HEIGHT) {
    ball_speed_Y = -ball_speed_Y;
  }

  // ブロックとの衝突判定
  checkBlockCollision();

  // ゲームメイン画面の描画処理
  spr.fillSprite(TFT_BLACK);

  // ゲームメイン画面の描画処理を追加
  drawBlocks();
  spr.fillRect(paddleX, paddleY, PADDLE_WIDTH, PADDLE_HEIGHT, TFT_WHITE);
  spr.fillCircle(ballX, ballY, BALL_RADIUS, TFT_RED);
  spr.pushSprite(0, 0); // LCDに描画

  // ゲームオーバー判定を追加
  if (ballY + BALL_RADIUS > 240) {
    gameState = "gameover";
  }

}

void gameover() {
  // ゲームオーバー画面の描画処理
  spr.fillSprite(TFT_BLACK);
  spr.setTextColor(TFT_RED);
  spr.setTextSize(3);
  spr.drawString("GAME OVER", 70, 80);
  spr.setTextSize(2);
  spr.drawString("PRESS A TO RETRY", 40, 150);
  spr.pushSprite(0, 0); // LCDに描画
  // ゲームオーバー画面からの遷移判定を追加
  if (digitalRead(WIO_KEY_A) == LOW) {
    gameinit();
    gameState = "main";
  }
}

void drawBlocks() {
  for (int row = 0; row < BLOCK_ROWS; row++) {
    for (int col = 0; col < BLOCK_COLS; col++) {
      if (blocks[row][col]) {
        spr.fillRect(col * BLOCK_WIDTH, row * BLOCK_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT, TFT_WHITE);
      }
    }
  }
}

void checkBlockCollision() {
  for (int row = 0; row < BLOCK_ROWS; row++) {
    for (int col = 0; col < BLOCK_COLS; col++) {
      if (blocks[row][col]) {
        int blockX = col * BLOCK_WIDTH;
        int blockY = row * BLOCK_HEIGHT;

        if (ballX + BALL_RADIUS > blockX && ballX - BALL_RADIUS < blockX + BLOCK_WIDTH &&
            ballY + BALL_RADIUS > blockY && ballY - BALL_RADIUS < blockY + BLOCK_HEIGHT) {
          // ブロックとの衝突
          blocks[row][col] = false;
          ball_speed_Y = -ball_speed_Y;
        }
      }
    }
  }
}

void setup() {
  pinMode(WIO_KEY_A, INPUT);
  pinMode(WIO_5S_UP, INPUT);
  pinMode(WIO_5S_DOWN, INPUT);
  pinMode(WIO_5S_LEFT, INPUT);
  pinMode(WIO_5S_RIGHT, INPUT);
  tft.begin();
  tft.setRotation(3);
  spr.createSprite(TFT_HEIGHT, TFT_WIDTH); // バッファの作成

  gameinit(); // ゲームの初期化
}

void loop() {
  // ゲームの状態によって分岐
  if (gameState == "title") {
    title();
  } else if (gameState == "main") {
    gamestage();
  } else if (gameState == "gameover") {
    gameover();
  }

  // ゲーム速度
  delay(10);
}
