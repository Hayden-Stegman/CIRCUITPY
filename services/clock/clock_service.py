def get_clock_data(requests):
    # Specify the URL of the TIME endpoint you want to query
    url = "http://worldtimeapi.org/api/ip"

    try:
        # Send a GET request to the API endpoint
        print("Calling World Time API")
        response = requests.get(url)
        print(response.json())

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Extract the time
            try: 
                datetime_str = data.get('datetime', None)
                datetime_split = datetime_str.split('T')
                time_split = datetime_split[1]
                time_str = time_split[:5]

                # Split the time string into hours & minutes
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
                return formatted_time
            except Exception as e:
                print("F1: ", e, response.json())
                return "F1"
        else:
            # If the request was not successful, print the error message
            print("Error:", response.json())
            return None
    except Exception as e:
        print("F2: ", e)
        return "F2"
