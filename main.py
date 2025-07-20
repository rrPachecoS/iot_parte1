#from hora_actual import connect_wifi, sync_ntp_time, get_current_datetime, display_time_on_oled
import utime
from machine import Pin, PWM, I2C
from config import *
import keyStick
from ssd1306 import SSD1306_I2C
import framebuf
import img
from icon import ( # Assuming these icons are defined in icon.py
    icon_reloj_digital,
    icon_crono,
    icon_reloj_analogico,
    icon_sokoban,
    icon_calculadora_graf,
    icon_temperatura
)

# Inicialización de hardware
i2c = I2C(OLED_I2C_ID, scl=Pin(OLED_SCL_PIN), sda=Pin(OLED_SDA_PIN))
buzzer = PWM(Pin(BUZZER_PIN))
buzzer.freq(BUZZER_FREQ)
#fondo y caratula
image_data=([])
image_data=img.fondo_imagen()
logo_data=([])
logo_data=img.logo_imagen()
fb = framebuf.FrameBuffer(image_data, 128, 64, framebuf.MONO_HLSB)
fb2= framebuf.FrameBuffer(logo_data,46,46,framebuf.MONO_HLSB)
# Variables globales
current_mode = 0
modes = [
    {"name": "Reloj digital", "module": "modo_reloj", "icon": icon_reloj_digital},
    {"name": "Cronómetro", "module": "modo_crono", "icon": icon_crono},
    {"name": "Reloj analógico", "module": "modo_reloj_analogico", "icon": icon_reloj_analogico},
    {"name": "Juego Sokoban", "module": "modo_sokoban", "icon": icon_sokoban},
    {"name": "Calculadora Graf", "module": "modo_calculadora", "icon": icon_calculadora_graf},
    {"name": "Monitor temp.", "module": "modo_temperatura", "icon": icon_temperatura}
]
# Icon and menu dimensions
ICON_WIDTH = 60
ICON_HEIGHT = 60
MENU_ITEM_HEIGHT = 64 # Height for icon + some padding for name

def init_oled():
    return SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=OLED_ADDR)

def play_sound(freq, duration_ms):
    buzzer.freq(freq)
    buzzer.duty_u16(BUZZER_DUTY)
    utime.sleep_ms(duration_ms)
    buzzer.duty_u16(0)

def show_start_screen(oled):
    oled.fill(0)
    #show_image(fb2,2,2,8)
    oled.blit(fb,0,0)
    oled.show()
    play_sound(523, 100)
    play_sound(659, 100)
    play_sound(784, 200)


def show_welcome_screen(oled):
    oled.fill(0)
    #show_image(fb2,2,2,8)
    
    print('tercera imagen')
    oled.text('DIPLOMADO IoT 3',0,0)
    oled.blit(fb2,0,8)
    oled.text('Modulo #3',50,17)
    oled.text('Sys Emb',60,30)
    oled.text('Proj Final',50,40)
    oled.text('Raul Pacheco',17,55)    
    oled.show()
    play_sound(523, 100)
    play_sound(659, 100)
    play_sound(784, 200)
    #fb2=([])

def draw_menu(oled, current_mode_index):
    oled.fill(0)
    
    # Calculate the vertical offset for scrolling
    # We want the selected icon to be centered or near the top, depending on total items
    
    display_height = oled.height
    num_modes = len(modes)

    # Determine visible range of icons
    # Display one icon at a time, vertically centered
    
    # Calculate Y position to center the selected icon vertically
    y_offset_for_centering = (display_height - ICON_HEIGHT) // 2

    for i, mode in enumerate(modes):
        # Only draw the current selected mode
        if i == current_mode_index:
            # Draw the icon
            fb = framebuf.FrameBuffer(mode["icon"], ICON_WIDTH, ICON_HEIGHT, framebuf.MONO_VLSB)
            # Center the icon horizontally
            icon_x = (oled.width - ICON_WIDTH) // 2
            oled.blit(fb, icon_x, y_offset_for_centering)
            
            # Draw the mode name below the icon
            name_y = y_offset_for_centering + ICON_HEIGHT + 2 # A small gap
            text_width = len(mode["name"]) * 8 # Assuming 8 pixels per character width
            name_x = (oled.width - text_width) // 2
            oled.text(mode["name"], name_x, name_y)
            
            # Draw a selection indicator (e.g., an outline around the icon or a pointer)
            # Example: a rectangle around the icon
            oled.rect(icon_x - 2, y_offset_for_centering - 2, ICON_WIDTH + 4, ICON_HEIGHT + 4, 1)

    oled.show()

def run_selected_mode(oled, mode_info):
    try:
        # Importar el módulo dinámicamente
        module = __import__(mode_info["module"])
        
        # Mostrar mensaje de carga
        oled.fill(0)
        oled.text(f"Cargando...", 0, 0)
        oled.text(mode_info["name"], 0, 20)
        oled.show()
        
        # Ejecutar la función main del módulo importado
        module.main(oled, keyStick.get_direction, play_sound)
        
    except Exception as e:
        # Manejo de errores
        oled.fill(0)
        oled.text("Error al cargar", 0, 0)
        oled.text(mode_info["module"], 0, 10)
        oled.text(str(e), 0, 30)
        oled.show()
        utime.sleep(2)
        play_sound(100, 500)

def main():
    oled = init_oled()
    show_start_screen(oled)
    utime.sleep(3)
    show_welcome_screen(oled)
    utime.sleep(2)
    
    while True:
        selected_mode = None
        current_mode_index = 0
        
        while selected_mode is None:
            draw_menu(oled, current_mode_index)
            direction = keyStick.get_direction()
            
            if direction == "up":
                current_mode_index = (current_mode_index - 1) % len(modes)
                play_sound(300, 50)
            elif direction == "down":
                current_mode_index = (current_mode_index + 1) % len(modes)
                play_sound(300, 50)
            elif direction == "center":
                play_sound(600, 100)
                selected_mode = modes[current_mode_index]
            
            utime.sleep_ms(50)
        
        run_selected_mode(oled, selected_mode)

if __name__ == "__main__":
    main()