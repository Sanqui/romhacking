#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <getopt.h>

int i;
int matched;
unsigned char off;
int c;
char* string;
int string_len;
char* filename;
FILE *fp;

int match_string(bool is16bit) {
    off = string[0] - c;
    
    matched = 1;
    for (i=1; i<string_len; i++) {
        if (is16bit) fgetc(fp);
        if ((unsigned char)(string[i] - fgetc(fp)) != off) break;
        matched++;
    }
    if (matched == string_len) {
        printf("%s-bit string found in file %s, pos 0x%x, offset by 0x%x\n", is16bit ? "16" : " 8", filename, ftell(fp)-i, off);
        i--;
    }
    
    
    if (feof(fp)) return -1;
    fseek(fp, -i * (is16bit ? 2 : 1), SEEK_CUR);
}

int main(int argc, char *argv[]) {
    int argi;
    bool verbose = false;
    
    while ((c = getopt (argc, argv, "v")) != -1) {
        switch (c) {
            case 'v':
                verbose = true;
                break;
        }
    }
    if (argc - optind < 2) {
        printf("Usage: ./relative_search (-v) string file [...]\n");
        return 1;
    }
    string = argv[optind];
    string_len = strlen(string);
    for (argi=optind+1; argi < argc; argi++) {
        filename = argv[argi];
        if (verbose) printf("Looking for string %s in %s\n", string, filename);
        
        fp = fopen(filename, "rb");
        
        if (fp == NULL) {
            fprintf(stderr, "ERROR: Cannot open file\n");
            return 1;
        }
        
        while((c = fgetc(fp)) != EOF) {
            match_string(false);
            match_string(true);
        }
    }
    
    return 0;
}
