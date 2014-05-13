#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    int argi;
    int i;
    int pos = 0;
    int matched;
    unsigned char off;
    int is16bit = 0;
    char c;
    char* filename;
    if (argc < 3) {
        printf("Usage: ./relative_search string file [...]\n");
        return 1;
    }
    char* string = argv[1];
    for (argi=2; argi < argc; argi++) {
        filename = argv[argi];
        printf("Looking for string %s in %s\n", string, filename);
        FILE *fp;
        
        fp = fopen(filename, "rb");
        
        if (fp == NULL) {
            fprintf(stderr, "ERROR: Cannot open file\n");
            return 1;
        }
        
        while((c = fgetc(fp)) != EOF) {
            off = string[0] - c;
            
            do {
                matched = 1;
                for (i=1; i<strlen(string); i++) {
                    if (is16bit) getc(fp);
                    if ((unsigned char)(string[i] - getc(fp)) != off) break;
                    matched++;
                }
                if (matched == strlen(string)) {
                    printf(" %d-bit string found at pos 0x%x, offset by 0x%x\n", is16bit ? 16 : 8, pos, off);
                    i--;
                }
                
                
                if (feof(fp)) break;
                fseek(fp, -i * (is16bit ? 2 : 1), SEEK_CUR);
                
                is16bit = !is16bit;
            } while (is16bit != 0);
            
            pos++;
        }
    }
    
    return 0;
}
