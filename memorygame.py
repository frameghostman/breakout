# coding: utf-8
from scene import *
import time
import random
A = Action

#カード情報
card_w = 140 #カード横幅
card_h = 190 #カード縦幅
m = 10 #カード間隔
rows = 2 #カード縦列数
columns = 4 #カード横列数

# カード表
cards_f = []
cards_f.append('card:ClubsA')
cards_f.append('card:Clubs2')
cards_f.append('card:Clubs3')
cards_f.append('card:Clubs4')
cards_f.append('card:HeartsA')
cards_f.append('card:Hearts2')
cards_f.append('card:Hearts3')
cards_f.append('card:Hearts4')
random.shuffle(cards_f)

#カード状態(Trueで裏)
cards_stat = []
for i in range(rows*columns):
	cards_stat.append(True)
turn_cards_f = [] #めくったカード情報
count = 0
wait_flg = False
total = 0
point = 0
result_flg = False

class Result (Scene):
	def setup(self):
		self.background_color = '#3c8242' #背景色	
		message = ['Score',
							 'Challenge :' + str(total),
							 'Result :' + str(point*100 // total) + '%']
		for i in range(len(message)):
				label = LabelNode(message[i], parent=self, font=('Arial',20), position=(self.size.w/2,400-i*50), color='orange')

class Game (Scene):
	def setup(self):
		global card_w, card_h, m, rows, columns
		init_x = self.size.w/2 - card_w*(columns/2) #カード開始x位置
		init_y = self.size.h/2 - card_h*(rows/2) #カード開始y位置

		self.cards = [] #カード用配列 
		self.turn_cards = [] #めくったカード
		self.background_color = '#004f82' #背景色

		# Make Card list
		x = init_x
		y = init_y
		for row in range(rows):
			for column in range(columns):
				self.cards.append(SpriteNode('card:BackBlue1', parent=self, position=(x, y)))
				self.cards[columns*row + column].anchor_point = (0, 0)
				x += card_w + m
			x = init_x
			y += card_h + m

	def touch_ended(self, touch):
		global count, wait_flg, cards_f, cards_stat
		# ウェイト中は何もしない
		if wait_flg:
			return
		# タップした位置の取得
		touch_loc = self.point_from_scene(touch.location)
		# タップした位置がカード
		for i in range(len(self.cards)):
			if touch_loc in self.cards[i].frame: #カードをクリックしたとき
				if cards_stat[i]: #もしカードが裏なら
					self.cards[i].texture = Texture(cards_f[i]) #カードを表にする
					cards_stat[i] = False #カードの状態を表にする
					self.turn_cards.append(self.cards[i]) #めくったカードを記憶
					turn_cards_f.append([cards_f[i], i]) #めくったカードを記憶(テクスチャ, 場所)
					count += 1
		if count == 2:
			count = 0
			self.run_action(A.sequence(A.wait(1), A.call(self.restore)))
			wait_flg = True

	def restore(self):
		global point, total, count, wait_flg, turn_cards_f, cards_stat
		if turn_cards_f[0][0][-1] != turn_cards_f[1][0][-1]: #めくったカードが一致しない場合
			for card in self.turn_cards: #めくったカードを
				card.texture = Texture('card:BackBlue1') #カードを裏にする
				cards_stat[turn_cards_f[0][1]] = True #めくったカード1枚目の状態を裏にする
				cards_stat[turn_cards_f[1][1]] = True #めくったカード2枚目の状態を裏にする
		else:
			point += 1
		total += 1
		self.turn_cards.clear()
		turn_cards_f.clear()
		wait_flg = False
		if point >= len(self.cards)/2:
			self.call_result()

	def call_result(self):
		# リザルト画面用
		sv = SceneView()
		sv.scene = Result()		
		sv.present()

if __name__ == '__main__':
	run(Game(), PORTRAIT, show_fps=True)
