import utime
from machine import RTC

def main(oled, get_direction, play_sound):
    rtc = RTC()
    months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
              "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    days_week = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
    
    while True:
        direction = get_direction()
        if direction == "double_click":
            play_sound(200, 100)
            play_sound(100, 100)
            return
        
        year, month, day, weekday, _, _, _, _ = rtc.datetime()
        
        oled.fill(0)
        oled.text("Calendario", 0, 0)
        oled.text("{:02d} {} {:04d}".format(day, months[month-1], year), 0, 20)
        oled.text(days_week[weekday], 0, 40)
        
        # Mostrar semana actual (simplificado)
        oled.text("Sem: {:02d}".format((day // 7) + 1), 70, 40)
        
        oled.show()
        utime.sleep_ms(500)