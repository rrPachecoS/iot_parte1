import utime
from machine import ADC, Pin

def main(oled, get_direction, play_sound):
    # Configurar ADC para sensor de temperatura
    temp_sensor = ADC(4)  # ADC4 es el sensor interno en RP2040
    conversion_factor = 3.3 / 65535
    last_update = 0
    
    while True:
        current_time = utime.ticks_ms()
        
        # Verificar entrada del usuario continuamente
        direction = get_direction()
        if direction == "double_click":
            play_sound(200, 100)
            play_sound(100, 100)
            return
        
        # Actualizar temperatura solo cada segundo
        if utime.ticks_diff(current_time, last_update) >= 1000:
            # Leer temperatura (ejemplo para RP2040)
            reading = temp_sensor.read_u16() * conversion_factor
            temperature = 27 - (reading - 0.706)/0.001721
            
            oled.fill(0)
            oled.text("Temperatura", 0, 0)
            oled.text("Actual:", 0, 20)
            oled.text("{:.1f} C".format(temperature), 0, 30)
            
            # Gráfico simple
            temp_level = min(max(int((temperature - 10) * 3), 0), 80)
            oled.fill_rect(0, 50, temp_level, 10, 1)
            oled.rect(0, 50, 80, 10, 1)
            
            oled.show()
            last_update = current_time
        
        # Pequeña pausa para no saturar la CPU
        utime.sleep_ms(50)