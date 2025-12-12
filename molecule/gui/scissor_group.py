from pyglet import gl
from pyglet.graphics import Group

class ScissorGroup(Group):
    def __init__(self, x, y, width, height, parent=None):
        super().__init__(parent=parent)
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    def set_state(self):
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(self.x, self.y, self.width, self.height)

    def unset_state(self):
        gl.glDisable(gl.GL_SCISSOR_TEST)

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)
