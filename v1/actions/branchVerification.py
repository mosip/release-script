from classes.repoInfo import RepoInfo
from paths import verifyBranchResult, repoListDataPath
from utils import myprint, write_json_file, get_json_file, CommandOutput
import config as conf


class BranchVerification:

    def __init__(self):
        self.repos = self.fetchRepoList()

    def fetchRepoList(self):
        repos = get_json_file(repoListDataPath)
        myprint("List of repos")
        myprint(repos)
        return repos

    # git ls-remote --heads <repo url> <branch> | wc -l
    def checkIfBranchExists(self, repo):
        r = CommandOutput('git ls-remote --heads ' + repo + ' ' + conf.branch_name + ' --single-branch | wc -l')
        if r.strip() == "1":
            return True
        else:
            return False

    def verifyBranches(self):
        output = []
        for repo in self.repos:
            myprint('Verifying branch '+conf.branch_name+' repo for '+repo, 2)
            has_branch = self.checkIfBranchExists(repo)
            if has_branch:
                myprint(conf.branch_name + " branch exists", 12)
            else:
                myprint(conf.branch_name + " branch does not exist", 11)
            output.append(RepoInfo(repo, conf.branch_name).set_branch_found(has_branch).__dict__)
        write_json_file(verifyBranchResult, output)
