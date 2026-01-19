import threading
from flask import Flask, request
import serial
import serial.tools.list_ports
import time

app = Flask(__name__)
ser = None
SERIAL_LOCK = threading.Lock() # Garante que a thread e a API não conflitem na porta

def find_pico_port():
    """Varre o sistema em busca do Raspberry Pi Pico pelo ID de hardware."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # 2E8A:0005 é o ID padrão do Raspberry Pi Pico com MicroPython
        if "PICO" in port.description.upper() or "2E8A" in port.hwid.upper():
            return port.device
    return None

def connect_to_pico():
    """Tenta estabelecer a conexão serial configurando DTR e RTS para evitar bloqueios."""
    global ser
    port = find_pico_port()
    
    with SERIAL_LOCK:
        if port:
            try:
                if ser and ser.is_open:
                    ser.close()
                
                # Configuração robusta para Windows e Linux
                ser = serial.Serial(port, 9600, timeout=0.1)
                ser.dtr = True
                ser.rts = True
                time.sleep(1) # Tempo para o Pico estabilizar a conexão
                print(f"Conectado ao Pico na porta: {port}")
                return True
            except Exception as e:
                print(f" Erro ao abrir a porta {port}: {e}")
        else:
            print(" Pico não encontrado. Aguardando conexão USB...")
    return False

def keep_alive_worker():
    """Thread que mantém o Pico ativo e tenta reconectar automaticamente se o cabo for removido."""
    global ser
    while True:
        try:
            with SERIAL_LOCK:
                if ser and ser.is_open:
                    ser.write(b'.\n') # Sinal de vida para o Pico
                else:
                    connect_to_pico()
        except:
            ser = None
        time.sleep(3) # Verifica a cada 3 segundos

connect_to_pico()

threading.Thread(target=keep_alive_worker, daemon=True).start()

@app.route('/led')
def control_led():
    """
    Controla o LED. Aceita comandos como:
    - /led?cmd=AZUL (Azul)
    - /led?cmd=P (Efeito Pulso)
    - /led?cmd=N15 (Limite de 15 LEDs)
    - /led?cmd=RECONNECT (Força busca de porta)
    """
    cmd = request.args.get('cmd')
    
    if cmd == "RECONNECT":
        if connect_to_pico():
            return "Pico reconectado com sucesso!", 200
        return "Falha ao localizar o Pico.", 404

    if not ser or not ser.is_open:
        return "Erro: Pico não conectado. Verifique o cabo ou use cmd=RECONNECT", 503

    if cmd:
        try:
            with SERIAL_LOCK:
                # Envia o comando com quebra de linha para o Pico processar via readline()
                ser.write((cmd + '\n').encode('utf-8'))
                ser.flush()
            return f"OK: {cmd}", 200
        except Exception as e:
            return f"Erro ao enviar comando: {e}", 500
            
    return "Erro: Parâmetro 'cmd' ausente.", 400

if __name__ == '__main__':
    # host='0.0.0.0' permite que outros dispositivos na rede acessem a API
    app.run(host='0.0.0.0', port=5050, debug=False)