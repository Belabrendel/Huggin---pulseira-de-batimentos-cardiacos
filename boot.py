# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)

import network
import time

# Função para conectar ao Wi-Fi
def connect_to_wifi(ssid, password, timeout=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Ativando Wi-Fi:", wlan.active())

    if wlan.isconnected():
        print("Já conectado ao Wi-Fi:", wlan.ifconfig())
        return True

    print(f"Conectando ao Wi-Fi: SSID={ssid}")
    wlan.connect(ssid, password)

    start_time = time.time()
    while not wlan.isconnected():
        print("Tentando conectar...")
        if time.time() - start_time > timeout:
            print("Erro: Timeout ao tentar conectar ao Wi-Fi.")
            return False
        time.sleep(1)

    print("Conectado ao Wi-Fi:", wlan.ifconfig())
    return True


# Substitua pelas suas credenciais de Wi-Fi
SSID = "Citi 6"
PASSWORD = "1cbe991a14"

if not connect_to_wifi(SSID, PASSWORD):
    print("Falha ao conectar ao Wi-Fi. Verifique as credenciais ou a rede.")

# Inicia o WebREPL
try:
    import webrepl
    webrepl.start()
    print("WebREPL iniciado com sucesso.")
except Exception as e:
    print("Erro ao iniciar o WebREPL:", e)
