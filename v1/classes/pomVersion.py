class PomVersion:

    def __init__(self, _module, _parent):
        self._module = _module
        self._parent = _parent

    @property
    def module(self):
        return self._module

    @property
    def parent(self):
        return self._parent

    def set_module(self, v):
        self._module = v
        return self

    def set_parent(self, v):
        self._parent = v
        return self
