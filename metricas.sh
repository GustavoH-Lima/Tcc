#!/bin/bash

#Este programa rodará a versão $1 com os tamanho 1024 até 2^(9 + $2) e armazenará a métrica cujas informações deseja-se coletar
# $1:Versão  $2:Quantas rodadas $3: Métrica a ser coletada $4 programa a ser executado {./testes_variaveis/pi ou ./mult}
#$3 pode ser:

# scaph_process_power_consumption_microwatts
# scaph_process_cpu_usage_percentage
# scaph_process_disk_total_read_bytes
# scaph_process_disk_total_write_bytes
# scaph_process_disk_read_bytes
# scaph_process_disk_write_bytes
# scaph_process_memory_bytes
# scaph_process_memory_virtual_bytes
mede_energia() {
    # $1: versão   $2: métrica   $3: programa
    >testes_variaveis/ER_$tamanho
    sudo scaphandre stdout -t-1 -s 1 --raw-metrics > Saida.txt &
    pid=$!

    $3 m1 m2 $1 > mult_s &
    pidp=$!

    # Enquanto o programa $3 não terminou
    while kill -0 $pidp 2>/dev/null; do
        sleep 20   # espera 20 segundos (20 medições)
        if [ -s Saida.txt ]; then
            extrai_numeros $2
            > Saida.txt   # limpa Saida.txt
        fi
    done

    wait $pidp
    kill $pid

    # processa qualquer sobra no final
    if [ -s Saida.txt ]; then
        extrai_numeros $2
        > Saida.txt
    fi
    rm Saida.txt
    rm Resultado
}


extrai_numeros()
{
    #$1: Métrica coletada $2 nome do programa executado
    tempo=$(cat mult_s)
    rm mult_s
    grep --text -E "$1.*$pidp.*m1m2" Saida.txt >> testes_variaveis/ER_$tamanho
    #Agora, outra expressão regular para pegar só os números

    # grep -o "[0-9]*\.[0-9]*" ER >medidas
    # rm ER
    #Por fim, pego somente os números, divido por 1e6 para transformar em watts, e como as medidas foram feitas de 1 em 1 segundo, eles estão em Joules.
    #Portanto, ao final do próximo comando, obtenho a quantidade de energia, em Joules, gasta pelo programa.
    # energia=$(grep -Eo "[0-9]+\.[0-9]+" medidas| awk '{s+=$1/1e6} END {print s}')
    # rm medidas
}

tamanho=1024

for ((i = 1; i<=$2; i++)); do
    #Colocando a versão a ser rodada
    ./gera m1 $tamanho
    ./gera m2 $tamanho
    echo "Executando tamanho $tamanho métrica $3"
    mede_energia $1 $3 $4
    tamanho=$(( $tamanho * 2 ))
    clear
done
echo "Terminado métrica $3" 