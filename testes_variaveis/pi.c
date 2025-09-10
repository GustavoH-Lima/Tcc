#include <stdio.h>

int main(void)
{
    double pi = 0;
    __uint32_t n = -1;
    double var = 1.0/n;

    for(long i = 0; i<n;i++)
    {
        pi+= 1/(1+(var*i)*(var*i))*var;
    }
    pi*=4;
    return 0;
}