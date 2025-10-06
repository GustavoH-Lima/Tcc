#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
//Funções de alocação
double** aloca_matriz(int tam); /*Função para alocar matrizes*/

double* aloca_vetor(int tam); /*Funções para alocar vetores*/

//Funções de leitura
double** le_matriz(char **argv,int i, int *tam);

double* le_vetor(char **argv,int i,int *tam);

//Funções de impressão
void imprime_matriz(double **m,int tam);
void imprime_vetor(double *m, int tam);
void escreve_arquivo_vect(char *nome,int tam,double *V);
void escreve_arquivo_matriz(char *nome,int tam,double **V);

//Funções auxiliares
void transpor(double* M,int tam);

//Funções principais de multiplicar matrizes
double** v1(double**A,double**B,int tam); /*Algoritmo ingênuo de Multiplicação de Matrizes, 3 laços aninhados e salvando direto na memória*/
double** v2(double**A,double**B,int tam); /*Algoritmo ingênuo de Multiplicação de Matrizes melhorado, 3 laços aninhados e salvando em variável temporária*/
double** v3(double*A,double*B,int tam); /*Algoritmo linearizando a matriz fazendo acesso com ponteiros*/
double** v4(double*A,double*B,int tam); /*Algoritmo linearizando a matriz fazendo acesso com ponteiros além de desenrolar o laço*/
double** v5(double*A,double*B,int tam); /*Algoritmo linearizando a matriz fazendo acesso com ponteiros além de desenrolar o laço e transpor a matriz B*/
double** v6(double*A,double*B,int tam,int blockSize);/*Algoritmo linearizando a matriz fazendo acesso com ponteiros além de desenrolar o laço, transpor a matriz B e utilizar a blocagem*/

double** v1_paralela(double**A,double**B,int tam,int nt);
double** v2_paralela(double**A,double**B,int tam,int nt);
double** v3_paralela(double*A,double*B,int tam,int nt);
double** v4_paralela(double*A,double*B,int tam, int nt);
double** v5_paralela(double*A,double*B,int tam,int nt);
double** v6_paralela(double*A,double*B,int tam,int blockSize,int nt);
