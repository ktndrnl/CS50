// Implements a dictionary's functionality

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "dictionary.h"

// Represents number of children for each node in a trie
#define N 27

// Represents a node in a trie
typedef struct node
{
    bool is_word;
    struct node *children[N];
}
node;

// Represents a trie
node *root;

unsigned int trie_size(const node *root_node);
void unload_trie(node *root_node);

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize trie
    root = malloc(sizeof(node));
    if (root == NULL)
    {
        return false;
    }
    root->is_word = false;
    for (int i = 0; i < N; i++)
    {
        root->children[i] = NULL;
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

    // Insert words into trie
    while (fscanf(file, "%s", word) != EOF)
    {
        int word_len = strlen(word);
        node *ptr = root;
        for (int i = 0; i < word_len; i++)
        {
            int index = word[i] == '\'' ? 26 : tolower(word[i]) - 'a';
            if (ptr->children[index] == NULL)
            {
                node *child_node = calloc(1, sizeof(node));
                if (!child_node)
                {
                    unload();
                    return false;
                }
                ptr->children[index] = child_node;
                child_node->is_word = i == word_len - 1;
                
                ptr = child_node;
            }
            else
            {
                ptr = ptr->children[index];
                ptr->is_word = ptr->is_word ? true : i == word_len - 1;
            }
        }
    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    int size = trie_size(root);

    return size;
}

unsigned int trie_size(const node *root_node)
{
    unsigned int size = 0;
    for (int i = 0; i < N; i++)
    {
        if (root_node->children[i])
        {
            size += trie_size(root_node->children[i]);
        }
    }
    if (root_node->is_word)
    {
        size += 1;
    }

    return size;
}

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    node *ptr = root;

    while (*word)
    {
        ptr = ptr->children[*word == '\'' ? 26 : tolower(*word) - 'a'];
        if (!ptr)
        {
            return false;
        }
        word++;
    }

    if (ptr->is_word)
    {
        return true;
    }
    
    return false;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    unload_trie(root);
    return true;
}

void unload_trie(node *root_node)
{
    for (int i = 0; i < N; i++)
    {
        if (root_node->children[i])
        {
            unload_trie(root_node->children[i]);
        }
    }

    free(root_node);
}
