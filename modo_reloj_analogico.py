import utime
import math
from machine import RTC

def draw_clock(oled, hour, minute, second):
    center_x = 32
    center_y = 32
    radius = 30
    
    oled.fill(0)
    oled.text("Reloj Analogico", 0, 0)
    
    # Dibujar círculo
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x = center_x + int((radius-2) * math.sin(rad))
        y = center_y - int((radius-2) * math.cos(rad))
        oled.pixel(x, y, 1)
    
    # Manecilla de horas
    hour_angle = math.radians((hour % 12) * 30 - 90 + minute * 0.5)
    hour_len = radius * 0.5
    oled.line(center_x, center_y, 
              center_x + int(hour_len * math.cos(hour_angle)),
              center_y + int(hour_len * math.sin(hour_angle)), 1)
    
    # Manecilla de minutos
    minute_angle = math.radians(minute * 6 - 90)
    minute_len = radius * 0.8
    oled.line(center_x, center_y,
              center_x + int(minute_len * math.cos(minute_angle)),
              center_y + int(minute_len * math.sin(minute_angle)), 1)
    
    # Manecilla de segundos
    second_angle = math.radians(second * 6 - 90)
    second_len = radius * 0.9
    oled.line(center_x, center_y,
              center_x + int(second_len * math.cos(second_angle)),
              center_y + int(second_len * math.sin(second_angle)), 1)

def main(oled, get_direction, play_sound):
    rtc = RTC()
    last_update = 0
    
    while True:
        direction = get_direction()
        if direction == "double_click":
            play_sound(200, 100)
            play_sound(100, 100)
            return
        
        if utime.ticks_diff(utime.ticks_ms(), last_update) >= 1000:
            _, _, _, _, hour, minute, second, _ = rtc.datetime()
            draw_clock(oled, hour, minute, second)
            oled.show()
            last_update = utime.ticks_ms()
        
        utime.sleep_ms(50)