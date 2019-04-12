import sys
from controller import actions

# TODO check input

if __name__ == '__main__':
    getattr(actions, sys.argv[1].replace('-', '_'))(*sys.argv[2:])
