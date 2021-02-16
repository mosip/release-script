import json

from utils import getRepoNameFromUrl


class RepoInfo:

    def __init__(self, _repo, _branch, _repo_path=None, _repo_short=None, _branch_found=None,
                 _pom_info=None, _pom_stats=None, _is_pom_outdated=None, _parent_poms=[], _pom_version=[], _trigger_info=[]):
        self._repo = _repo
        self._repo_short = getRepoNameFromUrl(_repo)
        self._branch = _branch
        self._repo_path = _repo_path
        self._branch_found = _branch_found
        self._pom_info = _pom_info
        self._pom_stats = _pom_stats
        self._is_pom_outdated = _is_pom_outdated
        self._parent_poms = []
        self._pom_version = []
        self._trigger_info = _trigger_info

    @property
    def repo(self):
        return self._repo

    @property
    def repo_short(self):
        return self._repo_short

    @property
    def branch(self):
        return self._branch

    @property
    def repo_path(self):
        return self._repo_path

    @property
    def branch_found(self):
        return self._branch_found

    @property
    def pom_stats(self):
        return self._pom_stats

    @property
    def pom_info(self):
        return self._pom_info

    def set_branch_found(self, v):
        self._branch_found = v
        return self

    def set_repo_path(self, v):
        self._repo_path = v
        return self

    def set_pom_info(self, v):
        self._pom_info = v
        return self

    def set_pom_stats(self, v):
        self._pom_stats = v
        return self

    def set_is_pom_outdated(self, v):
        self._is_pom_outdated = v
        return self

    def set_parent_poms(self, v):
        self._parent_poms = v
        return self

    def set_pom_version(self, v):
        self._pom_version = v
        return self

    def set_trigger_info(self, v):
        self._trigger_info = v
        return self

    def toJSON(self, sort=False, indent=4):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=sort, indent=indent)
