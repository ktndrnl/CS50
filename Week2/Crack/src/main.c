#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <crypt.h>

#define TRUE 1
#define FALSE 0

#define HASH_LENGTH 13 
#define SALT_LENGTH 3 
#define MAX_PWD_LEN 5

int crack(int pos, int len, char *brute, char *hash, char *salt);

int main(int argc, string argv[])
{
    if (argc < 2 || argc > 2)
    {
        printf("One password hash required as argument \nEx: ./crack 50cI2vYkF0YU2\n");
        return 1;
    }
    if (strlen(argv[1]) != HASH_LENGTH)
    {
        printf("Password hash is of incorrect length\n");
        return 1;
    }

    // For all string arrays, an extra index is added for the null character '\0'

    // Create and fill hash char array with chars from hash given as argument.
    char hash[HASH_LENGTH + 1] = "\0";
    for (int i = 0; i < HASH_LENGTH; i++)
    {
        hash[i] = argv[1][i];
    }

    // Create and fill salt char array with first two elements of hash array 
    // (the salt is the first two chars of the hash)
    char salt[SALT_LENGTH + 1] = "\0";
    salt[0] = (char)hash[0];
    salt[1] = (char)hash[1];

    // Create char array that will be used to store the bruteforced string
    char brute[MAX_PWD_LEN + 1] = "\0";

    // Try all possible passwords at each length up to the MAX_PWD_LEN
    for (int current_length = 0; current_length <= MAX_PWD_LEN; current_length++)
    {
        if (crack(0, current_length, brute, hash, salt))
        {
            printf("%s\n", brute);
            return 0;
        }
    }
}

// Recursive function that takes in the pointers to the original hash and salt,
// a pointer to the array that will contain the bruteforced password and the current
// position in that array, as well as the length of the password to generate.
// Modified version of: https://c-for-dummies.com/blog/?p=1809
int crack(int pos, int len, char *brute, char *hash, char *salt)
{
    char c;

    // Check if the current string in *brute is of the correct length
    if (pos == len)
    {
        // Hash the current bruteforced password using the original salt and see
        // if it matched the original hash
        char *brute_hash = crypt(brute, salt);
        if (strcmp(hash, brute_hash) == 0)
        {
            //printf("%s -> %s\n", brute, hash);
            return (TRUE);
        }
        else
        {
            return (FALSE);
        }
    }
    else
    {
        for (c = 'A'; c <= 'z' ; c++)
        {
            // If reached the end of capital ASCII characters, move c to the begining
            // of lowercase characters
            if (c == *"[")
            {
                c = *"a";
            }
            
            brute[pos] = c;
            //printf("\r%s", brute);
            //fflush(stdout);
            pos++;
            if (crack(pos, len, brute, hash, salt))
            {
                return (TRUE);
            }
            pos--;
        }
    }
    return (FALSE);
}