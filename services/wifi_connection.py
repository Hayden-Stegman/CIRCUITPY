from os import getenv
import board
import busio
from digitalio import DigitalInOut
import adafruit_connection_manager
import adafruit_requests
from adafruit_esp32spi import adafruit_esp32spi

def configure_wifi():
    print("\n--- Wifi Connection ---")
    #load wifi details from the secrets into dictionary
    secrets = {
        "ssid": getenv("HOME_WIFI_SSID"),
        "password": getenv("HOME_WIFI_PASSWORD"),
    }

    if secrets == {"ssid": None, "password": None}:
        print("Wifi Secrets Not Set - Please Configure in settings.toml")
        return

    # Board with pre-defined ESP32 Pins:
    esp32_cs = DigitalInOut(board.ESP_CS)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)

    # Secondary (SCK1) SPI used to connect to WiFi board on Arduino Nano Connect RP2040
    if "SCK1" in dir(board):
        spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
    else:
        spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

    pool = adafruit_connection_manager.get_radio_socketpool(esp)
    ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
    requests = adafruit_requests.Session(pool, ssl_context)

    if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
        print("ESP32 found and in idle mode")
    print("Firmware vers.", esp.firmware_version.decode("utf-8"))
    print("MAC addr:", ":".join("%02X" % byte for byte in esp.MAC_address))

    for ap in esp.scan_networks():
        print("\t%-23s RSSI: %d" % (str(ap["ssid"], "utf-8"), ap["rssi"]))

    print("Connecting to AP...")
    while not esp.is_connected:
        try:
            esp.connect_AP(secrets["ssid"], secrets["password"])
        except OSError as e:
            print("could not connect to AP, retrying: ", e)
            continue
    
    return requests