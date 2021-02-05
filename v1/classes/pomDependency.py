class PomDependency:

    def __init__(self, _group_id, _artifact_id, _version):
        self._group_id = _group_id
        self._artifact_id = _artifact_id
        self._version = _version

    @property
    def group_id(self):
        return self._group_id

    @property
    def artifact_id(self):
        return self._artifact_id

    @property
    def version(self):
        return self._version
