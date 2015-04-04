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
import sys
import getopt

import pyglet

from molecule import Config

class CliInterface:
    @staticmethod
    def handle_cmd_options():
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hldf",
                ["help", "level=", "debug","fullscreen", "height=", "width=",
                    "zoom="])
        except getopt.GetoptError as err:
            print(str(err))
            CliInterface.cmd_help()
            sys.exit(2)
        for o,a in opts:
            if o in ("-h", "--help"):
                CliInterface.cmd_help()
                sys.exit()
            elif o in ("-l", "--level"):
                Config.current.level = int(a)
            elif o in ("-d", "--debug"):
                Config.current.DEBUG = True
            elif o in ("--fullscreen"):
                Config.current.fullscreen = True
                Config.current.resizable = True
            elif o in ("--width"):
                Config.current.width = int(a)
            elif o in ("--height"):
                Config.current.height = int(a)
            elif o in ("--zoom"):
                Config.current.zoom = float(a)

    @staticmethod
    def cmd_help():
        default = Config.Config()
        print("Molecule - a chemical reaction puzzle game")
        print("-h --help print this help")
        print("--level=LEVEL choose what level to start on")
        print("-d --debug print debug messages")
        print("--fullscreen play in fullscreen mode")
        print("--width size of window, default=%s" % default.width)
        print("--height size of window, default=%s" % default.height)
        print("--zoom scale factor, scale game elements, default=1.0")
        print("During gameplay:")
        print("ESC - close game")
        print("r - reset current level")
        print("d - switch Graphic debug on/off")
        print("s - skip level")
import code, traceback, signal

def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal recieved : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)

def listen():
    signal.signal(signal.SIGUSR1, debug)  # Register handler

def main():
    listen()
    CliInterface.handle_cmd_options()
    from molecule.Game import Game
    game = Game()
    pyglet.app.run()
    print("game finished")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
