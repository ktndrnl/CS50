// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include<string.h>

#include "dictionary.h"

// Represents number of buckets in a hash table
#define N 26

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Represents a hash table
node *hashtable[N];

void unload_node(node *ptr);

// Hashes word to a number between 0 and 25, inclusive, based on its first letter
unsigned int hash(const char *word)
{
    return tolower(word[0]) - 'a';
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize hash table
    for (int i = 0; i < N; i++)
    {
        hashtable[i] = NULL;
    }

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];

    // Insert words into hash table
    while (fscanf(file, "%s", word) != EOF)
    {
        node *word_node = malloc(sizeof(node));
        if (!word_node)
        {
            unload();
            return false;
        }
        
        strcpy(word_node->word, word);

        unsigned int word_hash = hash(word);
        word_node->next = hashtable[word_hash];
        hashtable[word_hash] = word_node;
    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    int size = 0;

    for (int i = 0; i < N; i++)
    {
        node *ptr = hashtable[i];
        while (ptr)
        {
            size++;
            ptr = ptr->next;
        }
    }
    
    return size;
}

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    node *ptr = hashtable[hash(word)];
    while (ptr)
    {
        char word_lower[LENGTH + 1] = "\0";

        int i = 0;
        while (word[i] != '\0')
        {
            word_lower[i] = tolower(word[i]);
            i++;  
        }
        
        if (strcmp(word_lower, ptr->word) == 0)
        {
            return true;
        }

        ptr = ptr->next;
    }
    
    return false;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    for (int i = 0; i < N; i++)
    {
        node *ptr = hashtable[i];
        if (ptr)
        {
            unload_node(ptr);
            hashtable[i] = NULL;
        }
    }
    
    return true;
}

void unload_node(node *ptr)
{
    if (!ptr->next)
    {
        free(ptr);
        return;
    }
    else
    {
        unload_node(ptr->next);
        free(ptr);
        return;
    }
}
