#!/bin/bash

#Programa que pegará as métricas de consumo de energia e consumo da RAM do socket do programa de multiplicação de matrizes
# $1 Tamanho $2 Nome da Pasta em que os resultados serão armazenados

mede_energia(){
    #$1 Versão a ser executada (1-6)
    sudo scaphandre json -s 1 --max-top-consumers 2 --file consumo.json &
    pid_scaphandre=$!

    ./mult m1 m2 $1 > mult_time & #Armazena o tempo da multiplicação, executa em segundo plano para obter o pid do processo
    pid_mult=$!

    wait $pid_mult
    sleep 0.5
    sudo kill $pid_scaphandre

    tempo=$(cat mult_time)
    rm mult_time

    #Agora, para coletar as métricas de energia, há a necessidade de "formatar" o json e executar as expressões regulares.
    while ! jq . consumo.json >/dev/null 2>&1; do
    # remove o último caractere do arquivo
    truncate -s -1 consumo.json
    done
    sudo jq -s . consumo.json > consumo_formatado.json
    energia_processo=$(grep -A 2 "pid.*$pid_mult" consumo_formatado.json | grep -E "consumption" | grep -o "[0-9]*.[0-9]*" | awk '{s+=$1/1e6} END{print s}') #Coleta o consumo do processo
    energia_dramtot=$(grep -A 2 "name.*dram" consumo_formatado.json | grep -E "consumption" | grep -o "[0-9]*" | awk '{s+=$1/1e6} END{print s}') #Coleta o consumo da RAM
    energia_dram=$(awk -v tot="$energia_dramtot" -v norm="$dram_normal" -v t="$tempo" 'BEGIN {print tot - norm * t}')
}
energia_inicial(){
    #Vê qual a média de energia gasta "normalmente"
    echo "Coletando energia média inicial..."
    sudo scaphandre json -t 60 -s 1 --resources --max-top-consumers 2 --file consumo.json
    jq -s . consumo.json > consumo_formatado.json
    dram_normal=$(grep -A 2 "name.*dram" consumo_formatado.json | grep -E "consumption" | grep -o "[0-9]*" | awk '{s+=$1/(60*1e6)} END{print s}') #Coleta o consumo da RAM
}
matdim=$1
#Iniciando os .csv

if [ ! -d "$2" ]; then
    mkdir "$2"
    mkdir "$2/$matdim"
fi

if [ ! -d "$2/$matdim" ]; then
    mkdir "$2/$matdim"
fi

echo "versao;exec1;exec2;exec3;exec4;exec5" > $2/$matdim/energias_$matdim.csv
echo "versao;exec1;exec2;exec3;exec4;exec5" > $2/$matdim/dramtot_$matdim.csv
echo "versao;exec1;exec2;exec3;exec4;exec5" > $2/$matdim/tempos_$matdim.csv
echo "versao;exec1;exec2;exec3;exec4;exec5" > $2/$matdim/dram_$matdim.csv

#Tomando a energia média inicial
energia_inicial

./gera m1 $matdim
./gera m2 $matdim

for ((i = 5; i<=6; i++)); do
    #Colocando a versão a ser rodada
    linha_dram="$i"
    linha_tempo="$i"
    linha_energia="$i"
    linha_dram_tot="$i"
    for ((j = 1; j<=5;j++)); do
        clear
        echo "Executando versão $i vez $j..."
        mede_energia $i
        tempo=$(echo "$tempo" | sed 's/\./,/') #Trocando o ponto por , para adaptar ao google planilhas
        energia_processo=$(echo "$energia_processo" | sed 's/\./,/') #Novamente, trocando "." por ","
        energia_dram=$(echo "$energia_dram" | sed 's/\./,/')

        linha_energia+=";$energia_processo"
        linha_dram_tot+=";$energia_dramtot"
        linha_dram+=";$energia_dram"
        linha_tempo+=";$tempo"
    done
    #Adicionando a linha ao csv
    echo "$linha_energia" >> $2/$matdim/energias_$matdim.csv
    echo "$linha_dram_tot" >> $2/$matdim/dramtot_$matdim.csv
    echo "$linha_tempo" >> $2/$matdim/tempos_$matdim.csv
    echo "$linha_dram" >> $2/$matdim/dram_$matdim.csv
done

rm consumo.json
rm consumo_formatado.json
rm Resultado
echo "Terminado"