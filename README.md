## Situações
- [ ] Resumo: Aguardando término do capítulo 5
- [ ] Capítulo 1: Aguardando Feedback
- [ ] Capítulo 2: Aguardando Feedback
- [ ] Documentação da Experiência da ferramenta: Aguardando aval para teste dos componentes do "socket"
- [ ] Capítulo 3: Aguardando término da escrita da documentação e Realização dos testes
- [ ] Capítulo 4: Aguardando término do capítulo 3 
- [ ] Capítulo 5: Aguardando término do capítulo 4
- [ ] Apêndices / Anexo: Colocar Json de exemplo / Códigos

## Terefas xx/xx - xx/xx
- [X] Adicionar v6 das mutiplicações: Blocagem
- [ ] Adicionar v7 das multiplicações: Strassen?
- [-] Criar Pandas para analisar o consumo de energia
- [X] Implementar modo melhor de tomar os tempos (Precisa?)
- [X] Estudar mais como tomar as medidas de energia usando o scaphandre
- [X] Escrever o Shell de teste

## Tarefas do período 26/08 - 04/09
- [X] Estudo do Scaphandre
- [X] Método para conseguir o consumo de energia da CPU
- [X] Texto: Inclusão de autor na Revisão sobre Computação Verde
- [X] Texto: Scaphandre
- [X] Texto: Capítulo 1
- [X] Texto: Revisão Bibliográfica

## Perguntas 04/09
- [ ] Capítulo 1 está bom?
- [ ] Capítulo 2 está bom?
- [X] Coloco exemplo de saída Json no texto?
- [ ] Quais métricas seria interessante pegar?

## Tarefas do período 04/09 - 11/09
- [X] Entender as métricas melhor (Comparar as métricas para uma mesma versão mas variando o tamanho da matriz) *
- [ ] Explorar o exporter json para pegar os "dram"...
- [X] Escrever programa para analisar como as métricas são disponibilizadas

Disponíveis:

Parece o mais simples de entender
- [X] scaph_process_power_consumption_microwatts # Total data read on disk by the process, in bytes  
- [X] scaph_process_cpu_usage_percentage # CPU time consumed by the process, as a percentage of the capacity of all the CPU Cores

Escrever programa CPU_bound (Calculo de pi) que não lê nada da memória e comparar a métrica de baixo
- [X] scaph_process_disk_total_read_bytes # Total data read on disk by the process, in bytes
-- Comentário: Aqui parece estar funcionando pois quanto mais a matriz aumenta, maior é a métrica na ferramenta e a de calcular pi aparece como 0

Usar o programa de calculo de PI para ver se ele escreve na memória 
- [ ] scaph_process_disk_total_write_bytes # Total data written on disk by the process, in bytes
Conclusão: Aqui o programa não escreve nada na memória, o calculo de pi, mas ele ainda sim coloca o mesmo valor...


Será que esses de baixo são do intervalo específico e os de cima são durante toda a execução?
Se os de cima funcionarem, comparar o tempo de leitura da matriz, de computação e de escrita, usar sleep entre essas fases para que o time stamp seja pego (Json)
- [X] scaph_process_disk_read_bytes # Data read on disk by the process, in bytes
Na métrica acima, ao aumentar o tamanho da matriz para 8192, houve a leitura de disco (Como evidenciado pelo arquivo)
- [ ] scaph_process_disk_write_bytes # Data written on disk by the process, in bytes
-- Mesmo tendo uma escrita em arquivo binário, a ferramenta não acusou mudança nessa métrica, será que testando com matrizes maiores?

Para esses de baixo, escrever shell que aumente a matriz e ver o comportamento dessa métrica.
- [X] scaph_process_memory_bytes # Physical RAM usage by the process, in bytes
Realmente, com o passar do tempo de execução, o uso, em bytes, da RAM vai aumentando, a métrica parece confiável.

- [X] scaph_process_memory_virtual_bytes # Virtual RAM usage by the process, in bytes
Aqui parece que o comportamento faz sentido, na matriz 4096, no começo não se usa tanta memória virtual, mas depois se carregam as matrizes e o uso aumenta, talvez testar pra 8192

## tarefas 11/09 - 16/09
- [X] Escrever o processo de teste da ferramenta
- [X] Anotar ideias de propostas
    - No carderno
- [ ] Ideia para calcular o consumo da RAM:
    - durante um tempo, tomar medidas do consumo usando o json com a máquina funcionando normalmente (Sem nada rodando);
    - Tomar o consumo médio da Dram;
    - Diminuir esse consumo médio do consumo obtido quando se está executando a multiplicação de matriz desejada.
