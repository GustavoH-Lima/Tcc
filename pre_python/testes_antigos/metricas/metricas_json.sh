#!/bin/bash

#Este programa rodará a versão $1 com os tamanho 1024 até 2^(9 + $2) e armazenará a métrica cujas informações deseja-se coletar
# $1:Versão  $2:Quantas rodadas $3 programa a ser executado {./testes_variaveis/pi ou ./mult}

mede_energia() {
    sudo scaphandre json --resources -t 999 -s 1 --max-top-consumers 2 --file testes_variaveis/consumo_matriz_$tamanho.json &
    pid=$!

    $2 m1 m2 $1 > mult_s &
    pidp=$!

    wait $pidp
    kill $pid 2>/dev/null
    echo "$pidp para tamanho $tamanho" >>pids

    rm Resultado
    rm mult_s
}

#Depois de executar, salvar o arquivo json salvado certinho com "ctrl + k + f" (Vscode) e executar o comando
#grep -A 16 -B 3 "pid" testes_variaveis/consumo_1024.json > testes_variaveis/mult_$tamanho.json
tamanho=1024
>pids
for ((i = 1; i<=$2; i++)); do
    #Colocando a versão a ser rodada
    ./gera m1 $tamanho
    ./gera m2 $tamanho
    echo "Executando tamanho $tamanho"
    mede_energia $1 $3
    tamanho=$(( $tamanho * 2 ))
    clear
done
echo "Terminado" 