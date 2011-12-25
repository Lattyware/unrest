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
import math as maths
import random

import sf

import scenes

class Entity:
	def __init__(self, *args):
		self.interactive = False
		self.init(*args)
		self.image = sf.Texture.load_from_file(bytes(self.image_path, 'UTF-8'))
		self.sprite = sf.Sprite(self.image)
		self.sprite.origin = (self.sprite.width/2, self.sprite.height)
		self.sprite.position = (args[0], 500)
		self.postinit()

	def _set_x(self, x):
		self.sprite.x = x

	def _get_x(self):
		return self.sprite.x

	x = property(_get_x, _set_x)

	def postinit(self):
		pass

	def init(self):
		raise NotImplementedError

	def handle_event(self, scene, cursor, event):
		if event.type == sf.Event.MOUSE_BUTTON_RELEASED:
			if self.contains(cursor.position) and self.interactive and not scene.fade:
				scene.player.set_callback(cursor.x, self.interact, scene)
				return True
		return False
		
	def interact(self, scene):
		raise NotImplementedError
		
	def draw(self, target):
		target.draw(self.sprite)

	def contains(self, point):
		x, y = point
		hx, y2 = self.sprite.position
		x1 = hx-self.sprite.width/2
		x2, y1 = hx+self.sprite.width/2, y2-self.sprite.height
		if x > x1 and y > y1 and x < x2 and y < y2:
			return True
		else:
			return False

	def update(self, time):
		raise NotImplementedError

class Boundary(Entity):
	def init(self, direction, to, frm=None):
		self.name = to.__name__
		self.image_path = os.path.join("assets", direction+".png")
		self.text = sf.Text(to.__name__, sf.Font.DEFAULT_FONT, 20)
		self.direction = direction
		self.interactive = "Go To"
		self.to = to
		self.frm = frm

	def postinit(self):
		if self.direction == "right":
			self.sprite.position = (784, 600)
			self.text.position = (800, 200)
			self.text.rotate(90)
		else:
			self.sprite.position = (16, 600)
			self.text.rotate(-90)
			self.text.position = (0, 200)


	def update(self, time):
		pass

	def interact(self, scene):
		if self.frm:
			begin = self.frm
		else:
			if self.direction == "right":
				begin = 60
			else:
				begin = 740
		scene.finish(self.to, begin)

	def draw(self, target):
		Entity.draw(self, target)
		target.draw(self.text)

class Person(Entity):

	people = [
		os.path.join("assets", "man.png"),
	    os.path.join("assets", "woman.png"),
	    os.path.join("assets", "girl.png"),
	    os.path.join("assets", "boy.png"),
	]

	adults = [
		os.path.join("assets", "man.png"),
	    os.path.join("assets", "woman.png"),
	]

	def init(self, x, adults=False, speeds=(0.05, 0.15)):
		self.speed = random.uniform(*speeds)
		if adults:
			self.image_path = random.choice(self.adults)
		else:
			self.image_path = random.choice(self.people)
		if x < 400:
			self.direction = 1
		else:
			self.direction = -1

	def postinit(self):
		if self.direction == -1:
			self.sprite.flip_x(True)

	def update(self, time):
		self.x += self.direction*self.speed*time
		if self.x < -20 or self.x > 820:
			del(self)

	def _set_x(self, x):
		self.sprite.x = x

	def _get_x(self):
		return self.sprite.x

	x = property(_get_x, _set_x)

