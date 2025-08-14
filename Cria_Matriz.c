#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define max 10000

int main(int argc, char** argv)
{
    if ( argc != 3 )
    {
        printf("Escreva: $%s <Nome da matriz> <Tamanho da Matriz>\n",argv[0]);
        exit(1);
    }
    int tam = atoi(argv[2]);
    FILE *fp;
    int novo_tam = tam * tam;
    /*Alocando a matriz*/
    float *M = (float*) malloc(novo_tam*sizeof(float));
    if(!M)
    {
        printf("Não foi possível alocar a matriz\n");
        exit(2);
    }
    
    /*Inicializando os valores*/
    srand(time(NULL));
    for(int i=0; i<novo_tam;i++)
    {
        M[i] = ((rand() % (2*max)) - max)/7.0;
    }
    /*Escrevendo no arquivo*/
    fp = fopen(argv[1],"wb+");
    fwrite(&tam,sizeof(int),1,fp);
    fwrite(M,sizeof(float),novo_tam,fp);

    fclose(fp);
    return 0;
}