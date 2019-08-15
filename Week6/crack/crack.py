from crypt import crypt
from sys import argv
from sys import stdout
from itertools import product
from string import ascii_letters

def main():
    if len(argv) != 2:
        print("Usage: python crack.py password_hash")
        return 1

    if len(argv[1]) != 13:
        print("Password hash should be 13 characters long.")
        return 1

    pwd_hash = argv[1]
    salt = pwd_hash[0:2]

    print("Trying to brute force short (1-3 characters) passwords")
    for i in range(0, 4):
        for p in product(ascii_letters, repeat=i):
            guess = ''.join(p)
            print(f"\033[K{guess}", end='\r', flush=True)
            if crypt(guess, salt) == pwd_hash:
                print(guess)
                return

    print("Password longer than 3 characters. Trying to find it in dictionary.")
    words = open("pruned_list.txt", "r")
    for word in words:
        word = word.rstrip('\n')
        print(f"\033[K{word}", end='\r', flush=True)
        if crypt(word, salt) == pwd_hash:
            print(word)
            return

        word_list = list(word)
        word_list[0] = word[0].upper()
        word = ''.join(word_list)
        if crypt(word, salt) == pwd_hash:
            print(word)
            return
        
        word = word.upper()
        if crypt(word, salt) == pwd_hash:
            print(word)
            return

    print("Password not found in dictionary. Trying brute force.")
    for i in range(4, 6):
        for p in product(ascii_letters, repeat=i):
            guess = ''.join(p)
            #print(f"\033[K{guess}", end='\r', flush=True)
            if crypt(guess, salt) == pwd_hash:
                print(guess)
                return

    print("Password not found.")

if __name__ == "__main__":
    main()
