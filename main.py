# Made by JatoMixo.
#
# Twitter: @JatoMixo_Gamer
# Web: jatomixo.com

from datetime import datetime
import requests as req
import json
import gpiozero as gpio

DOWNLOAD_TIME = [0, 1, 0]
FILE_DATA_PATH = "data.json"
CHEAPEST_HOURS_QUANTITY = 3
RELAY = gpio.OutputDevice(17, active_high=False, initial_value=True)
API_URL = ("https://apidatos.ree.es/es/datos/mercados/"
           "precios-mercados-tiempo-real?"
           "start_date=DATET00:00&"
           "end_date=DATET23:59&"
           "time_trunc=hour")


def get_current_time():
    hour = str(datetime.now().strftime("%H"))
    minute = str(datetime.now().strftime("%M"))
    second = str(datetime.now().strftime("%S"))

    return [int(hour), int(minute), int(second)]


def get_api_url_for_today():
    current_date = str(datetime.today())[0:10]
    return API_URL.replace("DATE", current_date)


def get_hour_value_map():
    api_url = get_api_url_for_today()

    full_data = req.get(api_url, allow_redirects=False).json()
    hour_price_data = full_data["included"][0]["attributes"]["values"]

    hour_value_map = {}

    for hour_value in hour_price_data:
        value = hour_value["value"]
        hour = int(hour_value["datetime"][11] + hour_value["datetime"][12])

        hour_value_map[hour] = value

    return hour_value_map


def create_data_file():
    data = get_hour_value_map()

    with open(FILE_DATA_PATH, "w") as file:
        json.dump(data, file, indent=4)


def get_cheap_hours():
    hours_data = get_hour_value_map()
    cheap_hours = []

    cheapest_values = sorted(hours_data.values())[0:CHEAPEST_HOURS_QUANTITY]

    for hour, value in hours_data.items():
        if value in cheapest_values:
            cheap_hours.append(hour)

    return cheap_hours


def turn_on_relay():
    RELAY.off()


def turn_off_relay():
    RELAY.on()


create_data_file()
cheap_hours = get_cheap_hours()


def main():

    global cheap_hours

    if get_current_time() == DOWNLOAD_TIME:
        create_data_file()
        cheap_hours = get_cheap_hours()

    if get_current_time()[0] in cheap_hours:
        turn_on_relay()
    else:
        turn_off_relay()


if __name__ == "__main__":
    while True:
        main()
