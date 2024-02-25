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

import pyglet
from pyglet import gl
from molecule.Elements import Molecule

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:o:", ["help", "formula=", "output=",])
    except getopt.GetoptError as err:
        print(str(err))
        cmd_help()
        sys.exit(2)
    input = None
    output = None
    for o,a in opts:
        if o in ("-h", "--help"):
            cmd_help()
            sys.exit()
        elif o in ("-f", "--formula"):
            input = a
        elif o in ("-o", "--output"):
            output = a
    if input is None or output is None:
        cmd_help()
        sys.exit()
    convert_cml2png(input, output)

def convert_cml2png(formula, output): 
    space = SpaceMock()
    batch = pyglet.graphics.Batch()
    img = Molecule(formula, space, batch, pos=(50,50), render_only=True)
    w, h, _ = img.cml.max_pos()
    width = int(w*64) + 64 + 36
    height = int(h*64) + 64 + 36
    config = gl.Config(double_buffer=True)
    window = pyglet.window.Window(width=width,height=height,visible=True,config=config)
    window.minimize()
    gl.glClearColor(250/256.0, 250/256.0, 250/256.0, 0)
    gl.glLineWidth(4)
    gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
    img.update()
    @window.event
    def on_draw():
        window.clear()
        batch.draw()
        pyglet.image.get_buffer_manager().get_color_buffer().save(output)
        #window.close()
        pyglet.app.exit()
    pyglet.app.run()

def cmd_help():
    print("cml2img.py -f formula -o <pngfile>")

class SpaceMock():
    def add(*args):
        pass

if __name__ == "__main__":
    main()
