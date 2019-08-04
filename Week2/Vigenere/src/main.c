#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int shift(char k, char p);

int main(int argc, string argv[]) 
{
    if (argc < 2)
    {
        printf("Usage: ./vigenere keyword\n");
        return 1;
    }

    int keyword_len = strlen(argv[1]);
    char keyword[keyword_len + 1];
    keyword[keyword_len] = '\0';
    for (int i = 0; i < keyword_len; i++)
    {
        if (isalpha(argv[1][i]) == 0)
        {
            printf("Usage: ./vigenere keyword\n");
            return 1;
        }
        
        keyword[i] = argv[1][i];
    }
    
    string plaintext = get_string("plaintext: ");
    int plaintext_len = strlen(plaintext);
    char ciphertext[plaintext_len + 1];
    ciphertext[plaintext_len] = '\0';

    for (int i = 0, j = 0; i < plaintext_len; i++)
    {
        if (j >= keyword_len)
        {
            j = 0;
        }

        char p = plaintext[i];
        char k = keyword[j];
        if (isalpha(p) != 0)
        {
            int key = shift(k, p);
            ciphertext[i] = (p + key);
            j++;
        }
        else
        {
            ciphertext[i] = p;
        }	
    }

    printf("ciphertext: %s\n", ciphertext);
    
    return 0;
}

// Find shift amount
// ex: shift(keyword char "Z", plaintext char "y")
// "Z" or "z" represents a +25 shift, shifting beyond the end of alphabet will return
// negative shift in order to wrap around
int shift(char k, char p)
{
    int start = *"A";
    int end = *"Z";

    int shift = toupper(k) - start;
    char upper_p = toupper(p);
    if (upper_p + shift > end)
    {
        shift = (upper_p - (start + shift - 1 - (end - upper_p))) * -1;
        //shift = (end - upper_p + shift) % -26;
    }
    
    return shift;
}