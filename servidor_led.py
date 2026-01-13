import threading
from flask import Flask, request
import serial
import time

app = Flask(__name__)
ser = serial.Serial('/dev/ttyACM1', 9600, timeout=0.1)

def keep_alive():
    """Envia um ponto para o Pico a cada 3 segundos para ele não desligar"""
    while True:
        try:
            if ser.is_open:
                ser.write(b'.\n')
        except: pass
        time.sleep(3)

# Inicia a thread de segurança
threading.Thread(target=keep_alive, daemon=True).start()

@app.route('/led')
def control_led():
    cmd = request.args.get('cmd')
    if cmd:
        ser.write((cmd + '\n').encode())
        return "OK", 200
    return "Erro", 400


if __name__ == '__main__':
    app.run(port=5050)