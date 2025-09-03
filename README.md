- [X] Adicionar v6 das mutiplicações: Blocagem
- [ ] Adicionar v7 das multiplicações: Strassen?
- [-] Criar Pandas para analisar o consumo de energia
- [X] Implementar modo melhor de tomar os tempos (Precisa?)
- [X] Estudar mais como tomar as medidas de energia usando o scaphandre
- [X] Escrever o Shell de teste

## Tarefas do período 26/08 - 04/07
- [X] Estudo do Scaphandre
- [X] Método para conseguir o consumo de energia da CPU
- [X] Texto: Inclusão de autor na Revisão sobre Computação Verde
- [X] Texto: Scaphandre
- [X] Texto: Capítulo 1
- [X] Texto: Revisão Bibliográfica

## Perguntas 04/07
- [ ] Capítulo 1 está bom?
- [ ] Capítulo 2 está bom?
- [ ] Coloco exemplo de saída Json no texto?
- [ ] Quais métricas seria interessante pegar?\\
    Disponíveis:
    scaph_process_disk_write_bytes # Data written on disk by the process, in bytes\\
    scaph_process_power_consumption_microwatts # Total data read on disk by the process, in bytes\\
    
    scaph_process_disk_total_read_bytes # Total data read on disk by the process, in bytes
    
    scaph_process_disk_total_write_bytes # Total data written on disk by the process, in bytes
    
    scaph_process_memory_bytes # Physical RAM usage by the process, in bytes
    
    scaph_process_memory_virtual_bytes # Virtual RAM usage by the process, in bytes
    
    scaph_process_disk_read_bytes # Data read on disk by the process, in bytes
    
    scaph_process_cpu_usage_percentage # CPU time consumed by the process, as a percentage of the capacity of all the CPU Cores
