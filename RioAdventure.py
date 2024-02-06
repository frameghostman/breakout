from scene import *
import sound
import random
import collections
A = Action
speed = 10
game_mode = 0

def cmp(a, b):
	return((a > b) - (a < b))

standing_texture = Texture('plf:AlienPink_front')
swim_texture = [Texture('plf:AlienPink_swim1'), Texture('plf:AlienPink_swim2')]
hit_texture = Texture('plf:AlienPink_hit')

class Coin (SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, 'plf:Item_CoinGold', **kwargs)

class Meteor (SpriteNode):
	def __init__(self, **kwargs):
		img = random.choice(['spc:MeteorBrownBig1', 'spc:MeteorBrownBig2', 'spc:MeteorGrayBig3', 'spc:MeteorGrayBig4'])
		SpriteNode.__init__(self, img, **kwargs)

class Game(Scene):
	def setup(self):
		global game_mode
		global initialflag
		global initialgx
		initialflag = 0
		initialgx = 0
		self.background_color = 'blue'
		ground = Node(parent = self)
		x = 0
		while x <= self.size.w + 64:
			tile = SpriteNode('plf:Ground_GrassHalf', position= (x, 0))
			ground.add_child(tile)
			x += 64
		self.player = SpriteNode('plf:AlienPink_front')
		self.player.anchor_point = (0.5, 0)
		self.player.position = (self.size.w/2, 32)
		self.add_child(self.player)
		self.walk_step = -1
		self.items = []

		# ジャンプボタンの初期設定
		self.jump = 'ready'
		self.jump_button = SpriteNode('emj:Blue_Circle', position=(1000,600))

		if game_mode == 2:
			self.add_child(self.jump_button)

		font = ('Futura', 10)
		score_font = ('Futura', 40)
		self.g_ix = LabelNode(text=str(0), font=font, parent=self, position = (800, self.size.h - 70), z_position=1)
		self.g_cx = LabelNode(text=str(0), font=font, parent=self, position = (800, self.size.h - 100), z_position=1)
		self.g_y = LabelNode(text=str(0), font=font, parent=self, position = (800, self.size.h - 130), z_position=1)
		self.score_label = LabelNode('0', score_font, parent=self, position = (self.size.w/2, self.size.h - 70), z_position = 1)

		self.new_game()

	def new_game(self):
		# Reset everything to its initial state...
		for item in self.items:
			item.remove_from_parent()
		self.player_height = 32
		self.items = []
		self.score = 0
		self.score_label.text = '0'
		self.walk_step = -1
		self.player.position = (self.size.w/2, self.player_height)
		self.player.texture = standing_texture
		self.speed = 1.0
		self.player.alpha = 1
		self.game_over = False
		self.move_target = self.size.w/2

	def update(self):
		if self.game_over:
			return
		if game_mode == 1:
			self.update_player_g()
		elif game_mode == 2:
			self.update_player_t()
		self.check_item_collisions()
		if random.random() < 0.05:
			if len(self.items) < 10:
				self.spawn_item()

	def update_player_t(self):
		x = self.player.position.x
		y = self.player.position.y
		dx = self.move_target - self.player.position.x
		if abs(dx) > speed:
			dx = speed * cmp(dx, 0)

		# 上昇時の処理
		if self.jump == 'up':
			max_height = 180
			up_speed = 10
			y = max(self.player_height, min(self.size.h, y + up_speed))
			self.player.position = (x, y)
			if y > max_height + self.player_height:
				self.jump = 'down'
 
		# 落下時の処理        
		if self.jump == 'down':
			down_speed = 10
			y = max(self.player_height, min(self.size.h, y - down_speed))
			self.player.position = (x, y)
			if y == self.player_height:
				self.jump = 'ready'    
		self.player.position += dx, 0

	def update_player_g(self):
		global initialflag
		global initialgx
		step = -1
		g = gravity()
		if initialflag == 0:
			initialgx = g.x

		currentgx = g.x
		diff = currentgx - initialgx

		self.g_ix.text = str(initialgx)		
		self.g_cx.text = str(diff)
		self.g_y.text = str(g.y)

		x = self.player.position.x
		y = self.player.position.y
		max_speed = 40
		
		if abs(g.y) > 0.05:
			self.player.x_scale = cmp(0, g.y)
			x = max(0, min(self.size.w, x + g.y * -1 * max_speed))
			self.player.position = (x, y)
			step = int((self.player.position.x + self.player.position.y) / 40) % 2

		if abs(diff) > 0.05:
			y = max(32, min(self.size.h, y + diff * max_speed))
			self.player.position = (x, y)
			step = int((self.player.position.x + self.player.position.y) / 40) % 2

		if step != self.walk_step:
			self.player.texture = swim_texture[step]
			sound.play_effect('game:Footstep', 0.05, 1.0 + 0.5 * step)
			self.walk_step = step

		if abs(g.y) <= 0.05 and abs(diff) <= 0.05:
			self.player.texture = standing_texture
			self.walk_step = -1

		initialflag = 1

	def check_item_collisions(self):
		player_hitbox = Rect(self.player.position.x - 20, self.player.position.y - 32, 40, 65)
		for item in list(self.items):
			if item.frame.intersects(player_hitbox):
				if isinstance(item, Coin):
					self.collect_item(item)
				elif isinstance(item, Meteor):
					self.player_hit(self.player.position)
			elif not item.parent:
				self.items.remove(item)	

	def player_hit(self, position):
		self.game_over = True
		sound.play_effect('arcade:Explosion_1')
		explosion = SpriteNode('shp:Explosion00', position, size = (50, 50))
		pl_actions = [A.move_by(0, -100), A.fade_to(0.0, 1.0, TIMING_LINEAR)]
		ex_actions = [A.scale_to(10.0, 1.0, TIMING_LINEAR), A.fade_to(0.0, 1.0, TIMING_LINEAR)]
		self.player.texture = hit_texture
		self.player.run_action(A.sequence(pl_actions))
		explosion.run_action(A.group(ex_actions))
		self.add_child(explosion)
		self.run_action(A.sequence(A.wait(2*self.speed), A.call(self.new_game)))

	def spawn_item(self):
		if random.random() < 0.3:
			meteorcount = 0
			for item in list(self.items):
				if isinstance(item, Meteor):
					meteorcount += 1
			if meteorcount < 1:
				meteor = Meteor(parent=self)
				meteor.position = (random.uniform(20, self.size.w-20), self.size.h + 30)
				d = random.uniform(19.0, 20.0)
				actions = [A.move_to(random.uniform(0, self.size.w), -100, d), A.remove()]
				meteor.run_action(A.sequence(actions))
				self.items.append(meteor)
		else:
			coin = Coin(parent=self)
			coin.position = (random.uniform(20, self.size.w-20), self.size.h + 30)
			d = random.uniform(9.0, 10.0)
			actions = [A.move_by(0, -(self.size.h + 60 - 80), d, TIMING_BOUNCE_OUT)]
			coin.run_action(A.sequence(actions))
			self.items.append(coin)
		#self.speed = min(3, self.speed + 0.005)
		
	def collect_item(self, item, value = 10):
		sound.play_effect('digital:PowerUp7')
		item.remove_from_parent()
		self.items.remove(item)
		self.score += value
		self.score_label.text = str(self.score)

	def touch_began(self, touch):

		# タップした位置の取得
		touch_loc = self.point_from_scene(touch.location)
		# タップした位置がボタンならジャンプ
		if touch_loc in self.jump_button.frame:
			if self.jump == 'ready':
				sound.play_effect('game:Boing_1')
				self.jump = 'up'
		else:
			x, y = touch.location
			self.move_target = x

	def touch_moved(self, touch):
		self.move_target = touch.location.x


