from machine import sleep, SoftI2C, Pin
from utime import ticks_diff, ticks_us, ticks_ms
from max30102 import MAX30102, MAX30105_PULSE_AMP_HIGH
from heartbeat_example import HeartRateMonitor
import time

class StateMachine:
    
    def _init_(self, sample_rate=100, window_size=10, smoothing_window=5):
        """
        state 0 = check_heartbeat
        state 1 = pre_send_out
        state 2 = send_out_notify
        """
        self.state = 0
        self.max_viable_heartbeat = 400
        self.max_tries = 25
        self.current_tries = 0
        #max seconds until someone is notified
        self.max_seconds = 20
        
        i2c = SoftI2C(
            sda=Pin(21),  # Here, use your I2C SDA pin
            scl=Pin(22),  # Here, use your I2C SCL pin
            freq=100000,
        )  # Fast: 400kHz, slow: 100kHz

        # Sensor instance
        self.sensor = MAX30102(i2c=i2c)  # An I2C instance is required

        # Scan I2C bus to ensure that the sensor is connected
        if self.sensor.i2c_address not in i2c.scan():
            print("Sensor not found.")
            return
        elif not (self.sensor.check_part_id()):
            # Check that the targeted sensor is compatible
            print("I2C device ID not corresponding to MAX30102 or MAX30105.")
            return
        else:
            print("Sensor connected and recognized.")

        # Load the default configurations
        print("Setting up sensor with default configuration.", "\n")
        self.sensor.setup_sensor()

        # Set the sample rate to 400: 400 samples/s are collected by the sensor
        sensor_sample_rate = 400
        self.sensor.set_sample_rate(sensor_sample_rate)

        # Set the number of samples to be averaged per each reading
        sensor_fifo_average = 8
        self.sensor.set_fifo_average(sensor_fifo_average)

        # Set LED brightness to a medium value
        self.sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_HIGH)

        # Expected acquisition rate: 400 Hz / 8 = 50 Hz
        actual_acquisition_rate = int(sensor_sample_rate / sensor_fifo_average)
            
        self.hr_monitor = HeartRateMonitor(
            # Select a sample rate that matches the sensor's acquisition rate
            sample_rate=actual_acquisition_rate,
            # Select a significant window size to calculate the heart rate (2-5 seconds)
            window_size=int(actual_acquisition_rate * 3),
            )

        # Setup to calculate the heart rate every 2 seconds
        self.hr_compute_interval = 2  # seconds
        self.ref_time = ticks_ms()  # Reference time

    def check_heartbeat(self):
        # Verifica se o sensor possui dados disponíveis
        self.sensor.check()
        self.hr_compute_interval = 5  # Ajuste o intervalo para 5 segundos, por exemplo


        # Verifica se há amostras disponíveis na fila do sensor
        if self.sensor.available():
            red_reading = self.sensor.pop_red_from_storage()
            ir_reading = self.sensor.pop_ir_from_storage()

            # Verifica se as leituras são válidas
            if red_reading is not None and ir_reading is not None:
                # Adiciona a amostra de IR ao monitor de frequência cardíaca
                self.hr_monitor.add_sample(ir_reading)
            else:
                print("Leitura inválida do sensor (red ou ir).")
        else:
            print("Sem dados disponíveis no sensor.")
            return {"heart_rate": 78, "state": self.state} #ta retornando nulo 


        # Calcula a frequência cardíaca periodicamente a cada hr_compute_interval segundos
        if ticks_diff(ticks_ms(), self.ref_time) / 1000 > self.hr_compute_interval:
            # Calcula a frequência cardíaca
            heart_rate = self.hr_monitor.calculate_heart_rate()
            self.ref_time = ticks_ms()  # Reseta o tempo de referência

            if heart_rate is not None:
                print("Heart Rate: {:.0f} BPM".format(heart_rate))
                return {"heart_rate": heart_rate, "state": self.state} #ta retornando nulo 
            
            else:
                print("0 BPM")

    def run(self):
        if self.state == 0:
            return self.check_heartbeat()
    
        if self.state == 1:
            return self.pre_send_out()
        
        if self.state == 2:
            return self.send_out_notify()

    # Implementação do método pre_send_out
    def pre_send_out(self):
        # Iniciar contagem do tempo
        start_timer = time.time()
        
        if (time.time() - start_timer) < self.max_seconds:
            if self.send_app_request():
                print("Usuário afirmou estar bem. Voltando a monitorar batimento.")
                self.state = 0
                return
        else:
            print("Usuário não afirmou estar bem. Notificando responsável")
            self.state = 2

    # Enviar notificação
    def send_out_notify(self):
        print("Notificando responsável sobre a elevação do batimento.")
        # Lógica de notificação aqui
        self.state = 0
