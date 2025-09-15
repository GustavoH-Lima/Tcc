#!/bin/bash

#Este programa rodará a versão $1 com os tamanho 1024 até 2^(09 + $2) e armazenará a métrica cujas informações deseja-se coletar
# $1:Versão  $2:Quantas rodadas $3 nome da pasta

lista=("scaph_process_power_consumption_microwatts" \
       "scaph_process_cpu_usage_percentage" \
       "scaph_process_disk_total_read_bytes" \
       "scaph_process_disk_total_write_bytes" \
       "scaph_process_disk_read_bytes" \
       "scaph_process_disk_write_bytes" \
       "scaph_process_memory_bytes" \
       "scaph_process_memory_virtual_bytes")
inicia_pastas(){
    mkdir -p "$1"
    for item in "${lista[@]}"; do
        mkdir -p "$1/$item/matriz"
        mkdir -p "$1/$item/pi"
    done
}

mede_energia() {
    # $1: versão  $2: nome do subdir (matriz/pi)  $3: programa $4 pasta base
    for item in "${lista[@]}"; do
        >"$4/$item/$2/$tamanho"
    done
    sudo docker run -v /sys/class/powercap:/sys/class/powercap -v /proc:/proc -i hubblo/scaphandre stdout -t 999 -s 1 --raw-metrics > Saida.txt &
    pid=$!

    $3 m1 m2 $1 > mult_s &
    pidp=$!

    while kill -0 $pidp 2>/dev/null; do
        sleep 20
        if [ -s Saida.txt ]; then
            extrai_numeros $2 $pidp $4
            > Saida.txt
        fi
    done

    wait $pidp
    kill $pid 2>/dev/null

    if [ -s Saida.txt ]; then
        extrai_numeros $2 $pidp $4
        > Saida.txt
    fi

    rm -f Saida.txt mult_s
    rm -f Resultado
}


extrai_numeros() {
    # $1: subdir (matriz/pi)  $2: pid $3: base
    tempo=$(cat mult_s 2>/dev/null)

    for item in "${lista[@]}"; do
        grep --text -E "$item.*$2.*m1m2" Saida.txt | grep -v "grep" >> "$3/$item/$1/$tamanho"
    done
}

tamanho=1024
inicia_pastas $3

for ((i = 1; i <= $2; i++)); do
    ./gera m1 $tamanho
    ./gera m2 $tamanho
    echo "Executando versão $1 tamanho $tamanho"
    mede_energia $1 matriz ./mult $3
    tamanho=$(( tamanho * 2 ))
done

mede_energia $1 pi ./testes_variaveis/pi $3
echo "Terminado"