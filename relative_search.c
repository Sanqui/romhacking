#include <stdio.h>
#include <string.h>

int i;
int matched;
unsigned char off;
char c;
char* string;
int pos = 0;
FILE *fp;

int match_string(int is16bit) {
    off = string[0] - c;
    
    matched = 1;
    for (i=1; i<strlen(string); i++) {
        if (is16bit) fgetc(fp);
        if ((unsigned char)(string[i] - fgetc(fp)) != off) break;
        matched++;
    }
    if (matched == strlen(string)) {
        printf(" %d-bit string found at pos 0x%x, offset by 0x%x\n", is16bit ? 16 : 8, pos, off);
        i--;
    }
    
    
    if (feof(fp)) return -1;
    fseek(fp, -i * (is16bit ? 2 : 1), SEEK_CUR);
}

int main(int argc, char *argv[]) {
    int argi;
    char* filename;
    
    if (argc < 3) {
        printf("Usage: ./relative_search string file [...]\n");
        return 1;
    }
    string = argv[1];
    for (argi=2; argi < argc; argi++) {
        filename = argv[argi];
        printf("Looking for string %s in %s\n", string, filename);
        
        fp = fopen(filename, "rb");
        
        if (fp == NULL) {
            fprintf(stderr, "ERROR: Cannot open file\n");
            return 1;
        }
        
        while((c = fgetc(fp)) != EOF) {
            off = string[0] - c;
            
            match_string(0);
            match_string(1);
            
            pos++;
        }
    }
    
    return 0;
}
