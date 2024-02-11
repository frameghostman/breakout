from scene import *
import sound
import random
import math
import time
A = Action

slot_pictures = ['emj:Chicken', 'emj:Dog_Face', 'emj:Horse_Face', 'emj:Bear_Face', 'emj:Cat_Face', 'emj:Honeybee']
slot_counts = [0, 1, 2] #見えている絵柄
drum = [1, 1, 1] #1で停止、0で回転中
status = 1 #1開始画面 #2ゲーム中 #3終了/判定画面
message = ''
time_count = 0

class Result (Scene):
	def setup(self):
		self.background_color = '#3c8242' #背景色	
		label = LabelNode(message, parent=self, font=('Arial',20), position=(self.size.w/2,400), color='orange')

class MyScene (Scene):
	def setup(self):
		# 背景色
		self.background_color = 'midnightblue'

		# picture追加
		self.pictures = []
		self.pictures.append(SpriteNode(slot_pictures[slot_counts[0]], parent=self, position=(300,500), size=(100,100)))
		self.pictures.append(SpriteNode(slot_pictures[slot_counts[1]], parent=self, position=(500,500), size=(100,100)))
		self.pictures.append(SpriteNode(slot_pictures[slot_counts[2]], parent=self, position=(700,500), size=(100,100)))

		# switch		
		self.switch = SpriteNode('pzl:BallBlue', parent=self, position=(900,300), size=(50,50))

		# stop button
		self.buttons = []
		self.buttons.append(SpriteNode('pzl:Button2', parent=self, position=(300,300)))
		self.buttons.append(SpriteNode('pzl:Button2', parent=self, position=(500,300)))
		self.buttons.append(SpriteNode('pzl:Button2', parent=self, position=(700,300)))

	def update(self):
		global status, time_count
		if status == 3:
			time_count += 1
			if time_count >= 60: #1秒待ってから
				self.judgment() #リザルト画面
				status = 1 #開始画面に戻す
		if status == 2: #ゲーム中なら
			time_count += 1
			if time_count >= 20: #0.33秒間に1回
				time_count = 0
				for i in range(len(self.pictures)):
					self.rotation(i) #ドラムを回す

	def touch_ended(self, touch):
		global status
		# タップした位置の取得
		touch_loc = self.point_from_scene(touch.location)
		if status == 1: #もし開始画面で
			# タップした位置がボールなら
			if touch_loc in self.switch.frame: #ボールをクリックしたとき
				for i in range(len(drum)):
					drum[i] = 0 #全ドラムを回転中にして
				status = 2 #ゲーム中へ
		elif status == 2: #ゲーム中で
			# タップした位置がボタンなら
			for i in range(len(self.buttons)):
				if touch_loc in self.buttons[i].frame: #ボタンをクリックしたとき
					drum[i] = 1 #対応するドラムを停止		
	
	def rotation(self, num):
		global status
		if drum[num] == 0: #ドラムが回転中なら
			slot_counts[num] += 1 #対応するドラムの柄を変える
			if slot_counts[num] >= len(slot_pictures):
				slot_counts[num] = 0
			self.pictures[num].texture = Texture(slot_pictures[slot_counts[num]])
		if drum[0] == 1 and drum[1] == 1 and drum[2] == 1: #全ドラムが停止したなら
			status = 3 #ゲーム終了/判定へ

	def judgment(self):
		global message
		j = slot_counts[0] == slot_counts[1] == slot_counts[2]
		message = 'win' if j else 'miss'
		# リザルト画面用
		sv = SceneView()
		sv.scene = Result()		
		sv.present()
		
if __name__ == '__main__':
	run(MyScene(), show_fps=False)
