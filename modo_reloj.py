import utime
from machine import RTC # Keep RTC as it's specific to the clock's function and not a shared peripheral in the same way OLED/Joystick are

# The following imports related to hardware initialization and configuration
# are removed from modo_reloj.py to prevent interference.
# It is assumed that 'oled', 'get_direction', and 'play_sound'
# are passed as arguments from a central script (e.g., main.py)
# that handles global hardware initialization based on config.py.
#
# from machine import Pin, I2C, PWM, ADC
# import framebuf
# import ssd1306
# (No more direct use of config.py constants within this module)

# --- Main clock mode function ---
# This function now expects initialized hardware objects and functions
# to be passed to it, ensuring it doesn't interfere with other modules
# that might also use these peripherals.
def main(oled, get_direction_func, play_sound_func):
    rtc = RTC()
    last_display_update = 0
    edit_mode = False
    
    # Store initial time, which can be modified in edit mode
    current_time_tuple = rtc.datetime()
    edit_year, edit_month, edit_day, edit_weekday, edit_hour, edit_minute, edit_second, edit_yearday = current_time_tuple

    # Variables to track which part of the time is being edited
    # 0: Hour, 1: Minute
    edit_field = 0 # Start editing hour

    # For visual blinking of the edited field
    blink_state = True
    last_blink_toggle = utime.ticks_ms()
    blink_interval_ms = 300 # How often the edited field blinks

    while True:
        direction = get_direction_func() # Use the passed-in get_direction_func
        
        # --- Handle Joystick Input ---
        if direction == "double_click":
            if edit_mode:
                # Exit edit mode, save changes to RTC
                rtc.datetime((edit_year, edit_month, edit_day, edit_weekday, 
                              edit_hour, edit_minute, edit_second, edit_yearday))
                play_sound_func(600, 100) # Confirmation sound via passed-in function
                edit_mode = False
                edit_field = 0 # Reset edited field
            else:
                # Exit modo_reloj completely and return to main menu
                play_sound_func(200, 100) # Use passed-in play_sound_func
                play_sound_func(100, 100) # Use passed-in play_sound_func
                return # This exits the main loop and returns to the calling module (e.g., main.py)
        elif direction == "center":
            play_sound_func(500, 50) # Use passed-in play_sound_func
            edit_mode = not edit_mode # Toggle edit mode
            if edit_mode:
                edit_field = 0 # Start editing hour
            else:
                edit_field = 0 # Reset field on exit from edit mode
        elif edit_mode:
            # In edit mode, joystick adjusts time
            if direction == "up":
                if edit_field == 0: # Editing hour
                    edit_hour = (edit_hour + 1) % 24
                elif edit_field == 1: # Editing minute
                    edit_minute = (edit_minute + 1) % 60
                play_sound_func(400, 30) # Use passed-in play_sound_func
            elif direction == "down":
                if edit_field == 0: # Editing hour
                    edit_hour = (edit_hour - 1) % 24
                elif edit_field == 1: # Editing minute
                    edit_minute = (edit_minute - 1) % 60
                play_sound_func(400, 30) # Use passed-in play_sound_func
            elif direction == "right":
                # Move to next field to edit
                edit_field = (edit_field + 1) % 2 # Cycle between hour (0) and minute (1)
                play_sound_func(350, 30) # Use passed-in play_sound_func
            elif direction == "left":
                # Move to previous field to edit
                edit_field = (edit_field - 1) % 2 # Cycle between hour (0) and minute (1)
                play_sound_func(350, 30) # Use passed-in play_sound_func
            
            # Small delay after joystick input in edit mode for better control
            utime.sleep_ms(150)
        
        # --- Update Time and Display ---
        current_ms = utime.ticks_ms()

        # Toggle blink state for edited field
        if edit_mode and utime.ticks_diff(current_ms, last_blink_toggle) >= blink_interval_ms:
            blink_state = not blink_state
            last_blink_toggle = current_ms

        # Update display in normal mode or when editing
        # Update more frequently in edit mode for responsive blinking/changes
        if not edit_mode or utime.ticks_diff(current_ms, last_display_update) >= 100: 
            oled.fill(0) # Always clear the display to black

            # Display mode title
            oled.text("RELOJ DIGITAL", 25, 5, 1) # Centered title, white color

            # Get current time for display (use RTC in normal mode, edited vars in edit mode)
            if not edit_mode:
                current_time_tuple = rtc.datetime()
                # Ensure edit variables stay in sync even when not editing, for smooth transition
                edit_year, edit_month, edit_day, edit_weekday, edit_hour, edit_minute, edit_second, edit_yearday = current_time_tuple

            # Format time and date strings
            time_str_hour = "{:02d}".format(edit_hour)
            time_str_minute = "{:02d}".format(edit_minute)
            time_str_second = "{:02d}".format(edit_second)
            
            # Use 'time_str_second' from rtc.datetime() even in edit mode, as it's not edited
            real_second = rtc.datetime()[6]

            # Display time with larger font simulation (drawing multiple times)
            # Position for the "large" time display
            time_display_y = 25
            
            # Draw Hour
            if edit_mode and edit_field == 0 and not blink_state:
                # Blink effect: hide hour part by not drawing
                pass
            else:
                oled.text(time_str_hour, 20, time_display_y, 1)
                oled.text(time_str_hour, 21, time_display_y, 1) # Simulate bold/larger
                oled.text(time_str_hour, 20, time_display_y + 1, 1)

            oled.text(":", 45, time_display_y, 1) # Separator

            # Draw Minute
            if edit_mode and edit_field == 1 and not blink_state:
                # Blink effect: hide minute part by not drawing
                pass
            else:
                oled.text(time_str_minute, 55, time_display_y, 1)
                oled.text(time_str_minute, 56, time_display_y, 1) # Simulate bold/larger
                oled.text(time_str_minute, 55, time_display_y + 1, 1)
            
            oled.text(":", 80, time_display_y, 1) # Separator

            # Draw Second (always from RTC, not editable directly)
            oled.text("{:02d}".format(real_second), 90, time_display_y, 1)
            oled.text("{:02d}".format(real_second), 91, time_display_y, 1)
            oled.text("{:02d}".format(real_second), 90, time_display_y + 1, 1)


            # Display Date
            date_str = "{:02d}/{:02d}/{:04d}".format(edit_day, edit_month, edit_year)
            oled.text(date_str, 20, 50, 1)

            # Indicate EDIT MODE
            if edit_mode:
                oled.text("EDIT MODE", 0, 0, 1)
            
            oled.show()
            last_display_update = current_ms
        
        # Small delay to prevent busy-waiting
        if not edit_mode:
            utime.sleep_ms(50) # Standard delay for non-editing
        else:
            utime.sleep_ms(10) # Shorter delay in edit mode for responsiveness