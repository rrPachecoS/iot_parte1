from machine import Pin, ADC
from config import *
import utime

# Inicialización de pines
joy_x = ADC(Pin(JOY_X_PIN))
joy_y = ADC(Pin(JOY_Y_PIN))
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

# Variables para detección de doble clic
last_press_time = 0
double_click_threshold = 400  # ms entre clics para considerar doble clic

def get_direction():
    global last_press_time
    
    x_val = joy_x.read_u16()
    y_val = joy_y.read_u16()
    
    # Determinar dirección
    direction = None
    
    if x_val < JOY_THRESHOLD_LOW:
        direction = "left"
    elif x_val > JOY_THRESHOLD_HIGH:
        direction = "right"
    elif y_val < JOY_THRESHOLD_LOW:
        direction = "up"
    elif y_val > JOY_THRESHOLD_HIGH:
        direction = "down"
    elif button.value() == 0:  # Botón presionado
        utime.sleep_ms(50)  # Debounce
        if button.value() == 0:
            current_time = utime.ticks_ms()
            # Verificar si es un doble clic
            if utime.ticks_diff(current_time, last_press_time) < double_click_threshold:
                direction = "double_click"
            last_press_time = current_time
            # Si no es doble clic, retornamos "center" después del timeout
            while button.value() == 0:  # Esperar a que suelten el botón
                pass
            if direction != "double_click":
                direction = "center"
    
    return direction