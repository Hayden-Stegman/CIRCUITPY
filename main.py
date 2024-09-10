# type: ignore
import time
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrix import Matrix
from services.mbta import mbta_service
from services.clock import clock_service
from services import wifi_connection
from adafruit_display_shapes.rect import Rect
from os import getenv

print("-" * 40)
print("START")
print("LOCAL TIME ", time.localtime())

# Initalize Display Arrays
text_list = ["LOADING"]
diff_list = [""]
clock_data = ""

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

clock_label = Label(font, text=text_list[0], color=color[2])
train_label = Label(font, text="MBTA TIMES", color=color[1])
difference_label = Label(font, text="-", color=color[2])

# Set the Anchor for the label to half way across, and at the top
multi_offset = 8
clock_label.anchor_point = (0.5, 0.5)  # Set anchor point to the center of the label
clock_label.anchored_position = (display.width // 2, (display.height // 2) - multi_offset)
train_label.anchor_point = (0.5, 0.5)
train_label.anchored_position = (display.width // 2, (display.height // 2))
difference_label.anchor_point = (0.5, 0.5)
difference_label.anchored_position = (display.width // 2, (display.height // 2) + multi_offset)

def update_clock_text(display_text=""):
    clock_label.text = display_text
def update_train_text(display_text=""):
    train_label.text = display_text    
def update_diff_text(display_text=""):
    difference_label.text = display_text + " MIN"

# Add the label to the root group
group_root.append(clock_label)
group_root.append(train_label)
group_root.append(difference_label)

def time_to_minutes(time_str):
    # Convert a time string 'HH:MM' to the number of minutes past midnight.
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def time_difference(time1, time2):
    # Calculate the absolute difference in minutes between two times 'HH:MM'.
    minutes1 = time_to_minutes(time1)
    minutes2 = time_to_minutes(time2)
    
    # Calculate the difference considering crossing midnight
    difference = abs(minutes1 - minutes2)
    # Handle wrapping around midnight
    if difference > 720:  # More than 12 hours
        difference = 1440 - difference  # 1440 minutes in a day
    
    return difference

def update_diff_data():
    # Make Sure the clock is valid
    if(clock_data[0] == "F"):
        return
    else:
        # Delete the current differences list
        while len(diff_list) > 0:
            diff_list.pop()

        print("\n--- DIFF CALC ---")
        for index, text in enumerate(text_list):
            # The first item in text_list is not a time -- 
            if index == 0:
                diff_list.append("-")
            # Add the differences in times
            else:
                print("Index: ", index)
                print("Clock Data: ", clock_data[:5])
                print("Text_List: ", text_list[index][:5])
                diff = time_difference(clock_data[:5], text_list[index][:5])
                print("Diff: ", diff)
                diff_list.append(diff)

# Get Wifi
requests = wifi_connection.configure_wifi()

print("\nEND SETUP")
print("-" * 40)
print("STARTING TIME LOOP")

# Update Speed Controls
# How often to call the World Time API and update the time... Once a minute
CLOCK_TIME_DELAY = 60
clock_time_check = None
# How often to show the next upcomming train time. UI Switch.
UI_TIME_DELAY = 2
ui_time_check = None
# How often to get new MBTA API Data to display
MBTA_TIME_DELAY = 60
mbta_time_check = None
# Utils
DEBUG = True
CLOCK_ENABLED = True
current_text = 0

text_list[0] = "RED LINE"
while True:
    current_time = time.monotonic()
    # --- CLOCK LOOPER ---
    if (clock_time_check is None or current_time > clock_time_check + CLOCK_TIME_DELAY) and CLOCK_ENABLED:
        if DEBUG:
            print("\n" + ('-' * 10) + " EVENT " + ('-' * 10))
            print("UPDATING TIME")
        clock_data = clock_service.get_clock_data(requests)
        update_clock_text(clock_data)
        update_diff_data()
        clock_time_check = current_time

    # --- UI Swapper ---
    if ui_time_check is None or current_time > ui_time_check + UI_TIME_DELAY:
        if DEBUG:
            print("\n--- UPDATING SCREEN ---")
            print("Size: " + str(len(text_list)))
            print("Current Text: " + str(current_text))
            print("Clock: ", clock_data)
            print("\nText_List: ")
            for index, text in enumerate(text_list):
                print("[" + str(index) + "]: " + str(text))
            print("\nDiff_List: ")
            for index, text in enumerate(diff_list):
                print("[" + str(index) + "]: " + str(text))
        update_train_text(text_list[current_text])
        update_diff_text(str(diff_list[current_text]))
        if current_text == len(text_list) - 1:
            current_text = 0
        else:
            current_text += 1
        ui_time_check = current_time
    
    # --- NEW MBTA DATA ---
    if mbta_time_check is None or current_time > mbta_time_check + MBTA_TIME_DELAY:
        if DEBUG:
            print("\n" + ('-' * 10) + " EVENT " + ('-' * 10))
            print("UPDATING MBTA TIMES")
        while len(text_list) > 1:
            text_list.pop()
        text_list.extend(mbta_service.get_update_arrival_times(requests))
        update_diff_data()
        mbta_time_check = current_time
    
    # SLOW DOWN -- No updates are quicker than a second anyways
    time.sleep(1)