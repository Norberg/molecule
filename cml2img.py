import getopt
import sys
import pygame
from molecule.Molecule import Molecule

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "input=", "output=",])
	except getopt.GetoptError as err:
		print str(err)
		self.cmd_help()
		sys.exit(2)
	input = None
	output = None
	for o,a in opts:
		print "getops, debug", o, a
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
	img = Molecule(None, None).cml2Sprite(input)
	pygame.image.save(img, output)

def cmd_help():
	print "cml2img.py -i <cmlfile> -o <pngfile>"

if __name__ == "__main__":
	main()
