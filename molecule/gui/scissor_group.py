from pyglet import gl
from pyglet.graphics import Group

class ScissorGroup(Group):
    def __init__(
        self, x: int, y: int, width: int, height: int, parent: Group | None = None
    ) -> None:
        super().__init__(parent=parent)
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    def set_state(self) -> None:
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(self.x, self.y, self.width, self.height)

    def unset_state(self) -> None:
        gl.glDisable(gl.GL_SCISSOR_TEST)

    def __eq__(self, other: object) -> bool:
        return self is other

    def __hash__(self) -> int:
        return id(self)
