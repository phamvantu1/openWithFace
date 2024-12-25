import requests

# IP address of the ESP8266 device
esp_ip = "http://192.168.83.130"  # Change this to your ESP8266's IP address

# Send a GET request to the ESP8266
try:
    response = requests.get(esp_ip)

    # Check the status of the response
    if response.status_code == 200:
        print("Request was successful!")
        print("Response content:", response.text)
    else:
        print("Request failed with status code:", response.status_code)

except requests.exceptions.RequestException as e:
    print(f"Error during the request: {e}")
