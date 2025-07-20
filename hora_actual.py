import network
import utime
import ntptime
from machine import Pin, RTC, I2C
import ssd1306
from config import *

# Inicialización de pantalla OLED
i2c = I2C(OLED_I2C_ID, scl=Pin(OLED_SCL_PIN), sda=Pin(OLED_SDA_PIN))
oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=OLED_ADDR)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            utime.sleep(1)
            timeout -= 1
        
        if not wlan.isconnected():
            raise ConnectionError("No se pudo conectar a WiFi")
        print("\nConectado a WiFi")
        print("IP:", wlan.ifconfig()[0])

def sync_ntp_time():
    try:
        print("Sincronizando hora NTP...")
        ntptime.settime()
        return True
    except Exception as e:
        raise RuntimeError(f"Error NTP: {e}")

def get_current_datetime():
    if not network.WLAN(network.STA_IF).isconnected():
        raise ConnectionError("No hay conexión WiFi")
    
    year, month, day, hour, minute, second, weekday, yearday = utime.localtime()
    return {
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'minute': minute,
        'second': second,
        'weekday': weekday
    }

def display_time_on_oled(time_data):
    oled.fill(0)
    
    # Formatear fecha y hora
    days = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
    months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
              "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    date_str = f"{time_data['day']:02d}/{months[time_data['month']-1]}/{time_data['year']}"
    time_str = f"{time_data['hour']:02d}:{time_data['minute']:02d}:{time_data['second']:02d}"
    day_str = days[time_data['weekday']]
    
    # Mostrar en OLED
    oled.text("Fecha:", 0, 0)
    oled.text(date_str, 0, 10)
    oled.text("Hora:", 0, 25)
    oled.text(time_str, 0, 35)
    oled.text(day_str, 90, 0)
    
    oled.show()