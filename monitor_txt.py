import serial
import serial.tools.list_ports
import time
import threading

# --- CONFIGURAÇÃO SERIAL (A mesma lógica de Auto-Detect) ---
SERIAL_LOCK = threading.Lock()
ser = None

def find_pico_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "PICO" in port.description.upper() or "2E8A" in port.hwid.upper():
            return port.device
    return None

def connect_to_pico():
    global ser
    port = find_pico_port()
    with SERIAL_LOCK:
        if port:
            try:
                if ser and ser.is_open: ser.close()
                ser = serial.Serial(port, 9600, timeout=0.1)
                ser.dtr = True
                ser.rts = True
                print(f"✅ Conectado ao Pico: {port}")
                return True
            except: pass
    return False

# --- LÓGICA DO MONITOR ---
ARQUIVO_ESTADO = "estado_led.txt"

def rodar_monitor_passivo():
    global ser
    ultimo_estado = ""
    print(f"👀 Observando alterações em {ARQUIVO_ESTADO}...")

    while True:
        # 1. Tenta manter a conexão viva
        if not ser or not ser.is_open:
            connect_to_pico()
            time.sleep(2)
            continue

        try:
            # 2. Lê o arquivo de estado
            if not os.path.exists(ARQUIVO_ESTADO):
                with open(ARQUIVO_ESTADO, "w") as f: f.write("OFF")
            
            with open(ARQUIVO_ESTADO, "r") as f:
                estado_atual = f.read().strip()

            # 3. Se o estado mudou no arquivo, envia para o LED
            if estado_atual != ultimo_estado:
                print(f"🔄 Mudança detectada: {estado_atual}")
                with SERIAL_LOCK:
                    ser.write((estado_atual + '\n').encode('utf-8'))
                    ser.flush()
                ultimo_estado = estado_atual
            
            # 4. Sinal de keep-alive para o Pico (opcional, para manter LED interno)
            with SERIAL_LOCK:
                ser.write(b'.\n')

        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")
            ser = None # Força reconexão
        
        time.sleep(0.5) # Frequência de verificação (500ms)

if __name__ == "__main__":
    import os
    rodar_monitor_passivo()