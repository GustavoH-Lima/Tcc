## Situações
- [ ] Resumo: Aguardando término do capítulo 5
- [ ] Capítulo 1: Aguardando Feedback
- [ ] Capítulo 2: Aguardando Feedback
- [ ] Documentação da Experiência da ferramenta: Dizer a máquina em que os testes foram realizados (Máquina de casa)
- [ ] Capítulo 3: Aguardando término da escrita da documentação e Realização dos testes
- [ ] Capítulo 4: Aguardando término do capítulo 3 
- [ ] Capítulo 5: Aguardando término do capítulo 4
- [ ] Apêndices


## Passo a passo:
- [X] Iniciar o Scaphandre -- Shell Script
- [X] Iniciar a multiplicação de matriz Shell Script
- [X] Assim que terminar, parar a ferramenta Shell Script
- [X] Ajeitar o Json de uma linha para que, a última medida feita (Defeituosa) seja apagada -- Corrige.py
- [X] Usar o "jq" para formatar o arquivo da maneira correta 
- [X] Usar as expressões regulares para coletar os números --> Há maneira melhor? Tentar arquivo python
    - [ ] Tentar trocar para pegar os resultados em python e não em Shell (Para encapsular melhor)
- [X] Salvar em csv para posteriormente gerar gráficos
- [ ] Gerar os gráficos --> Produzir Arquivo Python & pensar em modo melhor de agregar os resultados para facilitar a geração

## Tarefas 30/09 - 07/10
- [X] Terminar capítulo de experimentação com Scaphandre
    (No laboratório)
    -[X] Verificar as medidas "disk_write_bytes" para o exporter Stdout;
    -[X] Verificar as medidas "disk_usage_write" e "consumption" para o exporter Json;(Não foi posśivel colher dados sobre os discos usando o container)
    -[X] Vericar, novamente, as outras medidas e determinar se o comentário bate.
- [ ] Implementar multiplicação de matrizes com paralelismo
- [ ] Colher dados de multiplicação e gerar tabelas
    (Gerar em casa por conta do fato de não conseguir encerrar o Scaphandre de dentro do container)
    - Coletar no laboratório com o código "gera_testes.sh"
    - [X] Multiplicar a média da ram pelo tempo que demorou na matriz OU;
    - [X] Considerar o gasto no total, explicando que não é o software isolado mas sim o chipe como um todo sendo executado.
        - Considerar os dois modos,por enquanto
        - 
- [ ] Buscar artigos do professor Daniel Cordeiro (Computação Sustentável)


## Tarefas 25/09 - 30/09
- [X] Fechar proposta do MiniCurso

## Tarefas 16/09 - 25/09
- [ ] Proposta de Minicurso
- [X] Testar calculo da ram
- [X] Testar normal (Nada executando) Obtido: 10.2711 J
- [X] Testar a Matriz Obtido: 10.8079 J
- [X] Testar a matriz com o navegador aberto Obtido: 38.1356

## tarefas 11/09 - 16/09
- [X] Escrever o processo de teste da ferramenta
- [X] Anotar ideias de propostas
    - No carderno
- [ ] Ideia para calcular o consumo da RAM:
    - durante um tempo, tomar medidas do consumo usando o json com a máquina funcionando normalmente (Sem nada rodando);
    - Tomar o consumo médio da Dram;
    - Diminuir esse consumo médio do consumo obtido quando se está executando a multiplicação de matriz desejada.

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



## Terefas xx/xx - xx/xx
- [X] Adicionar v6 das mutiplicações: Blocagem
- [ ] Adicionar v7 das multiplicações: Strassen?
- [-] Criar Pandas para analisar o consumo de energia
- [X] Implementar modo melhor de tomar os tempos (Precisa?)
- [X] Estudar mais como tomar as medidas de energia usando o scaphandre
- [X] Escrever o Shell de teste
