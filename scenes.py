#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Copyright © 2011: Lattyware <gareth@lattyware.co.uk>

This file is part of unrest.

unrest is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

unrest is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

Just as a quick note, please remember if you are reading this, 48 hours. It's
not clean, well documented or particularly well done in general, but that wasn't
the point. Hopefully it's a bit of fun.
"""

import os
import sf
import random

from unrest import opacity, Quit
import entities

class Scene:
	def __init__(self, state, *args):
		self.player = None
		self.state = state
		self.to_render = []
		self.objects = []
		self.next = None
		self.finished = False
		self.goal = sf.Text("Escape Hopelessness", sf.Font.DEFAULT_FONT, 30)
		self.goal.origin = (self.goal.rect.width/2, self.goal.rect.height/2)
		self.goal.position = (400, 550)
		self.goal.color = sf.Color.WHITE
		self.init(*args)

	def init(self):
		raise NotImplementedError

	def _update(self, cursor, time):
		opacity(self.goal, (1-(self.state.total/35))*255)
		self.update(cursor, time)

	def update(self, cursor, time):
		raise NotImplementedError

	def render(self, target):
		for item in self.to_render:
			try:
				target.draw(item)
			except TypeError:
				item.draw(target)
		for item in self.objects:
			item.draw(target)
		if self.player:
			self.player.draw(target)
		target.draw(self.goal)

	def handle_event(self, event):
		raise NotImplementedError

	def finish(self, next, *args):
		self.next = next(self.state, *args)
		self.finished = True

class Intro(Scene):
	def init(self):
		self.title_img = sf.Texture.load_from_file(bytes(os.path.join("assets", "title.png"), 'UTF-8'))
		self.logo_img = sf.Texture.load_from_file(bytes(os.path.join("assets", "logo.png"), 'UTF-8'))
		self.title = sf.Sprite(self.title_img)
		self.logo = sf.Sprite(self.logo_img)
		self.logo.position = (575, 0)
		self.title.position = (740, 8)
		self.logo.color = sf.Color(255, 255, 255, 1)
		self.title.color = sf.Color(255, 255, 255, 1)
		self.fadein = True

		self.titletime = 0
		self.logoalpha = 1

		self.done = False

		self.player_img = sf.Texture.load_from_file(bytes(os.path.join("assets", "you.png"), 'UTF-8'))
		self.player_sprite = sf.Sprite(self.player_img)
		self.player_sprite.origin = (self.player_sprite.width/2, self.player_sprite.height)
		self.player_sprite.position = (60, 500)

		self.to_render = [self.title, self.logo, self.player_sprite]

	def update(self, cursor, time):
		if self.titletime > 5200:
			if not self.done:
				opacity(self.title, 255)
				cursor.image = "interact"
				cursor.caption = "Begin"
		else:
			if self.logoalpha > 0:
				if self.fadein:
					self.logoalpha += time*0.15
					if self.logoalpha > 255:
						self.logoalpha = 255
						self.fadein = False
				else:
					self.logoalpha -= time*0.1
				if self.logoalpha < 0:
					self.logoalpha = 0
				opacity(self.logo, self.logoalpha)
				self.logo.y += time*0.05
			else:
				self.titletime += time
				if self.titletime <= 1000:
					opacity(self.title, 255)
				if self.titletime <= 2000:
					opacity(self.title, 0)
				elif self.titletime < 3000:
					opacity(self.title, 255)
				elif self.titletime < 3500:
					opacity(self.title, 0)
				elif self.titletime < 4000:
					opacity(self.title, 255)
				elif self.titletime < 4900:
					opacity(self.title, 0)

	def handle_event(self, cursor, event):
		if (event.type == sf.Event.KEY_PRESSED or 
		   event.type == sf.Event.MOUSE_BUTTON_RELEASED):
			self.finish(Street)

class Endgame(Scene):
	def init(self, win, messages=None):

		if win:
			messages = ["Well done, you managed to"]
			self.player_img = sf.Texture.load_from_file(bytes(os.path.join("assets", "drink.png"), 'UTF-8'))
		else:
			self.player_img = sf.Texture.load_from_file(bytes(os.path.join("assets", "you.png"), 'UTF-8'))

		self.player_sprite = sf.Sprite(self.player_img)
		self.player_sprite.origin = (self.player_sprite.width/2, self.player_sprite.height)
		self.player_sprite.position = (60, 500)
		msg_texts = []

		i = 0

		for message in messages:
			i = i + 40
			text = sf.Text(message, sf.Font.DEFAULT_FONT, 25)
			text.color = sf.Color.WHITE
			text.origin = (text.rect.width/2, text.rect.height/2)
			text.position = (400, i)
			msg_texts.append(text)

		self.to_render = [self.player_sprite]
		self.to_render.extend(msg_texts)

		if self.state.achievements["Girlfriend"]:
			self.her_img = sf.Texture.load_from_file(bytes(os.path.join("assets", "herdrink.png"), 'UTF-8'))
			self.her_sprite = sf.Sprite(self.her_img)
			self.her_sprite.origin = (self.her_sprite.width/2, self.her_sprite.height)
			self.her_sprite.position = (125, 500)
			self.to_render.append(self.her_sprite)

		if self.state.achievements["Father"]:
			self.him_img = sf.Texture.load_from_file(bytes(os.path.join("assets", "him.png"), 'UTF-8'))
			self.him_sprite = sf.Sprite(self.him_img)
			self.him_sprite.origin = (self.him_sprite.width/2, self.him_sprite.height)
			self.him_sprite.position = (180, 500)
			self.to_render.append(self.him_sprite)

	def update(self, cursor, time):
		cursor.image = "interact"
		cursor.caption = "Fin"

	def handle_event(self, cursor, event):
		if (event.type == sf.Event.KEY_PRESSED or
		   event.type == sf.Event.MOUSE_BUTTON_RELEASED):
			raise Quit

class Area(Scene):

	def init(self, start=60):
		self.time = 0
		self.to_render.append(self.state.stats)
		self.player = entities.Player(start)
		self.to_render.append(self.player)

		self.text = sf.Text(self.__class__.__name__, sf.Font.DEFAULT_FONT, 30)
		self.text.position = (25, 20)
		self.letterbox = (sf.Shape.rectangle(0, 0, 800, 100, sf.Color.BLACK),
		    sf.Shape.rectangle(0, 500, 800, 100, sf.Color.BLACK))

		self.fade = "in"
		self.fadespeed = 0.3
		self.fadetarget = None
		self.faderect = sf.Shape.rectangle(0, 0, 800, 600, sf.Color.BLACK)

	def render(self, target):
		Scene.render(self, target)
		target.draw(self.letterbox[0])
		target.draw(self.letterbox[1])
		target.draw(self.text)
		target.draw(self.faderect)
		target.draw(self.goal)

	def fadeout(self, target, *args):
		self.faderect.color = sf.Color(0, 0, 0, 0)
		self.fade = "out"
		cantbelievethereisntaneasierwaytodothis = [target]
		cantbelievethereisntaneasierwaytodothis.extend(list(args))
		self.fadetarget = tuple(cantbelievethereisntaneasierwaytodothis)

	def update(self, cursor, time):
		if self.fade == "out":
			opacity(self.faderect, time*self.fadespeed, True)
			if opacity(self.faderect) == 255:
				self.finish(*self.fadetarget)
		elif self.fade == "in":
			opacity(self.faderect, time*-self.fadespeed, True)
			if opacity(self.faderect) == 0:
				self.fade = None

		self.time += time

		self.player.update(time)
		self.state.stats.update(time)

		cursor.caption = ""

		if cursor.position[0] >= self.player.x:
			cursor.image = "right"
		else:
			cursor.image = "left"

		for object in self.objects:
			object.update(time)
			if object.interactive and object.contains(cursor.position):
				cursor.image = "interact"
				try:
					cursor.caption = object.name+": "+object.interactive
				except AttributeError:
					cursor.caption = object.__class__.__name__+": "+object.interactive

	def handle_event(self, cursor, event):
		for object in self.objects:
			if object.handle_event(self, cursor, event):
				return True
		return self.player.handle_event(self, cursor, event)

class Street(Area):

	def init(self, begin=60):
		Area.init(self, begin)
		self.objects.append(entities.College(125))
		self.objects.append(entities.JobCentre(350, self))
		self.objects.append(entities.Gym(600))
		self.objects.append(entities.Boundary("right", City))
		for i in range(0, random.randint(0, 10)):
			self.objects.append(entities.Person(random.randint(-20, 820)))
			
	def update(self, cursor, time):
		Area.update(self, cursor, time)
		if self.time > 500:
			if random.random() > 0.5:
				self.objects.append(entities.Person(random.choice([-20, 820])))
			self.time = 0

	def handle_event(self, cursor, event):
		Area.handle_event(self, cursor, event)

class City(Area):

	def init(self, begin=60):
		Area.init(self, begin)
		self.objects.append(entities.DrugDealer(100))
		self.objects.append(entities.Bar(300))
		self.objects.append(entities.EstateAgent(500, self))
		self.house = entities.House(700, self)
		self.objects.append(self.house)
		self.objects.append(entities.Boundary("left", Street))
		for i in range(0, random.randint(0, 10)):
			self.objects.append(entities.Person(random.randint(-20, 820)))

	def update(self, cursor, time):
		Area.update(self, cursor, time)
		if self.time > 500:
			if random.random() > 0.5:
				self.objects.append(entities.Person(random.choice([-20, 820])))
			self.time = 0

	def handle_event(self, cursor, event):
		Area.handle_event(self, cursor, event)

class Bar(Area):

	def init(self, begin=60):
		Area.init(self, begin)
		self.objects.append(entities.BarInside(400))
		if not self.state.achievements["Girlfriend"]:
			self.her = entities.Her(700, self)
			self.her.sprite.flip_x(True)
			self.objects.append(self.her)
		self.objects.append(entities.Boundary("left", City, 300))
		for i in range(0, random.randint(0, 4)):
			self.objects.append(entities.Person(random.randint(-20, 820), True, (0, 0.05)))

	def update(self, cursor, time):
		Area.update(self, cursor, time)
		if self.time > 2000:
			if random.random() > 0.75:
				self.objects.append(entities.Person(random.choice([-20, 820]), True, (0.01, 0.05)))
			self.time = 0

	def handle_event(self, cursor, event):
		Area.handle_event(self, cursor, event)

class House(Area):
	def init(self, begin=60):
		Area.init(self, begin)
		self.objects.append(entities.TV(600))
		self.objects.append(entities.Bed(200))
		self.objects.append(entities.Fridge(350, self))
		if self.state.achievements["Girlfriend"]:
			self.her = entities.Her(475, self)
			self.her.sprite.flip_x(True)
			self.objects.append(self.her)
		if self.state.achievements["Father"]:
			self.him = entities.Him(425)
			self.him.sprite.flip_x(True)
			self.objects.append(self.him)
		self.objects.append(entities.Boundary("left", City, 700))

	def update(self, cursor, time):
		Area.update(self, cursor, time)

	def handle_event(self, cursor, event):
		Area.handle_event(self, cursor, event)
