import base64
import json
import requests

 

	


def get_auth_token(username, password):
    url = "https://home.parsing.eu/api/Service.svc/BasicLogin"
    credentials = f"{username}:{password}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {base64_credentials}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text.strip()  # Токенът е в plain text
    else:
        raise Exception(f"Failed to get auth token: {response.status_code} {response.text}")

def send_reservation(token):
    url = "https://home.parsing.eu/api/Service.svc/NewResv"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    reservation_data = {
        "HotelGroup": "",
        "Hotel": "DIT MAJESTIC BEACH RESORT|5",
        "RoomType": "DBL (DOUBLE ROOM)",
        "RoomCategory": "SEA (SEA VIEW)",
        "CheckIn": "01.11.2020",
        "CheckOut": "08.11.2020",
        "Booked": "19.09.2020",
        "Voucher": "123456789",
        "Board": "HB",
        "Market": "",
        "Remark": "",
        "Status": "",
        "Adults": "2",
        "Children": "0",
        "Comments": "test",
        "Country": "BE",
        "Email": "",
        "Flight_Arr": "",
        "Flight_Arr_Time": "",
        "Flight_Dep": "",
        "Flight_Dep_Time": "",
        "Names": [
            {"name": "test1", "isChild": "Adult", "age": "", "birthDate": ""},
            {"name": "test2", "isChild": "Adult", "age": "", "birthDate": ""}
        ]
    }
    
    response = requests.post(url, headers=headers, json=reservation_data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to send reservation: {response.status_code} {response.text}")

if __name__ == "__main__":
    USERNAME = "your_username"
    PASSWORD = "your_password"
    
    try:
        token = get_auth_token(USERNAME, PASSWORD)
        print(f"Auth token retrieved: {token}")
        
        response = send_reservation(token)
        print("Reservation response:", response)
    except Exception as e:
        print("Error:", e)
