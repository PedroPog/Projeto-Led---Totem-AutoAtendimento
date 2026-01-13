import tkinter as tk
from tkinter import ttk, colorchooser
import serial
import serial.tools.list_ports
import time
import sys

BAUD_RATE = 9600 
MODES = {
    'A': "Azul Total",
    'V': "Vermelho Piscante",
    'M': "Amarelo Total"
}

class LEDControllerApp:
    def __init__(self, master):
        self.master = master
        master.title("Controle LED Pico")
        self.serial_connection = None
        self.selected_port = tk.StringVar()
        
        self.setup_ui()
        self.find_ports()
        
        # Inicia o loop de keep-alive para evitar o timeout do Pico
        self.keep_alive_loop()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def keep_alive_loop(self):
        """Envia um sinal 'vazio' a cada 2 segundos para o Pico não desligar."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b".\n")
            except: pass
        self.master.after(2000, self.keep_alive_loop)

    def update_led_count(self):
        count = self.led_count_var.get()
        if count.isdigit():

            self.send_command(f"N{count}")     

    def find_ports(self):

        ports = serial.tools.list_ports.comports()
        self.port_list = [port.device for port in ports]
        
        self.port_combobox['values'] = self.port_list
        if self.port_list:
            self.selected_port.set(self.port_list[0])

    def connect(self):
        port = self.selected_port.get()
        if not port: return
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            
            self.serial_connection = serial.Serial(port, BAUD_RATE, timeout=0.1) 
            time.sleep(2) # Aguarda inicialização do Pico
            
            self.status_label.config(text=f"CONECTADO", foreground="green")
            self.toggle_controls(True)
            self.connect_button.config(text="Desconectar", command=self.disconnect)
            
            # LIGA O LED IMEDIATAMENTE COM O VALOR ATUAL DOS SLIDERS
            self.send_rgb_from_sliders()

        except Exception as e:
            self.status_label.config(text=f"ERRO: {e}", foreground="red")


    def disconnect(self):

        if self.serial_connection and self.serial_connection.is_open:
            try:

                self.serial_connection.write(b"OFF\n")
                self.serial_connection.flush()
                time.sleep(0.1) 
            except:
                pass
            
            self.serial_connection.close()
            self.status_label.config(text="DESCONECTADO", foreground="blue")
            self.toggle_controls(False)
            self.connect_button.config(text="Conectar", command=self.connect)

    def on_closing(self):
        
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b"OFF\n")
                self.serial_connection.flush()
                time.sleep(0.1)
            except:
                pass
        self.disconnect()
        self.master.destroy()

    def toggle_controls(self, state):
        
        
        new_state = tk.NORMAL if state else tk.DISABLED
        

        for child in self.mode_frame.winfo_children():
            widget_type = child.winfo_class()
            if widget_type in ('TButton', 'Button'):
                 child.config(state=new_state)


        self.red_slider.config(state=new_state)
        self.green_slider.config(state=new_state)
        self.blue_slider.config(state=new_state)
        self.send_rgb_button.config(state=new_state)
        self.color_picker_button.config(state=new_state)


    def send_command(self, command):

        if self.serial_connection and self.serial_connection.is_open:
           
            try:
                self.serial_connection.write((command + '\n').encode('utf-8'))
                print(f"Comando enviado: {command}")
            except Exception as e:
                self.status_label.config(text=f"Erro de envio: {e}", foreground="red")
                self.disconnect()
        else:
            self.status_label.config(text="Não conectado.", foreground="red")

    def send_rgb_from_sliders(self, event=None):

        r = self.red_var.get()
        g = self.green_var.get()
        b = self.blue_var.get()
        command = f"{r},{g},{b}"
        self.send_command(command)
        
    def pick_color_dialog(self):
        color_code, rgb_tuple = colorchooser.askcolor(title="Selecione a Cor")
        
        if rgb_tuple:
            r, g, b = rgb_tuple
            
            self.red_var.set(int(r))
            self.green_var.set(int(g))
            self.blue_var.set(int(b))
            
            self.send_rgb_from_sliders()


    def setup_ui(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        connection_frame = ttk.LabelFrame(main_frame, text="Conexão", padding="10")
        connection_frame.pack(fill='x', pady=10)
        
        ttk.Label(connection_frame, text="Porta Serial:").pack(side=tk.LEFT, padx=5)
        
        self.port_combobox = ttk.Combobox(connection_frame, textvariable=self.selected_port, state="readonly", width=15)
        self.port_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(connection_frame, text="Recarregar", command=self.find_ports).pack(side=tk.LEFT, padx=5)
        
        self.connect_button = ttk.Button(connection_frame, text="Conectar", command=self.connect)
        self.connect_button.pack(side=tk.RIGHT, padx=5)

        self.status_label = ttk.Label(main_frame, text="Desconectado", foreground="blue")
        self.status_label.pack(pady=5)
        
        # --- 2. CONTROLES DE MODO ---
        self.mode_frame = ttk.LabelFrame(main_frame, text="Modos Pré-definidos", padding="10")
        self.mode_frame.pack(fill='x', pady=10)
        
        for char_code, name in MODES.items():
            ttk.Button(self.mode_frame, text=name, command=lambda code=char_code: self.send_command(code)).pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        
        # --- 3. CONTROLES CUSTOMIZADOS (RGB) ---
        self.control_frame = ttk.LabelFrame(main_frame, text="Controle Customizado (RGB)", padding="10")
        self.control_frame.pack(fill='x', pady=10)

        # Variáveis para os sliders
        self.red_var = tk.IntVar(value=0)
        self.green_var = tk.IntVar(value=0)
        self.blue_var = tk.IntVar(value=0)
        
        # Sliders e Rótulos (Red)
        ttk.Label(self.control_frame, text="Vermelho (R):").pack(pady=2)
        self.red_slider = ttk.Scale(self.control_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.red_var, command=self.send_rgb_from_sliders)
        self.red_slider.pack(fill='x', padx=10)
        
        # Sliders e Rótulos (Green)
        ttk.Label(self.control_frame, text="Verde (G):").pack(pady=2)
        self.green_slider = ttk.Scale(self.control_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.green_var, command=self.send_rgb_from_sliders)
        self.green_slider.pack(fill='x', padx=10)
        
        # Sliders e Rótulos (Blue)
        ttk.Label(self.control_frame, text="Azul (B):").pack(pady=2)
        self.blue_slider = ttk.Scale(self.control_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.blue_var, command=self.send_rgb_from_sliders)
        self.blue_slider.pack(fill='x', padx=10)

        # Botão para enviar RGB e Color Picker
        buttons_rgb_frame = ttk.Frame(self.control_frame)
        buttons_rgb_frame.pack(fill='x', pady=10)
        
        self.send_rgb_button = ttk.Button(buttons_rgb_frame, text="Aplicar RGB (Sliders)", command=self.send_rgb_from_sliders)
        self.send_rgb_button.pack(side=tk.LEFT, expand=True, padx=5)

        self.color_picker_button = ttk.Button(buttons_rgb_frame, text="Seletor de Cores...", command=self.pick_color_dialog)
        self.color_picker_button.pack(side=tk.RIGHT, expand=True, padx=5)

        # --- NOVO: CONFIGURAÇÃO DE QUANTIDADE DE LEDS ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuração da Fita", padding="10")
        config_frame.pack(fill='x', pady=5)
        
        ttk.Label(config_frame, text="Qtd. LEDs:").pack(side=tk.LEFT, padx=5)
        self.led_count_var = tk.StringVar(value="12")
        self.led_count_entry = ttk.Entry(config_frame, textvariable=self.led_count_var, width=10)
        self.led_count_entry.pack(side=tk.LEFT, padx=5)
        
        self.update_led_button = ttk.Button(config_frame, text="Atualizar Fita", 
                                            command=self.update_led_count)
        self.update_led_button.pack(side=tk.LEFT, padx=5)
        
        # Inicia os controles desabilitados
        self.toggle_controls(False)

    def on_closing(self):
        """Garante o fechamento da conexão serial ao fechar a janela."""
        self.disconnect()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LEDControllerApp(root)
    root.mainloop()