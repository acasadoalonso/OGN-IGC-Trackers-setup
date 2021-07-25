import httpx
import json
r = httpx.get('https://www.example.org/')
print(r)
print(r.status_code)
print(r.headers['content-type'])
print(r.text)
r = httpx.get('http://acasado.es:60082/download?j=2')
r.json()
j=json.loads(r.text)
d=j['devices']
print(r)
print(len(j), len(d))
