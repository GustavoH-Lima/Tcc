#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
float** aloca_matriz(int tam)
{
    float **M;
    int i;
    M = (float**) malloc(tam*sizeof(float*));
    if(!M)
    {
        printf("Não foi possível alocar a matriz\n");
        exit(1);
    }
    for(i=0;i<tam;i++)
    {
        M[i] = (float*)malloc(tam*sizeof(float));
        if(!M[i])
        {
            printf("Não foi possível alocar a matriz\n");
            exit(1); 
        }
    }
    return M;
}
float** le_matriz(char **argv,int i, int *tam)
{
    FILE *fp;
    float ** M;
    fp = fopen(argv[i],"rb");
    if(!fp)
    {
        printf("Não foi possível ler a matriz\n");
        exit(1);
    }
    fread(tam,sizeof(int),1,fp);
    M = aloca_matriz(*tam);
    for(int j=0;j<*tam;j++)
    {
        fread(M[j],sizeof(float),*tam,fp);
    }
    fclose(fp);
    return M;
}

float* aloca_vetor(int tam)
{
    float *M;
    M = (float*) malloc(tam*sizeof(float));
    if(!M)
    {
        printf("Não foi possível alocar a matriz\n");
        exit(1);
    }
    return M;
}

float* le_vetor(char **argv,int i,int *tam)
{
    FILE *fp;
    float *M;
    fp = fopen(argv[i],"rb");
    if(!fp)
    {
        printf("Não foi possível ler do arquivo\n");
        exit(1);
    }
    fread(tam,sizeof(int),1,fp);
    M = aloca_vetor((*tam)*(*tam));
    fread(M,sizeof(float),(*tam)*(*tam),fp);
    fclose(fp);
    return M;
}
void imprime_matriz(float **m,int tam)
{
    for(int i=0;i<tam;i++)
    {
        for(int j=0;j<tam;j++)
        {
            printf("%f ",m[i][j]);
        }
        printf("\n");
    }
}
void imprime_vetor(float *m, int tam)
{
    for(int i=0;i<tam;i++)
    {
        for(int j=0;j<tam;j++)
        {
            printf("%f ",m[i * tam + j]);
        }
        printf("\n");
    }
}
void transpor(float* M,int tam)
{
    float temp;
    for(int i = 0;i<tam;i++)
    {
        for(int j=i;j<tam;j++)
        {
            temp = M[i * tam + j];
            M[i * tam + j] = M[j* tam + i];
            M[j*tam + i] = temp;
        }
    }
}
float** v1(float**A,float**B,int tam) /*Algoritmo ingênuo de Multiplicação de Matrizes, 3 laços aninhados e salvando direto na memória*/
{
    float **C;
    C = aloca_matriz(tam);
    int i,j,k;
    for(i = 0;i<tam;i++)
    {
        for(j=0;j<tam;j++)
        {
            C[i][j] = 0;
            for (k=0;k<tam;k++)
            {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    return C;
}
float** v2(float**A,float**B,int tam) /*Algoritmo ingênuo de Multiplicação de Matrizes melhorado, 3 laços aninhados e salvando em variável temporária*/
{
    float **C, temp;
    C = aloca_matriz(tam);
    int i,j,k;
    for(i = 0;i<tam;i++)
    {
        for(j=0;j<tam;j++)
        {
            temp = 0;
            for (k=0;k<tam;k++)
            {
                temp += A[i][k] * B[k][j];
            }
            C[i][j] = temp;
        }
    }
    return C;
}
float** v3(float*A,float*B,int tam) /*Algoritmo linearizando a matriz fazendo acesso com ponteiros*/
{
    float **C, temp;
    C = aloca_matriz(tam);
    int i,j,k;
    for(i = 0;i<tam;i++)
    {
        for(j=0;j<tam;j++)
        {
            temp = 0;
            for (k=0;k<tam;k++)
            {
                temp += A[i*tam + k] * B[k*tam + j];
            }
            C[i][j] = temp;
        }
    }
    return C;
}
float** v4(float*A,float*B,int tam) /*Algoritmo linearizando a matriz fazendo acesso com ponteiros além de desenrolar o laço*/
{/*Desenrolar o laço consiste em fazer mais operações por laço a fim de diminuir o overhead de controle*/
    float **C, temp;
    C = aloca_matriz(tam);
    int i,j,k;
    for(i = 0;i<tam;i++)
    {
        for(j=0;j<tam;j++)
        {
            temp = 0;
            for (k=0;k<tam;k+=4)
            {
                temp += A[i*tam + k + 0] * B[(k + 0)*tam + j];
                temp += A[i*tam + k + 1] * B[(k + 1)*tam + j];
                temp += A[i*tam + k + 2] * B[(k + 2)*tam + j];
                temp += A[i*tam + k + 3] * B[(k + 3)*tam + j];
            }
            C[i][j] = temp;
        }
    }
    return C;
}
float** v5(float*A,float*B,int tam) /*Algoritmo linearizando a matriz fazendo acesso com ponteiros além de desenrolar o laço e transpor a matriz B*/
{/*Transpondo a matriz B para aproveitar a localidade de memória*/
    float **C, temp;
    C = aloca_matriz(tam);
    int i,j,k;
    for(i = 0;i<tam;i++)
    {
        for(j=0;j<tam;j++)
        {
            temp = 0;
            for (k=0;k<tam;k+=4)
            {
                temp += A[i*tam + k + 0] * B[(j*tam + k + 0)];
                temp += A[i*tam + k + 1] * B[(j*tam + k + 1)];
                temp += A[i*tam + k + 2] * B[(j*tam + k + 2)];
                temp += A[i*tam + k + 3] * B[(j*tam + k + 3)];
            }
            C[i][j] = temp;
        }
    }
    return C;
}
float** v6(float*A,float*B,int tam)/*Algoritmo linearizando a matriz fazendo acesso com ponteiros além de desenrolar o laço, transpor a matriz B e utilizar a blocagem*/
{
    //ToDo
}
int main(int argc, char** argv)
{
    float **A, **B, **C;
    int tam;
    A = le_matriz(argv,1,&tam);
    B = le_matriz(argv,2,&tam);
    // puts("A");
    // imprime_matriz(A,tam);
    // puts("B");
    // imprime_matriz(B,tam);

    // puts("C - v1");
    C = v1(A,B,tam);
    /*--*/
    // imprime_matriz(C,tam);
    // puts("C - v2");
    C = v2(A,B,tam);
    // imprime_matriz(C,tam);

    free(A);
    free(B);

    float *A2, *B2;
    A2 = le_vetor(argv,1,&tam);
    B2 = le_vetor(argv,2,&tam);
    /*--*/
    // puts("C - v3");
    C = v3(A2,B2,tam);
    // imprime_matriz(C,tam);
    /*--*/
    // puts("C - v4");
    C = v4(A2,B2,tam);
    // imprime_matriz(C,tam);
    transpor(B2,tam);
    /*--*/
    // puts("C - v5");
    C = v5(A2,B2,tam);
    // imprime_matriz(C,tam);

    return 0;
}