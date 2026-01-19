## Projeto Led Totem Auto-Atedimento

### Componentes:
 <li>Raspberry Pi Pico</li>
 <li>Fita led WS2512B PCB white</li>
 <li>Fonte Externa 5V 10A (Para alimetação da fita LED)</li>
 <li>Cabo usb V8 (Comunicação Pico para computador)</li>
 <li>Resistor 470 Ω (Somente para proteção ante surto)</li>


##### Obs. calculo para fonte de led 150 LEDs x 60mA = 9.000mA  (9 Ampéres)

### Projetos:

#### Interface.py

    Criado um projeto visual para ficar facil a configuração e teste de cores para facilitar a configuração para o embarcado.


    * Conexão: 
        > Realiza a consulta das portas e realiza a comunição ao embarcado e filtra alguns possiveis erros.
    * Mode Pré-definidos:
        > Tres opção de cores definida já no embarcado sendo A: Azul V: Vermelho piscante M: Amarelo.
    * Controle Customizado:
        > Para testar outras opções de cores dentro da paleta RGB.
    * Configuração da fita:
        > Realizar a ativação de somente um determinada quantia de ledm sendo default 12.
        *obs. necessario mais teste para verificar a efetividade.

#### Servidor_led.py
    
    Projeto criado como definitivo, porem falta a flexibilidade de porta e configuração de reconeção.

    Projeto tem o entuito de facilitar a comunicação com outras linguagem sendo a comunição de comando via api.

    * Comados aceitos:
        > Get http://localhost:5050/led?cmd=?
            > A: Azul total
            > V: Vermelho Piscante
            > M: Amarelo total
            > OFF: Desligar

#### Main.py

    Projeto do embarcado codigo que sera carregado no PI para realziar a comunicação aos led, caso queira realziar a troca das cores default deve ser realziado aqui.


#### Criado: [Pedro Vieira](https://github.com/PedroPog)     
#### Empresa que utiliza o projeto: [Remarca Automção](https://www.remarca.net/)