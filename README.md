# Huggin



## Pulseira de Batimentos Cardíacos conectada a plataforma de ajuda

![imagem](WhatsApp%20Image%202024-12-21%20at%2008.49.29.jpeg)

### Visão Geral

Este repositório contém um conjunto de códigos para implementar um monitor de batimentos cardíacos usando um sensor "pulse sensor", um microcontrolador (como ESP32), e o protocolo MQTT para transmissão dos dados coletados. O projeto também incorpora uma máquina de estados para monitorar e notificar sobre batimentos anormais. Os dados coletados sao passados para uma plataforma que disponibiliza os batimentos em tempo real e caso eles estejam muito altos ele manda um alerta na tela e em caso de ausencia de respostas, manda uma mensagem de alerta para algum contato de emergencia do usuario.

### Estrutura do Repositório

**main.py:** Script principal que realiza:

- Conexão ao broker MQTT.

- Leitura do sensor de batimentos.

- Cálculo e publicação do BPM (batimentos por minuto) via MQTT.

**boot.py:** Script executado automaticamente no boot do dispositivo. Configura:

- Conexão à rede Wi-Fi.

- Inicia o WebREPL para acesso remoto.

**heartbeat_state_machine.py:** Implementação de uma máquina de estados para:

- Verificar batimentos.

- Enviar notificações ao usuário e a contatos preestabelecidos.

## Configuração

### Requisitos de Hardware

- Microcontrolador ESP32 ou compatível.

- Sensor de batimentos cardíacos (ex.: pulse sensor, MAX30102).

- Conexão Wi-Fi ativa.

### Requisitos de Software

- Micropython instalado no microcontrolador.

- Biblioteca umqttsimple para comunicação MQTT.

- Bibliotecas para manipulação do sensor.

## Configuração Inicial

- Configurar o Wi-Fi: Altere as variáveis SSID e PASSWORD no arquivo boot.py para suas credenciais de rede.

- Configurar o Broker MQTT: Altere as variáveis MQTT_HOSTNAME e MQTT_PORT no arquivo main.py para os valores do seu broker MQTT.

- Pinos do Sensor: Certifique-se de que os pinos configurados no código correspondem às conexões físicas no seu hardware.

## Uso

#### boot.py

Este arquivo é executado automaticamente no boot do dispositivo e realiza:

- Conexão ao Wi-Fi.

- Inicialização do WebREPL para acesso remoto.

#### main.py

Este arquivo:

- Conecta ao broker MQTT.

- Lê os sinais do sensor de batimentos.

- Calcula o BPM com base nos intervalos entre batimentos detectados.

- Publica os dados no broker MQTT no tópico configurado.

#### heartbeat_state_machine.py

Implementa a máquina de estados:

- Estado 0: Monitora batimentos cardíacos.

- Estado 1: Aguarda confirmação do usuário sobre anormalidades.

- Estado 2: Envia notificação a contatos predefinidos caso o usuário não responda.

## Executando o Projeto

- Suba os arquivos para o microcontrolador.

- Execute o main.py para iniciar o monitoramento e a publicação MQTT.

### Ajustes

- Limiar do Sensor: Ajuste a variável THRESHOLD no arquivo main.py para calibrar a sensibilidade do sensor de batimentos.

- Intervalo de Cálculo do BPM: Alterar a frequência de cálculo do BPM editando o tamanho da janela de amostras.

### Exemplos de Saída MQTT

Os dados são enviados no formato JSON, por exemplo:

{
  "bpm": 72
}


## Frontend 

### Explicacao 
  O repositorio nao contem os codigos do frontend ( formatei meu pc e esqueci de salvar ), mas o front foi feito usando python, html, css e javascript. O site recebia os dados postados no broker mqtt e com isso, printava eles a todo tempo na tela (ao vivo) e caso o valor do batimento superasse uns 150 batimentos por minuto, ele mandava uma mensagem via sms para um contato pre-estabelecido pelo usuario da plataforma. Seguem imagens:

