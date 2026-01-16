import machine
import neopixel
import time
import sys
import select

# --- CONFIGURAÇÃO ---
LED_PIN = 5
MAX_LEDS = 300
np = neopixel.NeoPixel(machine.Pin(LED_PIN), MAX_LEDS)
limit_leds = 12 

# Configuração do LED Interno
# 'LED' funciona para Pico comum (pino 25) e Pico W
led_interno = machine.Pin('LED', machine.Pin.OUT)

# Estados de Controle
current_behavior = 'FIXO' 
current_color_mode = 'AZUL'

last_update_time = time.ticks_ms()
anim_step = 0
pulse_direction = 1
current_rgb = (0, 0, 255)
is_red_on = False
wave_width = 4

def clear():
    for i in range(MAX_LEDS): np[i] = (0, 0, 0)
    np.write()
    led_interno.off() # Desliga o interno ao limpar tudo

def set_all_limited(color):
    for i in range(MAX_LEDS):
        if i < limit_leds:
            np[i] = color
        else:
            np[i] = (0, 0, 0)
    np.write()

while True:
    if select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()
        
        # Indica recebimento de comando piscando o LED interno rapidamente
        led_interno.on()
        
        if line.startswith('N'):
            try:
                limit_leds = int(line[1:])
                clear()
            except: pass
        elif line == 'A':
            current_color_mode = 'AZUL'; current_rgb = (0, 0, 255)
            if current_behavior == 'CASCATA': anim_step = 0; clear()
        elif line == 'V':
            current_color_mode = 'PISCANTE'; anim_step = 0
        elif line == 'M':
            current_color_mode = 'AMARELO'; current_rgb = (255, 251, 0)
            if current_behavior == 'CASCATA': anim_step = 0; clear()
        elif line == 'OFF':
            current_color_mode = 'OFF'; clear()
        elif ',' in line:
            try:
                r, g, b = map(int, line.split(','))
                current_rgb = (r, g, b); current_color_mode = 'RGB'
                if current_behavior == 'CASCATA': anim_step = 0; clear()
            except: pass

        # Comportamentos
        elif line == 'FIXO': current_behavior = 'FIXO'
        elif line == 'C': current_behavior = 'CASCATA'; anim_step = 0; clear()
        elif line == 'PULSA': current_behavior = 'PULSA'; anim_step = 0; clear()
        elif line.startswith('W'):
            current_behavior = 'ONDA'; anim_step = 0
            try: wave_width = int(line[1:])
            except: wave_width = 4

    # --- LÓGICA DE EXIBIÇÃO ---
    now = time.ticks_ms()

    if current_color_mode == 'OFF':
        led_interno.off()
        pass

    else:
        # Se não estiver OFF, mantém o LED interno ligado para indicar atividade
        led_interno.on()

        if current_color_mode == 'PISCANTE':
            if time.ticks_diff(now, last_update_time) > 400:
                if is_red_on:
                    set_all_limited((0,0,0)); is_red_on = False
                else:
                    set_all_limited((255, 0, 0)); is_red_on = True
                last_update_time = now

        elif current_behavior == 'FIXO':
            set_all_limited(current_rgb)

        elif current_behavior == 'CASCATA':
            if time.ticks_diff(now, last_update_time) > 150:
                if anim_step < limit_leds:
                    np[anim_step] = current_rgb
                    np.write()
                    anim_step += 1
                last_update_time = now

        elif current_behavior == 'PULSA':
            if time.ticks_diff(now, last_update_time) > 30:
                brightness = anim_step / 100.0
                r = int(current_rgb[0] * brightness)
                g = int(current_rgb[1] * brightness)
                b = int(current_rgb[2] * brightness)
                set_all_limited((r, g, b))
                anim_step += (2 * pulse_direction)
                if anim_step >= 100 or anim_step <= 0:
                    pulse_direction *= -1
                last_update_time = now

        elif current_behavior == 'ONDA':
            if time.ticks_diff(now, last_update_time) > 150:
                for i in range(MAX_LEDS):
                    if i < limit_leds:
                        if (i - anim_step) % limit_leds < wave_width:
                            np[i] = current_rgb
                        else:
                            np[i] = (0, 0, 0)
                    else:
                        np[i] = (0, 0, 0)
                np.write()
                anim_step = (anim_step + 1) % limit_leds
                last_update_time = now

    time.sleep(0.001)
