import requests

url = "http://127.0.0.1:5000/api/video"
with open(r"C:\Users\itzkh\Downloads\3.mp4", "rb") as f:
    response = requests.post(url, files={"file": f})
    print(response.json())