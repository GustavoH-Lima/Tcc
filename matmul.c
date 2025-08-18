#include "func.h"
#include <omp.h>

int main(int argc, char** argv)
{
    double **A, **B, **C;
    int tam;
    A = le_matriz(argv,1,&tam);
    B = le_matriz(argv,2,&tam);
    // puts("A");
    // imprime_matriz(A,tam);
    // puts("B");
    // imprime_matriz(B,tam);

    puts("C - v1");
    C = v1(A,B,tam);
    /*--*/
    imprime_matriz(C,tam);
    puts("C - v2");
    C = v2(A,B,tam);
    imprime_matriz(C,tam);

    free(A);
    free(B);

    double *A2, *B2, *C2;
    A2 = le_vetor(argv,1,&tam);
    B2 = le_vetor(argv,2,&tam);
    /*--*/
    puts("C - v3");
    C = v3(A2,B2,tam);
    imprime_matriz(C,tam);
    /*--*/
    puts("C - v4");
    C = v4(A2,B2,tam);
    imprime_matriz(C,tam);
    transpor(B2,tam);
    /*--*/
    puts("C - v5");
    C = v5(A2,B2,tam);
    imprime_matriz(C,tam);
    C2 = v6(A2,B2,tam,2);
    puts("C - v6");
    imprime_vetor(C2,tam);
    return 0;
}