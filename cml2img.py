# Molecule - a chemical reaction puzzle game
# Copyright (C) 2013 Simon Norberg <simon@pthread.se>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import getopt
import sys
import pygame
from molecule.Molecule import Molecule

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "input=", "output=",])
	except getopt.GetoptError as err:
		print(str(err))
		self.cmd_help()
		sys.exit(2)
	input = None
	output = None
	for o,a in opts:
		print("getops, debug", o, a)
		if o in ("-h", "--help"):
			cmd_help()
			sys.exit()
		elif o in ("-i", "--input"):
			input = a
		elif o in ("-o", "--output"):
			output = a
	if input is None or output is None:
		cmd_help()
		sys.exit()
	convert_cml2png(input, output)

def convert_cml2png(input, output): 
	#TODO: move sprite generation from Molecule
	img = Molecule("H2O(g)").cml2Sprite(input)
	pygame.image.save(img, output)

def cmd_help():
	print("cml2img.py -i <cmlfile> -o <pngfile>")

if __name__ == "__main__":
	main()
