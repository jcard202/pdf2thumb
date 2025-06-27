import requests

files = {'file': open('chapter1.pdf', 'rb')}
data = {'sizes': '800,400,200'}
response = requests.post('http://localhost:5000/thumbnail', files=files, data=data)

with open('thumbnails.zip', 'wb') as f:
    f.write(response.content)

