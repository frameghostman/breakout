from scene import *
import sound
import random
import math
A = Action

map_data=[[0,0,1,0,0,1,0,0,0,0],
	        [1,0,1,1,0,1,0,0,1,1],
	        [0,0,0,0,0,0,0,0,0,0],
	        [1,0,1,1,0,1,1,0,1,0],
	        [0,0,0,1,0,0,0,0,0,0],
	        [0,0,0,0,0,1,1,0,1,1],
	        [0,1,1,1,0,0,0,0,0,0]]
player_location = [1, 0] #プレイヤー初期位置
cargo_location = [1, 1] #荷物初期位置
exit_location = [9, 6] #出口位置
size = 70 #タイルサイズ
init_x = 0
init_y = 0
status = 1 # 1:ゲーム中 2:終了 3:リザルト画面
message = ''
time_count = 0

class Result (Scene):
	def setup(self):
		self.background_color = '#3c8242' #背景色	
		label = LabelNode(message, parent=self, font=('Arial',20), position=(self.size.w/2,400), color='orange')

class MyScene (Scene):
	def setup(self):
		global init_x, init_y, size
		init_x = self.size.w/2 - 400 #背景開始x位置
		init_y = self.size.h/2 - 200 #背景開始y位置

		self.grounds = [] #背景用配列
		self.walls = [] #壁用配列
		self.background_color = '#004f82' #背景色
		
		# For Controller
		self.upbutton = SpriteNode('typb:Up', parent=self, size=(size, size), position=(1000, 500))
		self.downbutton = SpriteNode('typb:Down', parent=self, size=(size, size), position=(1000, 300))
		self.leftbutton = SpriteNode('typb:Left', parent=self, size=(size, size), position=(900, 400))
		self.rightbutton = SpriteNode('typb:Right', parent=self, size=(size, size), position=(1100, 400))
		
		# Make grounds
		for y in range(7):
			for x in range(10):
				self.grounds.append(SpriteNode('plf:Ground_StoneCenter', parent=self, size=(size, size), position=(init_x + size*x, init_y + size*y)))

		# Make walls
		for y in range(7):
			for x in range(10):
				if map_data[y][x] != 0:
					self.walls.append(SpriteNode('plf:Tile_BoxCrate_double', parent=self, size=(size, size), position=(init_x + size*x, init_y + 420 + size*-y)))

		# Exit
		self.exit = SpriteNode('plc:Chest_Closed',parent=self, size=(size, size), position=(init_x+exit_location[0]*size, init_y+420-exit_location[1]*size))

		# Player		
		self.player = SpriteNode('plc:Character_Horn_Girl', parent=self, size=(size, size))

		# Cargo	
		self.cargo = SpriteNode('plc:Key', parent=self, size=(size, size))
		
		# Game Start
		self.new_game()

	def new_game(self):
		global time_count
		time_count = 0
		player_location[0] = 1
		player_location[1] = 0
		cargo_location[0] = 1
		cargo_location[1] = 1
		self.player.position = (init_x+player_location[0]*size, init_y+420-player_location[1]*size)
		self.cargo.position = (init_x+cargo_location[0]*size, init_y+420-cargo_location[1]*size)

	def update(self):
		global status, time_count
		if status == 2: #終了判定チェック
			time_count += 1
			if time_count >= 60: #1秒待ってから
				# リザルト画面用
				sv = SceneView()
				sv.scene = Result()		
				sv.present() # リザルト画面表示
				status = 1 #開始画面に戻す
				self.new_game()
				
	def touch_ended(self, touch):
		global init_x, init_y, size, player_location
		touch_loc = self.point_from_scene(touch.location) # タップした位置の取得

		if touch_loc in self.upbutton.frame:
			key = 'up'
			if player_location[1] > 0:
				if self.is_cargo(key):
					if self.is_push(key):
						self.move(key, player_location, self.player)
				elif self.is_not_box(key, player_location):
					self.move(key, player_location, self.player)

		elif touch_loc in self.downbutton.frame:
			key = 'down'
			if player_location[1] < len(map_data)-1:
				if self.is_cargo(key):
					if self.is_push(key):
						self.move(key, player_location, self.player)
				elif self.is_not_box(key, player_location):
					self.move(key, player_location, self.player)

		elif touch_loc in self.leftbutton.frame:
			key = 'left'
			if player_location[0]:
				if self.is_cargo(key):
					if self.is_push(key):
						self.move(key, player_location, self.player)
				elif self.is_not_box(key, player_location):
					self.move(key, player_location, self.player)

		elif touch_loc in self.rightbutton.frame:
			key = 'right'
			if player_location[0] < len(map_data[0])-1:
				if self.is_cargo(key):
					if self.is_push(key):
						self.move(key, player_location, self.player)
				elif self.is_not_box(key, player_location):
					self.move(key, player_location, self.player)
		self.judgment()
	
	def is_not_box(self, key, location): #keyの方向が壁でなければ True を返す
		if key == 'up':
			if map_data[location[1]-1][location[0]] != 1:
				return True
		elif key == 'down':
			if map_data[location[1]+1][location[0]] != 1:
				return True
		elif key == 'left':
			if map_data[location[1]][location[0]-1] != 1:
				return True
		elif key == 'right':
			if map_data[location[1]][location[0]+1] != 1:
				return True
		return False

	def move(self, key, location, obj): #keyの方向にobjを動かす
		if key == 'up':
			location[1] -= 1
			obj.position = (init_x+location[0]*size, init_y+420-location[1]*size)
		elif key == 'down':
			location[1] += 1
			obj.position = (init_x+location[0]*size, init_y+420-location[1]*size)
		elif key == 'left':
			location[0] -= 1
			obj.position = (init_x+location[0]*size, init_y+420-location[1]*size)
		elif key == 'right':
			location[0] += 1
			obj.position = (init_x+location[0]*size, init_y+420-location[1]*size)

	def is_cargo(self, key): #keyの方向が荷物なら True を返す
		if key == 'up':
			if player_location[1]-1 == cargo_location[1] and player_location[0] == cargo_location[0]:
				return True
		elif key == 'down':
			if player_location[1]+1 == cargo_location[1] and player_location[0] == cargo_location[0]:
				return True
		elif key == 'left':
			if player_location[0]-1 == cargo_location[0] and player_location[1] == cargo_location[1]:
				return True
		elif key == 'right':
			if player_location[0]+1 == cargo_location[0] and player_location[1] == cargo_location[1]:
				return True
		return False

	def is_push(self, key): #keyの方向に荷物を動かす
		if key == 'up':
			if cargo_location[1] > 0 and self.is_not_box(key, cargo_location):
				self.move(key, cargo_location, self.cargo)
				return True
		elif key == 'down':
			if cargo_location[1] < len(map_data)-1 and self.is_not_box(key, cargo_location):
				self.move(key, cargo_location, self.cargo)
				return True
		elif key == 'left':
			if cargo_location[0] > 0 and self.is_not_box(key, cargo_location):
				self.move(key, cargo_location, self.cargo)
				return True
		elif key == 'right':
			if cargo_location[0] < len(map_data[0])-1 and self.is_not_box(key, cargo_location):
				self.move(key, cargo_location, self.cargo)
				return True

	def judgment(self): #終了判定
		global status, message
		if cargo_location == exit_location: #ゴールしたならクリア
			message = 'STAGE CLEAR'
			status = 2
		else: #ゴールしてないならゲームオーバー判定
			touch = 0
			x = cargo_location[0]
			y = cargo_location[1]
			if x == 0 or x == len(map_data[0])-1: #左右が壁か
				touch += 1
			elif map_data[y][x-1] == 1 or map_data[y][x+1] == 1: #左右がブロックなら touch を+1
				touch += 1
			if y == 0 or y == len(map_data)-1: #上下が壁か
				touch += 1
			elif map_data[y-1][x] == 1 or map_data[y+1][x] == 1: #上下がブロックなら touch を+1
				touch += 1
			if touch >= 2: #touchが2以上だと荷物は動かせないのでゲームオーバー
				message = 'GAME OVER'
				status = 2

if __name__ == '__main__':
	run(MyScene(), show_fps=False)
