from scene import *
from sound import *
import time
import random
import speech
symbol_list = ['Clubs', 'Hearts', 'Spades', 'Diamonds']

class MyScene (Scene):
	def setup(self):
		# 背景色
		self.background_color = 'midnightblue'
		score_number = 0

		# Card追加
		card1_kind = random.randint(0,3)
		card1_number = 'A'
		card1 = symbol_list[card1_kind] + str(card1_number)
		self.x1 = 200
		self.y1 = 500
		self.card1 = SpriteNode('card:' + card1, position=(self.x1, self.y1))
		self.add_child(self.card1)

		card2_kind = random.randint(0,3)
		card2_number = 2
		card2 = symbol_list[card2_kind] + str(card2_number)
		self.x2 = 400
		self.y2 = 500
		self.card2 = SpriteNode('card:' + card2, position=(self.x2, self.y2))
		self.add_child(self.card2)

		card3_kind = random.randint(0,3)
		card3_number = 3
		card3 = symbol_list[card3_kind] + str(card3_number)
		self.x3 = 600
		self.y3 = 500
		self.card3 = SpriteNode('card:' + card3, position=(self.x3, self.y3))
		self.add_child(self.card3)

		card4_kind = random.randint(0,3)
		card4_number = 4
		card4 = symbol_list[card4_kind] + str(card4_number)
		self.x4 = 800
		self.y4 = 500
		self.card4 = SpriteNode('card:' + card4, position=(self.x4, self.y4))
		self.add_child(self.card4)

		card5_kind = random.randint(0,3)
		card5_number = 5
		card5 = symbol_list[card5_kind] + str(card5_number)
		self.x5 = 1000
		self.y5 = 500
		self.card5 = SpriteNode('card:' + card5, position=(self.x5, self.y5))
		self.add_child(self.card5)

		# テキストの追加
		font1 = ('Futura', 100)
		text = str(random.randint(1,5))
		self.number = LabelNode(text=text, font=font1, parent=self, position = (self.size.w/2, self.size.h - 70), z_position=1)
		speech.say(self.number.text)

		font2 = ('Futura', 50)
		score_title = "Score:"
		score_text = str(score_number)
		self.scoretitle = LabelNode(text=score_title, font=font2, parent=self, position = (800, self.size.h - 70), z_position=1)
		self.score = LabelNode(text=score_text, font=font2, parent=self, position = (1000, self.size.h - 70), z_position=1)

	def update(self):
		pass

	def touch_began(self, touch):
		#x, y = touch.location
		#move_action = Action.move_to(x, y, 0.7, TIMING_SINODIAL)
		#self.card.run_action(move_action)
		pass

	def touch_ended(self, touch):
		# タップした位置の取得
		touch_loc = self.point_from_scene(touch.location)
		# タップした位置がカード
		if touch_loc in self.card1.frame:
			if self.number.text == '1':
				play_effect(name = 'arcade:Coin_2', volume = 1)
				self.score.text = str(int(self.score.text) + 1)
				time.sleep(1)
				self.number.text = str(random.randint(1,5))
				speech.say(self.number.text)
				
			else:
				play_effect(name = 'game:Error', volume = 1)
				self.score.text = str(0)
				time.sleep(1)

		if touch_loc in self.card2.frame:
			if self.number.text == '2':
				play_effect(name = 'arcade:Coin_2', volume = 1)
				self.score.text = str(int(self.score.text) + 1)
				time.sleep(1)
				self.number.text = str(random.randint(1,5))
				speech.say(self.number.text)
			else:
				play_effect(name = 'game:Error', volume = 1)
				self.score.text = str(0)
				time.sleep(1)
				
		if touch_loc in self.card3.frame:
			if self.number.text == '3':
				play_effect(name = 'arcade:Coin_2', volume = 1)
				self.score.text = str(int(self.score.text) + 1)
				time.sleep(1)
				self.number.text = str(random.randint(1,5))
				speech.say(self.number.text)
			else:
				play_effect(name = 'game:Error', volume = 1)
				self.score.text = str(0)
				time.sleep(1)

		if touch_loc in self.card4.frame:
			if self.number.text == '4':
				play_effect(name = 'arcade:Coin_2', volume = 1)
				self.score.text = str(int(self.score.text) + 1)
				time.sleep(1)
				self.number.text = str(random.randint(1,5))
				speech.say(self.number.text)
			else:
				play_effect(name = 'game:Error', volume = 1)
				self.score.text = str(0)
				time.sleep(1)

		if touch_loc in self.card5.frame:
			if self.number.text == '5':
				play_effect(name = 'arcade:Coin_2', volume = 1)
				self.score.text = str(int(self.score.text) + 1)
				time.sleep(1)
				self.number.text = str(random.randint(1,5))
				speech.say(self.number.text)
			else:
				play_effect(name = 'game:Error', volume = 1)
				self.score.text = str(0)
				time.sleep(1)

if __name__ == '__main__':
	run(MyScene(), show_fps=False)
