DEBUG = True
def get_update_arrival_times(requests):
    latest_times_strings = []
    
    # Call the function to get MBTA data
    print("Calling MBTA API")
    mbta_data = get_mbta_data(requests)
    
    if(mbta_data is None):
        latest_times_strings.append("NO TIMES")
        return latest_times_strings
    
    # Extract arrival times from the MBTA data
    arrival_times = extract_arrival_times(mbta_data)

    # Print the extracted arrival times
    for arrival_time in arrival_times:
        if DEBUG:
            print("Arrival Time:", arrival_time)
        time_str = arrival_time[11:16]
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
        latest_times_strings.append(formatted_time)
    
    return latest_times_strings[:4]

def get_mbta_data(requests):
    # Specify the URL of the MBTA API endpoint you want to query
    url = "https://api-v3.mbta.com/predictions?filter%5Bstop%5D=70088"

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        return data
    else:
        # If the request was not successful, print the error message
        print("Error:", response.status_code)
        return None

def extract_arrival_times(mbta_data):
    # Check if the data is not None
    if mbta_data is not None:
        # Extract the list of predictions
        predictions = mbta_data.get('data', [])
        
        # Iterate over each prediction and extract the arrival_time
        arrival_times = []
        for prediction in predictions:
            attributes = prediction.get('attributes', {})
            arrival_time = attributes.get('arrival_time')
            if arrival_time:
                arrival_times.append(arrival_time)
        
        return arrival_times
    else:
        return []