// Copies a BMP file

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: resize scale infile outfile\n");
        return 1;
    }

    double scale;
    double *p_scale = &scale;
    *p_scale = round(strtod(argv[1], NULL));
    if (*p_scale <= 0.0 || *p_scale > 100.0)
    {
        printf("Scale must be a number greater than 0 and no greater than 100.\n");
        return 1;
    }

    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    BITMAPFILEHEADER bf_resized = bf;

    BITMAPINFOHEADER bi_resized = bi;
    bi_resized.biWidth = (LONG)(bi.biWidth * scale);
    bi_resized.biHeight = (LONG)(bi.biHeight * scale);

    // determine padding for scanlines
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int padding_resized = (4 - (bi_resized.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    bi_resized.biSizeImage =
        ((sizeof(RGBTRIPLE) * bi_resized.biWidth) + padding_resized)
        * abs(bi_resized.biHeight);

    bf_resized.bfSize = bi_resized.biSizeImage +
                        sizeof(BITMAPFILEHEADER) +
                        sizeof(BITMAPINFOHEADER);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf_resized, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi_resized, sizeof(BITMAPINFOHEADER), 1, outptr);

    RGBTRIPLE scanline_array[bi_resized.biWidth * sizeof(RGBTRIPLE)];

    // iterate over infile's scanlines
    for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
    {
        // iterate over pixels in scanline
        for (int j = 0; j < bi.biWidth; j++)
        {
            // temporary storage
            RGBTRIPLE triple;

            // read RGB triple from infile
            fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

            // write RGB triple to outfile
            for (int k = 0; k < scale; k++)
            {
                scanline_array[(int)(j * scale) + k] = triple;
            }
        }

        // skip over padding, if any
        fseek(inptr, padding, SEEK_CUR);

        for (int j = 0; j < scale; j++)
        {
            fwrite(scanline_array, sizeof(RGBTRIPLE), bi_resized.biWidth, outptr);

            // then add it back (to demonstrate how)
            for (int k = 0; k < padding_resized; k++)
            {
                fputc(0x00, outptr);
            }		
        }
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}