class Title (Scene):
	def setup(self):
		self.background_color = '#05982f'
		ground = Node(parent=self)
		# タイトルの表示
		font = ('Chalkboard SE', 50)
		label = LabelNode('りおの大冒険', font, parent=self, color='yellow')
		label.position = (self.size.w/2, self.size.h - 200)
		label.z_position = 1
	
		# サブタイトルの表示
		font = ('Chalkboard SE', 25)
		subtitle_label = LabelNode('~コインをゲットだぜ!~', font, parent=self, color='white')
		subtitle_label.position = (self.size.w/2, self.size.h -280)
		subtitle_label.z_position = 1
		
		# メッセージ
		font = ('Chalkboard SE', 20)
		text_label = LabelNode('ボタンをタッチしてね', font, parent=self, color='white')
		text_label.position = (self.size.w/2, 150)
		text_label.z_position = 1

		button_font = ('Futura', 30)
		# ボタン1
		self.button1 = SpriteNode('pzl:Button1', position=(self.size.w / 2, 300))
		self.button1_label = LabelNode('Gravity', button_font, parent=self, color='black')
		self.button1_label.position = (self.size.w / 2, 305)
		self.button1_label.z_position = 1
		self.add_child(self.button1)

		# ボタン2
		button_font = ('Futura', 30)
		self.button2 = SpriteNode('pzl:Button1', position=(self.size.w / 2, 240))
		self.button2_label = LabelNode('Touch', button_font, parent=self, color='black')
		self.button2_label.position = (self.size.w / 2, 245)
		self.button2_label.z_position = 1
		self.add_child(self.button2)

	def touch_began(self, touch):
		global game_mode
		touch_loc = self.point_from_scene(touch.location)
		if touch_loc in self.button1.frame:
			game_mode = 1
			# ゲーム画面に切り替える処理
			sv = SceneView()
			# パラメータ設定
			ui_orientations = None
			sv.anti_alias = False
			sv.frame_interval = 1
			sv.multi_touch_enabled = True
			sv.shows_fps = False
			# MySceneを読み込む
			sv.scene = Game()
			sv.present(orientations=ui_orientations)

		if touch_loc in self.button2.frame:
			game_mode = 2
			# ゲーム画面に切り替える処理
			sv = SceneView()
			# パラメータ設定
			ui_orientations = None
			sv.anti_alias = False
			sv.frame_interval = 1
			sv.multi_touch_enabled = True
			sv.shows_fps = False
			# MySceneを読み込む
			sv.scene = Game()
			sv.present(orientations=ui_orientations)

if __name__ == '__main__':
	run(Title(), show_fps=False)
