def get_clock_data(requests):
    # Specify the URL of the TIME endpoint you want to query
    url = "http://worldtimeapi.org/api/ip"

    try:
        # Send a GET request to the API endpoint
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            print("API Response:", data)
            # Extract the time
            datetime_str = data.get('datetime', None)
            datetime_split = datetime_str.split('T')
            time_split = datetime_split[1]
            time_str = time_split[:5]
            
            print("JUST HOUR: ", int(time_str[:2]))

            if int(time_str[:2]) > 12:
                updated_hour = int(time_str[:2]) - 12
                hour_min_split = time_str.split(':')
                corrected_time_str = str(updated_hour) + ":" + hour_min_split[1]
                return corrected_time_str
            return time_str
        else:
            # If the request was not successful, print the error message
            print("Error:", response.status_code)
            return None
    except Exception as e:
        print("Failed to get Time:", e)
