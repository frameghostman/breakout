from scene import *
import sound
import random
import math
import ui
A = Action

vx = 0
vy = 0

class MyScene (Scene):
	def setup(self):
		#background color
		self.background_color = 'blue'

		#paddle & ball setting
		barrect = ui.Path.rect(0, 0, 150, 20)
		ballrect = ui.Path.oval(0, 0, 20, 20)
		self.blocks = []
		self.paddle = ShapeNode(barrect, parent=self)
		self.ball = ShapeNode(ballrect, parent=self)

		#for result messeage
		self.resultlabel = LabelNode('', parent=self, color='yellow', position=(self.size.w/2, self.size.h - 500))

		#Game Start
		self.new_game()

	def new_game(self):
		global vx, vy
		vx = 0 #ボール速度0に初期化
		vy = 0 #ボール速度0に初期化

		#パドルとボールの初期位置をセット
		self.paddle.position = (self.size.w/2, 100)
		self.ball.position = (self.size.w/2, 200)
		
		self.resultlabel.text=''
		
		#ブロック描画
		for block in self.blocks:
			block.remove_from_parent()
		self.blocks = []
		blockrect = ui.Path.rect(0, 0, 80, 30)
		for yy in range(4):
			for xx in range(11):
				self.blocks.append(ShapeNode(blockrect, parent=self, position=(100+xx*100, self.size.h - (40+yy*50))))
	
	def update(self):
		g = gravity()
		if abs(g.y) > 0.05:
			x = self.paddle.position.x
			max_speed = 40
			x = max(0, min(self.size.w, x - g.y * max_speed))
			self.paddle.position = (x, 100)
		self.gamestage()
	
	def touch_ended(self, touch):
		global vx, vy
		vx = 10
		vy = 10

	def gamestage(self):
		global vx, vy
		
		#ボール位置更新
		x = self.ball.position.x + vx
		y = self.ball.position.y + vy
		self.ball.position = (x, y)
		
		#壁反射
		if x < 0 or self.size.w < x:
			vx = -vx
		if self.size.h < y:
			vy = -vy

		#ボールが下に落ちたらゲームオーバー
		if y < 0:
			self.game_over()
		
		#パドルで反射
		if self.paddle.frame.intersects(Rect(x, y, 20, 20)):
			vy = -vy
		
		#ブロック衝突判定
		for block in self.blocks:
			if block.frame.intersects(Rect(x, y, 20, 20)):
				block.remove_from_parent()
				self.blocks.remove(block)
				vy = -vy
				if len(self.blocks) <= 0: #ブロックが0になったら
					vx = 0
					vy = 0
					self.game_clear() #ゲームクリア

	def game_over(self):
		self.resultlabel.text='GAME OVER'
		self.run_action(A.sequence(A.wait(1), A.call(self.new_game)))

	def game_clear(self):
		self.resultlabel.text='GAME CLEAR!!'
		self.run_action(A.sequence(A.wait(1), A.call(self.new_game)))

class Title (Scene):
	def setup(self):
		self.background_color = '#05982f'
		ground = Node(parent=self)
		# タイトルの表示
		font = ('Chalkboard SE', 50)
		label = LabelNode('ブロック崩し', font, parent=self, color='yellow', position=(self.size.w/2, self.size.h - 200))
		
		# メッセージ
		font = ('Chalkboard SE', 20)
		text_label = LabelNode('ボタンをタッチしてね', font, parent=self, color='white', position=(self.size.w/2, 150))

		# ボタン
		button_font = ('Futura', 30)
		self.button1 = SpriteNode('pzl:Button1', parent=self,position=(self.size.w / 2, 300))
		self.button1_label = LabelNode('Gravity', button_font, parent=self, color='black', position=(self.size.w / 2, 305))

	def touch_began(self, touch):
		touch_loc = self.point_from_scene(touch.location)
		if touch_loc in self.button1.frame:
			# ゲーム画面に切り替える処理
			sv = SceneView()
			# パラメータ設定
			ui_orientations = None
			sv.anti_alias = False
			sv.frame_interval = 1
			sv.multi_touch_enabled = True
			sv.shows_fps = False
			# MySceneを読み込む
			sv.scene = MyScene()
			sv.present(orientations=ui_orientations)

if __name__ == '__main__':
	run(Title(), show_fps=False)
