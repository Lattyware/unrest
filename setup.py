"""
This setup script is designed to freeze the game into an stand-alone executable
without any dependancies. It is NOT needed to run the game. Just do ./unrest.py
- or go and download your appropriate binary version created using this.

Before running, please check the value of PLATFORM below.
"""

from cx_Freeze import setup, Executable

################################################################################

PLATFORM = "POSIX"
#PLATFORM = "WIN32"

################################################################################

includes = ["re"]
includefiles = ["assets", "README", "COPYING"]

if PLATFORM == "WIN32":
	exe = Executable(
		script="unrest.py",
		base="Win32GUI",
		icon="assets/unrest-icon.ico",
	)
else:
	exe = Executable(
		script="unrest.py",
		icon="assets/unrest-icon.png",
	)

setup(
	name = "unrest",
	version = "1.0",
	author = "Gareth Latty",
	author_email = "gareth@lattyware.co.uk",
	url = "http://www.lattyware.co.uk/projects/unrest",
	description = "A game in which you must escape from helplessness.",
	platforms = ["POSIX", "WIN32"],
	license = "GPL3",
	executables = [exe],
	options = {
		"build_exe": {
			"includes": includes,
			'include_files': includefiles,
		},
	},
)