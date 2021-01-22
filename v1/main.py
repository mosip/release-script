import argparse
import sys
import traceback
from paths import envPath, logPath
from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity
load_dotenv(verbose=True)

load_dotenv(dotenv_path=envPath)

from actions.commit import Commit
from actions.push import Push
from actions.build import Build
from actions.branchVerification import BranchVerification
from actions.cleanup import Cleanup
from actions.dependency import Dependency
from actions.checkout import Checkout
from utils import init_logger, myprint


def args_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='cleanup|checkout|all')
    args = parser.parse_args()
    return args, parser


def main():
    args, parser = args_parse()

    init_logger(logPath)
    try:
        if args.action == 'cleanup' or args.action == 'all':
            myprint("Action: cleanup", 1)
            Cleanup()

        if args.action == 'verify_branch' or args.action == 'all':
            myprint("Action: verify branch (check if branch exists or not)", 1)
            BranchVerification().verifyBranches()

        if args.action == 'checkout' or args.action == 'all':
            myprint("Action: checkout", 1)
            Checkout().checkoutRepos()

        if args.action == 'dependency_check' or args.action == 'all':
            myprint("Action: dependency check (whether repo contains older dependencies)", 1)
            Dependency().pomCheck()

        if args.action == 'dependency_update' or args.action == 'all':
            myprint("Action: dependency update (update the dependency with release name)", 1)
            Dependency().depUpdate()

        if args.action == 'build' or args.action == 'all':
            myprint("Action: build", 1)
            Build().build()

        if args.action == 'commit' or args.action == 'all':
            myprint("Action: commit", 1)
            Commit().commitRepos()

        if args.action == 'push' or args.action == 'all':
            myprint("Action: push", 1)
            Push().pushRepos()

    except:
        formatted_lines = traceback.format_exc()
        myprint(formatted_lines, 13)
        sys.exit(1)

    return sys.exit(0)


if __name__ == "__main__":
    main()
