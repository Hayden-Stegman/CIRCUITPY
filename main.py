# type: ignore
import time
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrix import Matrix
from services.MBTA import mbta_service
from services import wifi_connection
from adafruit_display_shapes.rect import Rect

print("-" * 40)
print("START")

TIME_DELAY = 2
MBTA_TIME_DELAY = 30
DEBUG = True

# Initalize Display Array
text_list = ["LOADING..."]

# --- Display Setup
matrix = Matrix()
display = matrix.display

# Root Group
group_root = displayio.Group()

# Grid One
bitmap = displayio.Bitmap(64, 32, 2)
color = displayio.Palette(3)
color[0] = 0x000000 # black background
color[1] = 0xff0000 # red
color[2] = 0xffffff # white
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)

# Configure Root Layout
group_root.append(tile_grid)
display.root_group = group_root

# Display Font Setup
font = terminalio.FONT

main_label = Label(font, text=text_list[0], color=color[2])

# Set the Anchor for the label to half way across, and at the top
main_label.anchor_point = (0.5, 0.5)  # Set anchor point to the center of the label
main_label.anchored_position = (display.width // 2, display.height // 2)  

def update_text(display_text=""):
    # Set the Text
    main_label.text = display_text
update_text(text_list[0])

# Add the label to the root group
group_root.append(main_label)

# Get Wifi
requests = wifi_connection.configure_wifi()

def get_update_arrival_times():
    lastest_strings = []
    
    # Call the function to get MBTA data
    mbta_data = mbta_service.get_mbta_data(requests)
    
    if(mbta_data is None):
        lastest_strings.append("NO TIMES")
        return lastest_strings
    
    # Extract arrival times from the MBTA data
    arrival_times = mbta_service.extract_arrival_times(mbta_data)
    
    times_size = len(arrival_times)
    time_size_str = str(times_size) + " COMING"
    lastest_strings.append(time_size_str)

    # Print the extracted arrival times
    for arrival_time in arrival_times:
        if DEBUG:
            print("Arrival Time:", arrival_time)
        time_str = arrival_time[11:16]
        # Split the time string into hours, minutes, seconds
        hours, minutes = map(int, time_str.split(':'))
        # Convert 24-hour time to 12-hour format
        period = "AM"
        if hours >= 12:
            period = "PM"
            if hours > 12:
                hours -= 12
        elif hours == 0:
            hours = 12
        # Format the time in 12-hour format
        formatted_time = f"{hours:02}:{minutes:02} {period}"
        lastest_strings.append(formatted_time)
    
    return lastest_strings

last_display_check = None
last_mbta_check = None
current_text = 0

print("\nEND")
print("-" * 40)
print("\n--- STARTING TIME LOOP ---")

text_list[0] = "RED LINE"

while True:
    current_time = time.monotonic()
    
    # --- DISPLAY UPDATING ---
    if last_display_check is None or current_time > last_display_check + TIME_DELAY:
        if DEBUG:
            print("\n--- UPDATING SCREEN ---")
            print("Size: " + str(len(text_list)))
            print("Current Text: " + str(current_text))
            print("\nText_List: ")
            for index, text in enumerate(text_list):
                print("[" + str(index) + "]: " + str(text))
        update_text(text_list[current_text])
        if current_text == len(text_list) - 1:
            current_text = 0
        else:
            current_text += 1
        last_display_check = current_time

    # --- MBTA TIMES UPDATING ---
    if last_mbta_check is None or current_time > last_mbta_check + MBTA_TIME_DELAY:
        if DEBUG:
            print("\n" + ('-' * 10) + " EVENT " + ('-' * 10))
            print("UPDATING MBTA TIMES")

        while len(text_list) > 1:
            text_list.pop()
        text_list.extend(get_update_arrival_times())
        last_mbta_check = current_time

    time.sleep(1)