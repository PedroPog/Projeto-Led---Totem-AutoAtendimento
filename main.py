import machine
import neopixel
import time
import sys
import select

# --- CONFIGURAÇÃO ---
LED_PIN = 0
total_leds = 12 
np = neopixel.NeoPixel(machine.Pin(LED_PIN), total_leds)

current_mode = 'OFF'
last_flicker_time = time.ticks_ms()
is_red_on = False

# Controle de Timeout (Segurança)
last_msg_time = time.ticks_ms()
TIMEOUT_MS = 5000 

def set_color(r, g, b):
    for i in range(len(np)):
        np[i] = (r, g, b)
    np.write()

while True:
    # Verifica entrada serial
    if select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()
        last_msg_time = time.ticks_ms() # Reseta o tempo de vida

        if line.startswith('N'):
            try:
                new_count = int(line[1:])
                if new_count > 0:
                    total_leds = new_count
                    np = neopixel.NeoPixel(machine.Pin(LED_PIN), total_leds)
            except: pass
        elif line == 'A':
            current_mode = 'AZUL'; set_color(0, 0, 255)
        elif line == 'V':
            current_mode = 'PISCANDO'
        elif line == 'M':
            current_mode = 'AMARELO'; set_color(255, 251, 0)
        elif line == 'OFF':
            current_mode = 'OFF'; set_color(0, 0, 0)
        elif ',' in line:
            try:
                r, g, b = map(int, line.split(','))
                current_mode = 'CUSTOM'; set_color(r, g, b)
            except: pass

    # Lógica de Timeout: Desliga se o PC sumir
    if current_mode != 'OFF' and time.ticks_diff(time.ticks_ms(), last_msg_time) > TIMEOUT_MS:
        current_mode = 'OFF'
        set_color(0, 0, 0)

    # Lógica do modo Piscando
    if current_mode == 'PISCANDO':
        if time.ticks_diff(time.ticks_ms(), last_flicker_time) > 300:
            if is_red_on:
                set_color(0, 0, 0)
                is_red_on = False
            else:
                set_color(255, 0, 0)
                is_red_on = True
            last_flicker_time = time.ticks_ms()
    
    time.sleep(0.01)