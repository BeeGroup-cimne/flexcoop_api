from requests import Session
import json

base_url = 'http://localhost:8080/1/'
token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ2Ql80R2RaVXVaYWFvd0xDa08zQVBSYnhDUkNXMDY3Y3p2NEgwQk1wNWxZIn0.eyJqdGkiOiJmZTg5YzQwNS0wYmFlLTQ2NDQtYWJjMS0yMjI2NDFjNzIwY2QiLCJleHAiOjE1NjMyMzAyNzEsIm5iZiI6MCwiaWF0IjoxNTYzMTk0MjcxLCJpc3MiOiJodHRwczovL29hdXRoMi1mbGV4Y29vcC1rZXljbG9hay5va2QuZm9rdXMuZnJhdW5ob2Zlci5kZS9hdXRoL3JlYWxtcy9mbGV4Y29vcCIsImF1ZCI6ImJhY2tlbmQtbW9ja3VwIiwic3ViIjoiYTdhNWY3MGUtZTA1Yy00OWJiLThiNmQtOTkxYzQyOTc0NDkzIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYmFja2VuZC1tb2NrdXAiLCJhdXRoX3RpbWUiOjE1NjMxOTQyNzEsInNlc3Npb25fc3RhdGUiOiJhNjVlNDVlNC0wZmE1LTQ3MWQtYTBiMi04NzM2MzU3NzUwZTkiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC8qIiwiaHR0cHM6Ly9mbGV4Y29vcC1iYWNrZW5kLW1vY2t1cC5va2QuZm9rdXMuZnJhdW5ob2Zlci5kZS8qIl0sInJlc291cmNlX2FjY2VzcyI6e30sInNjb3BlIjoib3BlbmlkIiwicm9sZSI6InByb3N1bWVyIn0.UNc08vOUHWdVT_23XOeQaTMvgRCoPVF8wqdEVz0gMtLLRgBlwevWSdtUIqu8HzbngX7MRHEXhVBZddmikClPyUm-ySLMPXcU_KtOpzJH9jDY8wGGid9n24mayhRPWBaopUsp4fiWePfU0ocEkOvIrVw1d1lXvLwhvE1lu17R_r0BTpv35b6yW_ZjxZWeqx5XLEJw0zXzPl4vscn28og0-A2_fJr51vBXiIQGe0kbB34S1CGsNyemNuklhmO9cU_A15XqFwTT0og8onHVGcM1_BbKM4plNnalLL-wGuNw8C_UH-NBWnjv2XBEu-dQ_vOBhJpTVarP_26iPOtuwgPcTA'
headers = {'accept': 'application/xml', 'Authorization': token, "Content-Type": "application/json"}
delete_first = True

session = Session()
session.headers = headers

with open("test_data.json") as json_file:
    # print(json_file)
    json_data = json.load(json_file)
    # print(json_data)


for domain in json_data:
    if delete_first:
        session.delete(base_url + domain)

    for item in json_data[domain]:
        # print(item)
        r = session.post(base_url + domain, data=json.dumps(item))
        # print(session.headers)
        print("HTTP status code: " + str(r.status_code) + " while connecting to " + base_url + domain)
        if r.status_code == 201:
            print(json.dumps(item))
        else:
            print(r.text)
        print('=================================================')
        # print(r.content)






