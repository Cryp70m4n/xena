import codecs
import base64
import gzip
import requests

headers = {
    "Content-Type": "application/json"
}

login = {
    'user': 'root',
    'password': 'root'
}

res = requests.get("http://localhost:4334/", json=login)

json_data = {
    'session': res.text,
    'user': 'root',
}

response = requests.get('http://localhost:4334/api/read_shared', json=json_data)
print(response.text)


file = "test.png"
url = f"http://localhost:4334/api/download_shared?file={file}"

resp = requests.get(url, json=json_data)
print(resp.text)

data = gzip.decompress(base64.b64decode(resp.text))
with codecs.open(file, 'wb') as f:
    f.write(data)
