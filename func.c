#include "func.h"
double** aloca_matriz(int tam)
{
    double **M;
    int i;
    M = (double**) malloc(tam*sizeof(double*));
    if(!M)
    {
        printf("Não foi possível alocar a matriz\n");
        exit(1);
    }
    for(i=0;i<tam;i++)
    {
        M[i] = (double*)malloc(tam*sizeof(double));
        if(!M[i])
        {
            printf("Não foi possível alocar a matriz\n");
            exit(1); 
        }
    }
    return M;
}

double* aloca_vetor(int tam)
{
    double *M;
    M = (double*) malloc(tam*sizeof(double));
    if(!M)
    {
        printf("Não foi possível alocar a matriz\n");
        exit(1);
    }
    return M;
}

double** le_matriz(char **argv,int i, int *tam)
{
    FILE *fp;
    double ** M;
    fp = fopen(argv[i],"rb");
    if(!fp)
    {
        printf("Não foi possível ler a matriz %s\n",argv[i]);
        exit(1);
    }
    fread(tam,sizeof(int),1,fp);
    M = aloca_matriz(*tam);
    for(int j=0;j<*tam;j++)
    {
        fread(M[j],sizeof(double),*tam,fp);
    }
    fclose(fp);
    return M;
}

double* le_vetor(char **argv,int i,int *tam)
{
    FILE *fp;
    double *M;
    fp = fopen(argv[i],"rb");
    if(!fp)
    {
        printf("Não foi possível ler do arquivo\n");
        exit(1);
    }
    fread(tam,sizeof(int),1,fp);
    M = aloca_vetor((*tam)*(*tam));
    fread(M,sizeof(double),(*tam)*(*tam),fp);
    fclose(fp);
    return M;
}

void imprime_matriz(double **m,int tam)
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
void imprime_vetor(double *m, int tam)
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

void transpor(double* M,int tam)
{
    double temp;
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

double** v1(double**A,double**B,int tam) /*Algoritmo ingênuo de Multiplicação de Matrizes, 3 laços aninhados e salvando direto na memória*/
{
    double **C;
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
double** v2(double**A,double**B,int tam) /*Algoritmo ingênuo de Multiplicação de Matrizes melhorado, 3 laços aninhados e salvando em variável temporária*/
{
    double **C, temp;
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
double** v3(double*A,double*B,int tam) /*Algoritmo linearizando a matriz fazendo acesso com ponteiros*/
{
    double **C, temp;
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
double** v4(double*A,double*B,int tam) /*Algoritmo linearizando a matriz fazendo acesso com ponteiros além de desenrolar o laço*/
{/*Desenrolar o laço consiste em fazer mais operações por laço a fim de diminuir o overhead de controle*/
    double **C, temp;
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
double** v5(double*A,double*B,int tam) /*Algoritmo linearizando a matriz fazendo acesso com ponteiros além de desenrolar o laço e transpor a matriz B*/
{/*Transpondo a matriz B para aproveitar a localidade de memória*/
    double **C, temp;
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
double* v6(double*A,double*B,int tam,int blockSize)/*Algoritmo linearizando a matriz fazendo acesso com ponteiros além de desenrolar o laço, transpor a matriz B e utilizar a blocagem*/
{
    double *C;
    C = (double *) calloc (tam * tam,sizeof(double));
    if(!C)
    {
        printf("Não foi possível alocar a matriz\n");
        exit(1);
    }
    
    for (int ii = 0; ii < tam; ii += blockSize)
        for (int jj = 0; jj < tam; jj += blockSize)
            for (int kk = 0; kk < tam; kk += blockSize)
                for (int i = ii; i < ii + blockSize && i < tam; i++)
                    for (int j = jj; j < jj + blockSize && j < tam; j++)
                    {
                        double sum = 0.0;
                        for (int k = kk; k < kk + blockSize && k < tam; k++)
                            sum += A[i * tam + k] * B[j * tam + k];
                        C[i * tam + j] += sum;
                    }
    return C;
}