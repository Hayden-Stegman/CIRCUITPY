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