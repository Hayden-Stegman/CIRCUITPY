# type: ignore
import time
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrix import Matrix
from services.MBTA import mbta_service
from services.clock import clock_service
from services import wifi_connection
from adafruit_display_shapes.rect import Rect
from os import getenv

print("-" * 40)
print("START")

TIME_DELAY = 60
DEBUG = True

# Initalize Display Array
text_list = ["LOADING"]

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

# Set the Anchor for the label to half way across, and at the top
multi_offset = 5
clock_label.anchor_point = (0.5, 0.5)  # Set anchor point to the center of the label
clock_label.anchored_position = (display.width // 2, (display.height // 2) + multi_offset)

train_label.anchor_point = (0.5, 0.5)
train_label.anchored_position = (display.width // 2, (display.height // 2) - multi_offset)

def update_clock_text(display_text=""):
    clock_label.text = display_text
def update_train_text(display_text=""):
    train_label.text = display_text    
# Initial Setup Set Setting
update_clock_text(text_list[0])

# Add the label to the root group
group_root.append(clock_label)
group_root.append(train_label)

# Get Wifi
requests = wifi_connection.configure_wifi()

last_time_check = None

print("\nEND SETUP")
print("-" * 40)
print("\nSTARTING TIME LOOP")

while True:
    current_time = time.monotonic()
    # --- DISPLAY UPDATING ---
    if last_time_check is None or current_time > last_time_check + TIME_DELAY:
        clock_data = clock_service.get_clock_data(requests)
        update_clock_text(clock_data)
        last_time_check = current_time
    time.sleep(1)