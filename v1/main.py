import argparse
import sys
import traceback

from dotenv import load_dotenv

from paths import envPath

load_dotenv()

# OR, the same with increased verbosity
load_dotenv(verbose=True)

load_dotenv(dotenv_path=envPath)

from actions.checkout import Checkout
from utils import init_logger, myprint





def args_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='checkout|all')
    args = parser.parse_args()
    return args, parser


def main():
    args, parser = args_parse()

    init_logger('./out.log')
    try:
        if args.action == 'checkout' or args.action == 'all':
            myprint("Action: checkout", 1)
            Checkout()

    except:
        formatted_lines = traceback.format_exc()
        myprint(formatted_lines, 13)
        sys.exit(1)

    return sys.exit(0)


if __name__ == "__main__":
    main()
