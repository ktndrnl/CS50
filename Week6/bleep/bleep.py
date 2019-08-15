from cs50 import get_string
from sys import argv


def main():
    if len(argv) != 2:
        print("Usage: bleep [banned words file]")
        exit(1)

    banned_words = {w.rstrip('\n') for w in open(argv[1], "r")}

    message = get_string("What message would you like to censor?\n").split(' ')
    print(' '.join(["*" * len(w) if w.lower() in banned_words else w for w in message]))


if __name__ == "__main__":
    main()
