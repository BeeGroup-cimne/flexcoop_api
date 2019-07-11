from requests import Session
import json

base_url = 'http://localhost:8080/1/'
token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ2Ql80R2RaVXVaYWFvd0xDa08zQVBSYnhDUkNXMDY3Y3p2NEgwQk1wNWxZIn0.eyJqdGkiOiIyMGVkNTRlNi1hNzBlLTQ2ZTQtOGY2NS0zOTlmYjUyOTNmZTgiLCJleHAiOjE1NjI4OTE3MzEsIm5iZiI6MCwiaWF0IjoxNTYyODU1NzMxLCJpc3MiOiJodHRwczovL29hdXRoMi1mbGV4Y29vcC1rZXljbG9hay5va2QuZm9rdXMuZnJhdW5ob2Zlci5kZS9hdXRoL3JlYWxtcy9mbGV4Y29vcCIsImF1ZCI6ImJhY2tlbmQtbW9ja3VwIiwic3ViIjoiYTdhNWY3MGUtZTA1Yy00OWJiLThiNmQtOTkxYzQyOTc0NDkzIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYmFja2VuZC1tb2NrdXAiLCJhdXRoX3RpbWUiOjE1NjI4NTU3MzEsInNlc3Npb25fc3RhdGUiOiJhNzU0ZjY4Ny04OTBlLTQ3NzgtODc1MS05ZmE2MGQxNTRiMWMiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC8qIiwiaHR0cHM6Ly9mbGV4Y29vcC1iYWNrZW5kLW1vY2t1cC5va2QuZm9rdXMuZnJhdW5ob2Zlci5kZS8qIl0sInJlc291cmNlX2FjY2VzcyI6e30sInNjb3BlIjoib3BlbmlkIiwicm9sZSI6InByb3N1bWVyIn0.X2v_QMGu-gEb80UKGC7QJZiTsmOI2hLpi8mBk5_hkoDTkVFaOKgI3VDKHmhU4eo6Kcc4iAKp_QYz5xI5pzq8rewzmlml5rqcXUU0UukT9jW8iLX54PWKUCrU1Gc0IBAmL4rzRms7ji-xDDwHeJgyGxLWz_lavS7UKxxbjCOKuJMFXlk-y--tG_ujtck0VbKmeUtVnVP4h6aY3GWXN4MLRs2kJ2mnr1K2LnrOGYBfcXU7X0ifOmUtvGEF2VAgWN2AtHsRUe8llQ4FPwqLxj2qdgTRb6EpFlB1WPBTuMJOIWRMSw4COL3EtQmWz3nVPO3KNeqOz03YF3ufeYGyBTVZoQ'
headers = {'accept': 'application/xml', 'Authorization': token, "Content-Type": "application/json"}
delete_first = True

session = Session()
session.headers = headers

with open("test_data.json") as json_file:
    # print(json_file)
    json_data = json.load(json_file)
    # print(json_data)

for domain in json_data:
    for item in json_data[domain]:
        # print(item)
        if delete_first:
            session.delete(base_url + domain)
        r = session.post(base_url + domain, data=json.dumps(item))
        # print(session.headers)
        print("HTTP status code: " + str(r.status_code) + " while connecting to " + base_url + domain)
        print(json.dumps(item))
        # print(r.content)