class Player(Entity):
	def init(self, x):
		self.target = None
		self.callback = None
		self.speed = 0.3
		self.right = True
		self.image_path = os.path.join("assets", "you.png")
		self.action = False
		self.wait = None
		self.time = 0
				
	def update(self, time):
		if self.action:
			if not self.target:
				if self.wait:
					self.time += time
					if self.time > self.wait:
						self.wait = None
						self.time = 0
				else:
					try:
						call, *args = next(self.action)
						getattr(self, call)(*args)
					except StopIteration:
						self.action = None
		if self.target:
			if maths.fabs(self.x-self.target) <= self.speed*time:
				if self.callback:
					func, args = self.callback
					func(*args)
					self.callback = None
				self.target = None
			else:
				if self.x > self.target:
					mod = -self.speed*time
					self.sprite.flip_x(True)
					self.right = False
				else:
					mod = self.speed*time
					self.sprite.flip_x(not self.right)
					self.right = True
				self.x += mod
										
	def handle_event(self, scene, cursor, event):
		if event.type == sf.Event.MOUSE_BUTTON_RELEASED and not self.action and not scene.fade:
			self.target = cursor.position[0]
			if self.target < 0:
				self.target = 0
			elif self.target > 800:
				self.target = 800
			return True
		else:
			return False

	def perform(self, action):
		self.action = iter(action)
		self.target = None

	def set(self, attr, x):
		#Used for actions.
		setattr(self, attr, x)
		
	def set_other(self, other, attr, x):
		#Used for actions.
		setattr(other, attr, x)

	def call_other(self, other, func, *args):
		#Used for actions.
		getattr(other, func)(*args)

	def change_scene(self, scene, to, *args):
		#Used for actions.
		scene.finish(to, *args)

	def reload(self, scene, *args):
		scene.fadeout(scene.__class__, *args)

	def change_image(self, image):
		pos = self.sprite.x, self.sprite.y
		right = self.right
		self.sprite = sf.Sprite(image)
		self.sprite.x, self.sprite.y = pos
		self.sprite.flip_x(not right)
		#self.sprite.texture = image
		#self.sprite.resize(image.width, image.height)
		self.sprite.origin = (self.sprite.width/2, self.sprite.height)

	def change_other_image(self, other, image):
		pos = other.sprite.x, other.sprite.y
		right = other.right
		other.sprite = sf.Sprite(image)
		other.sprite.x, other.sprite.y = pos
		other.sprite.flip_x(not right)
		#other.sprite.texture = image
		#other.sprite.resize(image.width, image.height)
		other.sprite.origin = (other.sprite.width/2, other.sprite.height)

	def set_callback(self, x, func, *args):
		if not self.action:
			self.callback = (func, args)
			self.target = x

class Her(Entity):
	def init(self, x, scene):
		if scene.state.achievements["Girlfriend"]:
			self.name = "Girlfriend"
		else:
			self.name = "Girl"
		self.speed = 0.3
		if scene.__class__.__name__ == "Bar":
			self.interactive = "Offer A Drink"
		elif scene.state.achievements["Father"]:
			self.interactive = "\"Spend Some Time Together\""
		else:
			self.interactive = "Have A Child"
		self.image_path = os.path.join("assets", "her.png")
		self.target = None
		self.right = True

	def interact(self, scene):
		if scene.__class__.__name__ == "Bar":
			scene.state.increase(scene, "Poor", 1)
			scene.state.decrease(scene, "Lonely", 3)
			scene.state.decrease(scene, "Stressed", 1)
			scene.state.increase(scene, "Addiction", 1)
			pdrink = sf.Texture.load_from_file(bytes(os.path.join("assets", "drink.png"), 'UTF-8'))
			hdrink = sf.Texture.load_from_file(bytes(os.path.join("assets", "herdrink.png"), 'UTF-8'))
			speed = scene.player.speed
			if scene.state.achievements["Have Home"] and \
			   scene.state.issues["Uneducated"] < 8 and scene.state.issues["Overweight"] < 6:
				scene.state.achievements["Girlfriend"] = True
				parts = [
					("set", "speed", speed/3),
					("set_other", self,  "speed", speed/4),
					("set_other", self, "target", 535),
					("set", "target", 460),
					("set", "target", 470),
					("change_other_image", self, hdrink),
					("change_image", pdrink),
					("set", "wait", 4000),
					("set_other", self,  "speed", speed/3),
					("change_image", scene.player.image),
					("change_other_image", self, self.image),
					("set_other", self, "target", 1),
					("set", "target", 1),
					("change_scene", scene, scenes.House)
				]
			else:
				parts = [
					("set", "speed", speed/3),
					("set_other", self,  "speed", speed/4),
					("set_other", self, "target", 535),
					("set", "target", 460),
					("set", "target", 470),
					("change_other_image", self, hdrink),
					("change_image", pdrink),
					("set", "wait", 2000),
					("change_image", scene.player.image),
					("set", "target", 1),
					("change_scene", scene, scenes.City, 300)
				]
			scene.player.perform(parts)
		else:
			speed = scene.player.speed
			if not scene.state.achievements["Father"]:
				scene.state.achievements["Father"] = True
			scene.state.decrease(scene, "Lonely", 3)
			scene.state.decrease(scene, "Stressed", 3)
			scene.state.decrease(scene, "Bored", 1)
			parts = [
					("set", "speed", speed/5),
					("set_other", self,  "speed", speed/3),
					("set_other", self, "target", 175),
					("set", "target", 125),
					("reload", scene),
				]
			scene.player.perform(parts)

	def update(self, time):
		if self.target:
			if maths.fabs(self.x-self.target) <= self.speed*time:
				self.target = None
			else:
				if self.x >= self.target:
					mod = -self.speed*time
					self.sprite.flip_x(True)
					self.right = False
				else:
					mod = self.speed*time
					self.sprite.flip_x(not self.right)
					self.right = True
				self.x += mod
				
