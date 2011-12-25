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

import sys
import random
import os

import sf

import scenes
from interface import Cursor
from interface import Stats

class Quit(Exception):
	pass

class LeeroyJenkins:

	def __init__(self, name):
		random.seed()
		video_mode = sf.VideoMode(800, 600, 32)
		style = sf.Style.CLOSE
		self.window_image = sf.Image.load_from_file(bytes(os.path.join("assets", "you.png"), 'UTF-8'))
		self.window = sf.RenderWindow(video_mode, bytes(name, 'UTF-8'), style)
		self.window.set_icon(40, 40, self.window_image.get_pixels())
		self.window.framerate_limit = 60
		self.window.show_mouse_cursor = False
		self.state = State()
		self.scene = scenes.Intro(self.state)
		self.cursor = Cursor()
		self.pause_img = sf.Texture.load_from_file(bytes(os.path.join("assets", "paused.png"), 'UTF-8'))
		self.pause_sprite = sf.Sprite(self.pause_img)
		self.pause = False
		self.run()
		
	def run(self):
		while True:
			try:
				self.step()
			except Quit:
				self.window.close()
				sys.exit()

	def step(self):
		if self.scene.finished:
			self.scene = self.scene.next
		self.handle_events()
		if not self.pause:
			self.update()
		self.render()

	def handle_events(self):
		for event in self.window.iter_events():
			if event.type == sf.Event.CLOSED or (event.type ==
			    sf.Event.KEY_PRESSED and event.code == sf.Keyboard.ESCAPE):
				self.quit()
			elif (event.type == sf.Event.KEY_PRESSED and
			      event.code == sf.Keyboard.P):
				self.pause = not self.pause
			elif event.type == sf.Event.MOUSE_BUTTON_RELEASED and self.pause:
				self.pause = False
			elif event.type == sf.Event.LOST_FOCUS:
				self.pause = True
			elif event.type == sf.Event.GAINED_FOCUS:
				self.pause = False
			elif not self.pause:
				self.scene.handle_event(self.cursor, event)

	def render(self):
		self.window.clear(sf.Color.BLACK)
		self.scene.render(self.window)
		self.cursor.draw(self.window)
		if self.pause:
			self.window.draw(self.pause_sprite)
		self.window.display()

	def update(self):
		self.scene._update(self.cursor, self.window.frame_time)
		self.cursor.position = sf.Mouse.get_position(self.window)

	def quit(self):
		raise Quit

class State:
	def __init__(self):
		self.achievements = {
			"Educated": False,
			"Have Home": False,
		    "Girlfriend": False,
			"Father": False,
		}

		self.issues = {
			"Poor": 5,
			"Uneducated": 10,
			"Stressed": 0,
			"Overweight": 5,
			"Guilty": 0,
			"Bored": 3,
			"Lonely": 6,
			"Addiction": 1,
		}

		self.stats = Stats(self)

	def _get_total(self):
		total = 0
		for count in self.issues.values():
			total += count
		return total

	total = property(_get_total)

	def increase(self, scene, name, amount=1):
		self.issues[name] += amount
		self.stats.show(name)
		self.check_victory(scene)

	def decrease(self, scene, name, amount=1):
		self.issues[name] -= amount
		if self.issues[name] < 1:
			self.issues[name] = 0
			self.stats.hide(name)

		if self.issues["Uneducated"] == 0:
			self.achievements["Educated"] = True

		self.check_victory(scene)

	def check_victory(self, scene):
		if self.total == 0:
			scene.finish(scenes.Endgame, True)
		else:
			if self.issues["Poor"] > 10:
				scene.finish(scenes.Endgame, False, ["With no money,", "hopelessness set in,", "and you took your own life."])
			elif self.issues["Stressed"] > 10:
				scene.finish(scenes.Endgame, False, ["Hopelessly stressed,", "you could no longer take living,", "and took your own life."])
			elif self.issues["Overweight"] > 10:
				scene.finish(scenes.Endgame, False, ["You died due to a", "hopelessly unhealthy lifestyle."])
			elif self.issues["Bored"] > 10:
				scene.finish(scenes.Endgame, False, ["Hopelessly bored with life,", "you saw no reason to go on."])
			elif self.issues["Lonely"] > 10:
				scene.finish(scenes.Endgame, False, ["Hopelessly lonely,", "you saw no reason to go on."])
			elif self.issues["Addiction"] > 10:
				scene.finish(scenes.Endgame, False, ["Your addictions lead you", "to a to die a hopeless death", "desperately seeking a fix."])
			elif self.total > 35:
				scene.finish(scenes.Endgame, False, ["Your life became hopeless", "as your issues built up,", "you saw no reason to go on."])

def opacity(obj, change=None, relative=False):
	col = obj.color
	if change == None:
		return col.a
	if relative:
		if col.a + change > 255:
			col.a = 255
		elif col.a + change < 0:
			col.a = 0
		else:
			col.a += change
	else:
		if change > 255:
			col.a = 255
		elif change < 0:
			col.a = 0
		else:
			col.a = change
	obj.color = col

if __name__ == "__main__":
	lets_do_this = LeeroyJenkins("Unrest")
