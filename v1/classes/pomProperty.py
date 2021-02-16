class PomProperty:

    def __init__(self, _name, _version):
        self._name = _name
        self._version = _version

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version
