import requests

url = 'https://projetodashboardgestaodasaguasufsc.streamlit.app/'
response = requests.get(url)
print(f"Status code: {response.status_code}")
