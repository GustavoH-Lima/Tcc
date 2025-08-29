#!/bin/bash

mede_energia()
{
    sudo docker run -v /sys/class/powercap:/sys/class/powercap -v /proc:/proc -i hubblo/scaphandre stdout -t 7 -s 1 --raw-metrics >Saida &
    pid=$!

    ./mult m1 m2 $1 > tmp_tempo &
    pid_mult=$!
    wait $pid_mult
    tempo=$(cat tmp_tempo)
    rm tmp_tempo


    wait $pid
    #Agora, uso uma expressão regular para pegar as linhas em que foi medido a potência do processo.
    grep -E "power.*[0-9]*\.[0-9]*.*$pidmult" Saida > ER
    rm Saida
    #Agora, outra expressão regular para pegar só os números

    grep -o "[0-9]*\.[0-9]*" ER >medidas
    rm ER
    #Por fim, pego somente os números, divido por 1e6 para transformar em watts, e como as medidas foram feitas de 1 em 1 segundo, eles estão em Joules.
    #Portanto, ao final do próximo comando, obtenho a quantidade de energia, em Joules, gasta pelo programa.
    energia=$(grep -Eo "[0-9]+\.[0-9]+" medidas| awk '{s+=$1/1e6} END {print s}')
    rm medidas
}

matdim=$1
./gera m1 $matdim
./gera m2 $matdim

echo "versao;exec1;exec2;exec3;exec4;exec5" > "tabelas/tempos_$matdim.csv"
echo "versao;exec1;exec2;exec3;exec4;exec5" > "tabelas/energia_$matdim.csv"

for ((i = 1; i<=6; i++)); do
    #Colocando a versão a ser rodada
    linha_tempo="$i"
    linha_energia="$i"
    for ((j = 1; j<=5;j++)); do
        echo "Executando versão $i vez $j"
        mede_energia $i
        tempo=$(echo "$tempo" | sed 's/\./,/') #Trocando o ponto por , para adaptar ao google planilhas
        energia=$(echo "$energia" | sed 's/\./,/') #Novamente, trocando "." por ","
        linha_energia+=";$energia"
        linha_tempo+=";$tempo"
    done
    echo "$linha_energia" >> tabelas/energia_$matdim.csv
    echo "$linha_tempo" >> tabelas/tempos_$matdim.csv
done