class Him(Entity):
	def init(self, x):
		self.name = "Son"
		self.interactive = "Play"
		self.image_path = os.path.join("assets", "him.png")

	def interact(self, scene):
			scene.state.decrease(scene, "Lonely", 2)
			scene.state.decrease(scene, "Stressed", 1)
			scene.state.decrease(scene, "Bored", 1)
			parts = [
				("reload", scene, self.x),
			]
			scene.player.perform(parts)

	def update(self, time):
		pass

class JobCentre(Entity):
	def init(self, x, scene):
		self.name = "Job Centre"
		if scene.state.achievements["Educated"]:
			self.interactive = "Complex Job (Freelance Business Adviser)"
		else:
			self.interactive = "Simple Job (Hand Out Leaflets)"
		self.image_path = os.path.join("assets", "jobcentre.png")

	def interact(self, scene):
		if scene.state.achievements["Educated"]:
			parts = [
				("reload", scene, self.x),
			]
			scene.state.increase(scene, "Stressed", 3)
			scene.state.decrease(scene, "Poor", 5)
			scene.player.perform(parts)
		else:
			x = scene.player.x
			speed = scene.player.speed
			image = sf.Texture.load_from_file(bytes(os.path.join("assets", "leaflets.png"), 'UTF-8'))
			parts = [
				("set", "speed", speed/2),
				("change_image", image),
				("set", "target", x-200),
				("set", "target", x+200),
				("set", "target", x-200),
				("set", "target", x+200),
				("set", "speed", speed),
				("change_image", scene.player.image),
				("set", "target", x),
			]
			scene.state.increase(scene, "Bored", 1)
			scene.state.increase(scene, "Stressed", 1)
			scene.state.decrease(scene, "Poor", 3)
			scene.player.perform(parts)

	def update(self, time):
		pass

class EstateAgent(Entity):
	def init(self, x, scene):
		self.name = "Estate Agent"
		if scene.state.achievements["Have Home"]:
			self.interactive = False
		else:
			self.interactive = "Rent House"
		self.image_path = os.path.join("assets", "estateagent.png")

	def interact(self, scene):
		scene.state.increase(scene, "Poor", 4)
		scene.house.interactive = "Enter House"
		self.interactive = False
		scene.state.achievements["Have Home"] = True
		image = sf.Texture.load_from_file(bytes(os.path.join("assets", "key.png"), 'UTF-8'))
		speed = scene.player.speed
		parts = [
			("change_image", image),
			("set", "speed", speed/4),
			("set", "target", 600),
		    ("change_image", scene.player.image),
			("set", "speed", speed),
			("change_scene", scene, scenes.House),
		]
		scene.player.perform(parts)

	def update(self, time):
		pass

