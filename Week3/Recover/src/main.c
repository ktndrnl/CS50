#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

bool is_jpg_header(uint8_t block[]);

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }

    FILE *raw_file = fopen(argv[1], "r");
    if (!raw_file)
    {
        printf("Unable to open file \"%s\"\n", argv[1]);
        return 1;
    }

    uint8_t buffer[512] = "\0";

    int file_number = 0;
    char filename[8] = "\0";
    FILE *img = NULL;
    bool file_open = false;
    int bytes_in_block = fread(buffer, 1, 512, raw_file);

    while (bytes_in_block == 512)
    {
        if (is_jpg_header(buffer))
        {
            if (img)
            {
                fclose(img);
            }
            sprintf(filename, "%03i.jpg", file_number++);
            img = fopen(filename, "w");
            file_open = true;
        }
        if (file_open)
        {
            fwrite(buffer, 1, 512, img);
        }

        bytes_in_block = fread(buffer, 1, 512, raw_file);
    }
}

bool is_jpg_header(uint8_t block[])
{
    if (block[0] == 0xff && block[1] == 0xd8 &&
        block[2] == 0xff && (block[3] & 0xf0) == 0xe0)
    {
        return true;
    }
    else
    {
        return false;
    }
}