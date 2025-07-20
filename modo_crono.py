import utime

def main(oled, get_direction, play_sound):
    running = False
    start_time = 0
    elapsed = 0
    
    while True:
        direction = get_direction()
        
        if direction == "center":
            running = not running
            if running:
                start_time = utime.ticks_ms() - elapsed
                play_sound(440, 50)
            else:
                play_sound(220, 50)
        elif direction == "double_click":
            play_sound(200, 100)
            play_sound(100, 100)
            return
        
        if running:
            elapsed = utime.ticks_diff(utime.ticks_ms(), start_time)
        
        # Convertir milisegundos a formato hh:mm:ss.ms
        ms = elapsed % 1000
        seconds = (elapsed // 1000) % 60
        minutes = (elapsed // 60000) % 60
        hours = elapsed // 3600000
        
        time_str = "{:02d}:{:02d}:{:02d}.{:03d}".format(hours, minutes, seconds, ms)
        
        oled.fill(0)
        oled.text("Cronometro", 0, 0)
        oled.text(time_str, 0, 20)
        oled.text("[OK] Start/Stop", 0, 50)
        oled.show()
        
        utime.sleep_ms(50)