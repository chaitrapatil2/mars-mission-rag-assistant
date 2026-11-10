import requests

r = requests.post("http://127.0.0.1:5000/ask",
                  json={"question": "What are the main radiation risks for astronauts?"})
print(r.status_code)
print(r.json())