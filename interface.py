import tkinter as tk
from tkinter import ttk, colorchooser
import serial
import serial.tools.list_ports
import time

BAUD_RATE = 9600 

class LEDControllerApp:
    def __init__(self, master):
        self.master = master
        master.title("Painel LED - Controle de Limite e Custom")
        self.serial_connection = None
        self.selected_port = tk.StringVar()
        
        self.setup_ui()
        self.find_ports()
        self.keep_alive_loop()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        main_frame = ttk.Frame(self.master, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # --- CONEXÃO ---
        conn_frame = ttk.LabelFrame(main_frame, text=" Conexão ", padding="5")
        conn_frame.pack(fill='x', pady=5)
        self.port_combobox = ttk.Combobox(conn_frame, textvariable=self.selected_port, state="readonly")
        self.port_combobox.pack(side=tk.LEFT, padx=5, fill='x', expand=True)
        ttk.Button(conn_frame, text="Reload", command=self.find_ports).pack(side=tk.LEFT)
        self.connect_button = ttk.Button(conn_frame, text="Conectar", command=self.connect)
        self.connect_button.pack(side=tk.RIGHT, padx=5)

        # --- CORES PRÉ-DEFINIDAS ---
        color_frame = ttk.LabelFrame(main_frame, text=" Cores Rápidas ", padding="10")
        color_frame.pack(fill='x', pady=5)
        
        btn_row = ttk.Frame(color_frame)
        btn_row.pack(fill='x')
        ttk.Button(btn_row, text="Azul", command=lambda: self.send_command('AZUL')).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(btn_row, text="Amarelo", command=lambda: self.send_command('AMARELO')).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(btn_row, text="Piscante (V)", command=lambda: self.send_command('VERMELHO')).pack(side=tk.LEFT, expand=True, padx=2)

        # --- COR CUSTOMIZADA (RGB) ---
        custom_frame = ttk.LabelFrame(main_frame, text=" Cor Personalizada ", padding="10")
        custom_frame.pack(fill='x', pady=5)

        self.red_var, self.green_var, self.blue_var = tk.IntVar(value=0), tk.IntVar(value=0), tk.IntVar(value=255)

        for label, var, color in [("R", self.red_var, "red"), ("G", self.green_var, "green"), ("B", self.blue_var, "blue")]:
            row = ttk.Frame(custom_frame)
            row.pack(fill='x')
            ttk.Label(row, text=label, foreground=color, width=2, font=('bold')).pack(side=tk.LEFT)
            ttk.Scale(row, from_=0, to=255, orient=tk.HORIZONTAL, variable=var, command=self.send_rgb_from_sliders).pack(side=tk.LEFT, fill='x', expand=True, padx=5)

        ttk.Button(custom_frame, text="Abrir Seletor de Cores", command=self.pick_color_dialog).pack(fill='x', pady=5)

        # --- COMPORTAMENTO ---
        mode_frame = ttk.LabelFrame(main_frame, text=" ⚡ Modo de Exibição ", padding="10")
        mode_frame.pack(fill='x', pady=5)
        
        ttk.Button(mode_frame, text="FIXO", command=lambda: self.send_command('F')).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(mode_frame, text="CASCATA", command=lambda: self.send_command('C')).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(mode_frame, text="PULSA", command=lambda: self.send_command('P')).pack(side=tk.LEFT, expand=True, padx=2)
        
        wave_sub = ttk.Frame(mode_frame)
        wave_sub.pack(side=tk.LEFT, expand=True, padx=2)
        self.wave_width_var = tk.StringVar(value="4")
        ttk.Entry(wave_sub, textvariable=self.wave_width_var, width=3).pack(side=tk.LEFT)
        ttk.Button(wave_sub, text="ONDA", command=self.send_wave_mode).pack(side=tk.LEFT)

        # --- LIMITE DE LEDS ---
        limit_frame = ttk.LabelFrame(main_frame, text=" ⚙️ Configuração Física ", padding="10")
        limit_frame.pack(fill='x', pady=5)
        ttk.Label(limit_frame, text="Ativar apenas:").pack(side=tk.LEFT)
        self.led_limit_var = tk.StringVar(value="10")
        ttk.Entry(limit_frame, textvariable=self.led_limit_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Button(limit_frame, text="Aplicar Limite", command=self.update_led_limit).pack(side=tk.LEFT)

        # --- DESLIGAR ---
        ttk.Button(main_frame, text=" DESLIGAR TUDO", command=lambda: self.send_command('OFF')).pack(fill='x', pady=10)
        
        self.status_label = ttk.Label(main_frame, text="Desconectado", foreground="gray")
        self.status_label.pack()

    def send_command(self, command):
        if self.serial_connection and self.serial_connection.is_open:
            try: 
                self.serial_connection.write((command + '\n').encode('utf-8'))
            except: 
                self.disconnect()

    def send_rgb_from_sliders(self, event=None):
        cmd = f"{self.red_var.get()},{self.green_var.get()},{self.blue_var.get()}"
        self.send_command(cmd)

    def pick_color_dialog(self):
        # A correção está aqui: desempacotamos a tupla (rgb, hex)
        # askcolor retorna algo como: ((255.0, 0.0, 0.0), '#ff0000')
        rgb_tuple, hex_code = colorchooser.askcolor(title="Selecione a Cor")
        
        if rgb_tuple:
            self.red_var.set(int(rgb_tuple[0]))
            self.green_var.set(int(rgb_tuple[1]))
            self.blue_var.set(int(rgb_tuple[2]))
            self.send_rgb_from_sliders()

    def update_led_limit(self):
        val = self.led_limit_var.get()
        if val.isdigit(): self.send_command(f"N{val}")

    def send_wave_mode(self):
        w = self.wave_width_var.get()
        if w.isdigit(): self.send_command(f"W{w}")

    def keep_alive_loop(self):
        if self.serial_connection and self.serial_connection.is_open:
            try: self.serial_connection.write(b".\n")
            except: pass
        self.master.after(2000, self.keep_alive_loop)

    def find_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_list = [port.device for port in ports]
        self.port_combobox['values'] = self.port_list
        if self.port_list: self.selected_port.set(self.port_list[0])

    def connect(self):
        port = self.selected_port.get()
        if not port: return
        try:
            self.serial_connection = serial.Serial(port, BAUD_RATE, timeout=0.1)
            self.serial_connection.dtr = True  # Ativa o sinal de pronto
            self.serial_connection.rts = True  # Ativa o sinal de fluxo
            time.sleep(2)
            self.status_label.config(text="Conectado", foreground="green")
            self.send_rgb_from_sliders() 
        except Exception as e:
            self.status_label.config(text=f"Erro: {e}", foreground="red")

    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b"OFF\n")
                self.serial_connection.close()
            except: pass
        self.status_label.config(text="Desconectado", foreground="gray")

    def on_closing(self):
        self.disconnect()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LEDControllerApp(root)
    root.mainloop()