class Bar(Entity):
	def init(self, x):
		self.interactive = "Enter"
		self.image_path = os.path.join("assets", "bar.png")

	def interact(self, scene):
		scene.finish(scenes.Bar)

	def update(self, time):
		pass

class Fridge(Entity):
	def init(self, x, scene):
		self.interactive = "Eat"
		if scene.state.achievements["Father"]:
			self.image_path = os.path.join("assets", "fridgehim.png")
		else:
			self.image_path = os.path.join("assets", "fridge.png")

	def interact(self, scene):
		parts = [
			("reload", scene, self.x),
		]
		scene.state.decrease(scene, "Stressed", 1)
		scene.state.increase(scene, "Overweight", 2)
		scene.player.perform(parts)

	def update(self, time):
		pass

class Gym(Entity):
	def init(self, x):
		self.interactive = "Work Out"
		self.image_path = os.path.join("assets", "gym.png")

	def interact(self, scene):
		parts = [
			("reload", scene, self.x),
		]
		scene.state.increase(scene, "Bored", 2)
		scene.state.increase(scene, "Poor", 1)
		scene.state.decrease(scene, "Overweight", 2)
		scene.player.perform(parts)

	def update(self, time):
		pass

class DrugDealer(Entity):
	def init(self, x):
		self.name= "Drug Dealer"
		self.interactive = "Buy Drugs"
		self.image_path = os.path.join("assets", "drugdealer.png")

	def interact(self, scene):
		parts = [
			("reload", scene, self.x),
		]
		scene.state.increase(scene, "Addiction", 5)
		scene.state.increase(scene, "Poor", 2)
		scene.state.decrease(scene, "Stressed", 4)
		scene.state.decrease(scene, "Bored", 4)
		scene.state.increase(scene, "Guilty", 3)
		scene.player.perform(parts)

	def update(self, time):
		pass

class College(Entity):
	def init(self, x):
		self.interactive = "Take Course"
		self.image_path = os.path.join("assets", "college.png")

	def interact(self, scene):
		parts = [
			("reload", scene, self.x),
		]
		scene.state.decrease(scene, "Uneducated", 3)
		scene.state.increase(scene, "Poor", 2)
		scene.state.increase(scene, "Stressed", 1)
		scene.player.perform(parts)

	def update(self, time):
		pass

class BarInside(Entity):
	def init(self, x):
		self.name = "Bar"
		self.interactive = "Get Drink"
		self.image_path = os.path.join("assets", "barinside.png")

	def interact(self, scene):
		parts = [
			("reload", scene, self.x),
		]
		scene.state.increase(scene, "Addiction", 1)
		scene.state.increase(scene, "Poor", 1)
		scene.state.decrease(scene, "Stressed", 1)
		scene.player.perform(parts)

	def update(self, time):
		pass

class House(Entity):
	def init(self, x, scene):
		if scene.state.achievements["Have Home"]:
			self.interactive = "Enter"
		else:
			self.interactive = False
		self.image_path = os.path.join("assets", "house.png")

	def interact(self, scene):
		scene.finish(scenes.House)

	def update(self, time):
		pass

class TV(Entity):
	def init(self, x):
		self.interactive = "Watch TV"
		self.image_path = os.path.join("assets", "tv.png")

	def interact(self, scene):
		parts = [
			("reload", scene, self.x),
		]
		scene.state.increase(scene, "Lonely", 1)
		scene.state.decrease(scene, "Stressed", 1)
		scene.state.decrease(scene, "Bored", 2)
		scene.player.perform(parts)

	def update(self, time):
		pass

class Bed(Entity):
	def init(self, x, asleep=False):
		self.interactive = "Sleep"
		self.image_path = os.path.join("assets", "bed.png")
		if asleep:
			self.image_path = os.path.join("assets", "beduse.png")

	def interact(self, scene):
		parts = [
			("reload", scene, self.x),
		]
		scene.state.increase(scene, "Lonely", 2)
		scene.state.decrease(scene, "Stressed", 2)
		scene.state.decrease(scene, "Addiction", 1)
		scene.state.decrease(scene, "Guilty", 1)
		scene.player.perform(parts)


	def update(self, time):
		pass

