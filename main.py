from machine import Pin, ADC
import time
import ujson, socket, ubinascii, machine
from umqttsimple import MQTTClient

# Configuração MQTT
MQTT_HOSTNAME = 'broker.emqx.io'
MQTT_PORT = 1883

mqtt_server = socket.getaddrinfo(MQTT_HOSTNAME, MQTT_PORT)[0][4][0]
topic_prefix = 'huginn'
last_will_topic = 'client'
PULSE_SENSOR_TOPIC = 'PULSE_SENSOR'

client_id = ubinascii.hexlify(machine.unique_id()).decode('utf8')
bpm = 0

# Configuração do sensor
PULSE_SENSOR_PIN = 34  # Pino analógico do Pulse Sensor
THRESHOLD = 550        # Limite para detectar batimentos
pulse_sensor = ADC(Pin(PULSE_SENSOR_PIN))
pulse_sensor.atten(ADC.ATTN_11DB)  # Ajusta escala de tensão para 3.3V
pulse_sensor.width(ADC.WIDTH_10BIT)  # Resolução de 10 bits (valores de 0 a 1023)

# Variáveis para calcular BPM
last_beat_time = 0
intervals = []

# Função para calcular BPM
def calculate_bpm():
    global intervals
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        bpm = int(60000 / avg_interval)  # BPM = 60s * 1000ms / intervalo médio
    else:
        bpm = 0
    intervals = []
    return bpm

# Função de conexão MQTT
def connect(client_id, mqtt_server):
    print(f'{client_id} conectando a {mqtt_server}')
    client = MQTTClient(client_id, mqtt_server)

    # Configura mensagem "Last Will"
    last_will_message = ujson.dumps({'client_id': client_id, 'status': False})
    client.set_last_will(f'{topic_prefix}/{last_will_topic}', last_will_message)

    try:
        client.connect()
        print('Conectado ao broker MQTT')
    except Exception as e:
        print(f'Erro ao conectar ao broker MQTT: {e}')
        raise
    return client

# Inicializa MQTT e notifica que está online
def start_mqtt():
    global client
    try:
        client = connect(client_id, mqtt_server)
        online_message = ujson.dumps({'client_id': client_id, 'status': True})
        client.publish(f'{topic_prefix}/{last_will_topic}', online_message)
    except OSError as e:
        print(e)
        print("Falha ao conectar ao broker MQTT. Reconectando...")
        time.sleep(10)
        machine.reset()

# Inicializa MQTT
client = None
start_mqtt()

# Loop principal
print("Iniciando leitura do Pulse Sensor...")
while True:
    signal = pulse_sensor.read()  # Lê o valor do Pulse Sensor
    current_time = time.ticks_ms()  # Tempo atual em milissegundos

    # Detecta batimento
    if signal > THRESHOLD and time.ticks_diff(current_time, last_beat_time) > 300:  # Debounce 300ms
        interval = time.ticks_diff(current_time, last_beat_time)
        intervals.append(interval)
        last_beat_time = current_time

    # Calcula BPM
    if len(intervals) >= 5:
        bpm = calculate_bpm()
        print(f"BPM: {bpm}")
        try:
            # Publica no broker MQTT
            client.publish(f'{topic_prefix}/{PULSE_SENSOR_TOPIC}', ujson.dumps({"bpm": bpm}))
        except Exception as e:
            print(f"Erro ao publicar no MQTT: {e}")

    time.sleep(0.02)  # Delay pequeno para reduzir uso da CPU
