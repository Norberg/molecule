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
import os
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
    # Delete old output to avoid showing stale data if something fails
    if os.path.exists(output):
        try:
            os.remove(output)
        except Exception:
            pass

    # 1. Get CML data to calculate window dimensions
    from libcml import CachedCml
    from libreact import Reaction
    formula_only, _ = Reaction.split_state(formula)
    cml = CachedCml.getMolecule(formula_only)
    cml.normalize_pos()
    w, h, _ = cml.max_pos()

    width = int(w*64) + 64 + 36
    height = int(h*64) + 64 + 36

    # 2. Create Window (and OpenGL context)
    config = gl.Config(double_buffer=True)
    window = pyglet.window.Window(width=width, height=height, visible=True, config=config)
    window.minimize()

    # 3. Create graphics objects now that context is active
    gl.glClearColor(250/256.0, 250/256.0, 250/256.0, 0)
    gl.glLineWidth(4)
    gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)

    space = SpaceMock()
    batch = pyglet.graphics.Batch()
    img = Molecule(formula, space, batch, pos=(50,50), render_only=True)
    img.update()

    # Process events and draw
    window.switch_to()
    window.dispatch_events()
    window.clear()
    batch.draw()

    # Ensure all GL commands are executed
    gl.glFlush()

    # Save the buffer
    try:
        pyglet.image.get_buffer_manager().get_color_buffer().save(output)
    finally:
        window.close()

def cmd_help():
    print("cml2img.py -f formula -o <pngfile>")

class SpaceMock():
    def add(*args):
        pass

if __name__ == "__main__":
    main()
