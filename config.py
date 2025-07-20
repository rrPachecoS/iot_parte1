# config.py
# Configuración de pines para Raspberry Pi Pico
##


# Pantalla OLED (I2C)
OLED_I2C_ID = 0
OLED_SCL_PIN = 5
OLED_SDA_PIN = 4
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_ADDR = 0x3C

# Joystick (Analógico)
JOY_X_PIN = 26
JOY_Y_PIN = 27
JOY_THRESHOLD_LOW = 10000   # Umbral mínimo para detección de movimiento
JOY_THRESHOLD_HIGH = 60000  # Umbral máximo para detección de movimiento
JOY_CENTER = 32768          # Valor aproximado en posición central

# Buzzer
BUZZER_PIN = 14
BUZZER_FREQ = 1000         # Frecuencia base en Hz
BUZZER_DUTY = 30000        # Ciclo de trabajo (0-65535)

# Botón
BUTTON_PIN = 15

# Ultrasoico
ECHO_HC_04 = 8               # ULTRASONICO
TRIG_HC_04 = 7               # ULTRASONICO

# LED RGB
RGB_RED_PIN = 16           # Canal rojo (PWM)
RGB_GREEN_PIN = 17         # Canal verde (PWM)
RGB_BLUE_PIN = 18          # Canal azul (PWM)
RGB_FREQ = 1000            # Frecuencia PWM para RGB

# Teclado matricial (Filas)
KEY_ROW1 = 10              # Fila 1 del teclado
KEY_ROW2 = 11              # Fila 2 del teclado
KEY_ROW3 = 12              # Fila 3 del teclado
KEY_ROW4 = 13              # Fila 4 del teclado

# Configuración PWM general
PWM_FREQ = 1000            # Frecuencia base para todos los PWM