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
from random import randint

import sf

class Stats:

	size = 8

	def __init__(self, state):
		self.issues = {}
		self.state = state
		for name, count in state.issues.items():
			if count > 0:
				size = count*self.size
			else:
				size = 0
			item = sf.Text(name.lower(), sf.Font.DEFAULT_FONT, size)
			item.position = (randint(0, 700), randint(0, 600))
			self.issues[name] = item
			if count == 0:
				self.hide(name)
			else:
				self.show(name)

	def hide(self, name):
		self.issues[name].color = sf.Color(255, 255, 255, 0)

	def show(self, name):
		self.issues[name].color = sf.Color(255, 255, 255, 150)

	def update(self, time):
		for name, issue in self.issues.items():
			issue.y += 0.05*time
			if issue.y > 620:
				issue.position = (randint(0, 800), -20)
				count = self.state.issues[name]
				if count > 0:
					size = count*self.size
				else:
					size = 0
				issue.character_size = size

	def draw(self, target):
		for issue in self.issues.values():
			target.draw(issue)

class Menu:
	def __init__(self):
		pass

class Cursor:
	def __init__(self):
		self.images = {
			"skip": sf.Texture.load_from_file(bytes(os.path.join("assets", "cursors", "skip.png"), 'UTF-8')),
		    "go": sf.Texture.load_from_file(bytes(os.path.join("assets", "cursors", "go.png"), 'UTF-8')),
		    "left": sf.Texture.load_from_file(bytes(os.path.join("assets", "cursors", "left.png"), 'UTF-8')),
		    "right": sf.Texture.load_from_file(bytes(os.path.join("assets", "cursors", "right.png"), 'UTF-8')),
		    "interact": sf.Texture.load_from_file(bytes(os.path.join("assets", "cursors", "interact.png"), 'UTF-8')),
		}

		self.cursor = sf.Sprite(self.images["skip"])
		self.current = "skip"
		self.cursor.origin = (self.cursor.width/2, self.cursor.height/2)
		self._caption = sf.Text(b"", sf.Font.DEFAULT_FONT, 10)
		self._caption.color = sf.Color.WHITE

	def _set_position(self, position):
		self.cursor.position = position
		self._caption.position = position

	def _get_position(self):
		return self.cursor.position

	position = property(_get_position, _set_position)

	def _set_x(self, x):
		self.position = (x, self.poisition[1])

	def _get_x(self):
		return self.position[0]

	x = property(_get_x, _set_x)

	def _set_caption(self, caption):
		self._caption.string = caption
		self._caption.origin = (self._caption.rect.width/2, -15)

	def _get_caption(self):
		return self._caption.string

	caption = property(_get_caption, _set_caption)

	def _set_image(self, name):
		self.current = name
		self.cursor.texture = self.images[name]

	def _get_image(self):
		return self.current
 
	image = property(_get_image, _set_image)

	def draw(self, target):
		target.draw(self.cursor)
		target.draw(self._caption)
