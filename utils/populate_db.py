from requests import Session
import json

base_url = 'http://localhost:8080/1/'
token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ2Ql80R2RaVXVaYWFvd0xDa08zQVBSYnhDUkNXMDY3Y3p2NEgwQk1wNWxZIn0.eyJqdGkiOiJiOTg4MWM5Mi1lNTZjLTQxZWUtOGNmMy02YjJmZTkwZTJhZGEiLCJleHAiOjE1NjI5NTE3MTAsIm5iZiI6MCwiaWF0IjoxNTYyOTE1NzEwLCJpc3MiOiJodHRwczovL29hdXRoMi1mbGV4Y29vcC1rZXljbG9hay5va2QuZm9rdXMuZnJhdW5ob2Zlci5kZS9hdXRoL3JlYWxtcy9mbGV4Y29vcCIsImF1ZCI6ImJhY2tlbmQtbW9ja3VwIiwic3ViIjoiYTdhNWY3MGUtZTA1Yy00OWJiLThiNmQtOTkxYzQyOTc0NDkzIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYmFja2VuZC1tb2NrdXAiLCJhdXRoX3RpbWUiOjE1NjI5MTU3MTAsInNlc3Npb25fc3RhdGUiOiJmMDg5ZDkxMS0xMjk3LTQ3ZTUtOTA4My03MmE0YzJmZmQwZWQiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC8qIiwiaHR0cHM6Ly9mbGV4Y29vcC1iYWNrZW5kLW1vY2t1cC5va2QuZm9rdXMuZnJhdW5ob2Zlci5kZS8qIl0sInJlc291cmNlX2FjY2VzcyI6e30sInNjb3BlIjoib3BlbmlkIiwicm9sZSI6InByb3N1bWVyIn0.aICpHpG-XibcvRiSvhH_b1WbTpBqiRtb4GOiiPuqQWw-rMH-C9TBG2XrwQuveO36jUcLqki2vpsG4i1KxcSID4FurTnrlI_GjTlh35ZPrZj7RG-XJ5u576STiIFge3-FmcS0sRnPb4PxPum9d2sakTN2Tp9ZcCvLrRmBUnS6wBcixAenvdCwqX2lEO9fUiPEks02etRXjT0YDwEFeM-su9QM4wgLGGypZRFQuJNQyz-QbrvK6X0D2AzUGghp0Ncu0wXPO_F-QzL6-5IjRMCmYYmizYPYyvP7zW-edsRl6rt0yDMNWUim5blyaQ8-MypbF24iBZqoGbE4wWWvB6zXIg'
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






