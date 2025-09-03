#include "func.h"
#include <omp.h>

int main(int argc, char** argv)
{
    int tam;
    double **C;
    if (argc != 4)
    {
        printf("Entre: %s <matriz 1> <matriz 2> <Caso de teste desejado(1 - 6)>\n",argv[0]);
        exit(1);
    }

    int opt;
    opt = atoi(argv[3]);
    double inicio, fim;
    if (opt == 1 || opt == 2)
    {
        double **A, **B;
        inicio = omp_get_wtime();
        A = le_matriz(argv,1,&tam);
        B = le_matriz(argv,2,&tam);
        // puts("A");
        // imprime_matriz(A,tam);
        // puts("B");
        // imprime_matriz(B,tam);
        switch (opt)
        {
        case 1:
            // puts("C - v1");
            C = v1(A,B,tam);
            // imprime_matriz(C,tam);
            break;
        case 2:
            // puts("C - v2");
            C = v2(A,B,tam);
            // imprime_matriz(C,tam);
            break;    
        default:
            break;
        }
        fim = omp_get_wtime();
        free(A);
        free(B);
    }
    else
    {
        double *A2, *B2, *C2;
        A2 = le_vetor(argv,1,&tam);
        B2 = le_vetor(argv,2,&tam);
        inicio = omp_get_wtime();
        switch (opt)
        {
        case 3:
            // puts("C - v3");
            C = v3(A2,B2,tam);
            // imprime_matriz(C,tam);
            break;
        case 4:
            // puts("C - v4");
            C = v4(A2,B2,tam);
            // imprime_matriz(C,tam);
            break;
        case 5:
            transpor(B2,tam);
            // puts("C - v5");
            C = v5(A2,B2,tam);
            // imprime_matriz(C,tam);

        case 6:
            transpor(B2,tam);
            C2 = v6(A2,B2,tam,16);
            // puts("C - v6");
            // imprime_vetor(C2,tam);
        default:
            break;
        }        
        fim = omp_get_wtime();
    }
    printf("%lf",fim - inicio);
    return 0;
}