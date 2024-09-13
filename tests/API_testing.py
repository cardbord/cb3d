import requests
import pathlib
from _catchers import Test

@Test()
def create_account():
    json = {
        'username':'bill',
        'password':'smith'
    }
    r = requests.post("http://127.0.0.1:8000/register/",json=json)

@Test()
def login():
    json = {
        'username':'bill',
        'password':'smith'
    }
    r = requests.post("http://127.0.0.1:8000/login/",data=json,headers={'content-type':'application/x-www-form-urlencoded'})
    print(r.status_code)
    print(r.json())
    
    


@Test()
def get(): #grabbing all models from the database
    r = requests.get("http://127.0.0.1:8000/models/")
    print(r.json())

@Test()
def upload_castle_demo(): #uploading CASTLE.CBmodel to the API, for storage in the database
    path = pathlib.Path(__file__).parent.parent
    with open(f'{path}/examples/CASTLE.CBmodel','r') as model:
        model_info = model.readlines()
        model_points = eval((model_info[0]).replace('\n',''))
        model_connections = eval((model_info[1]).replace('\n',''))
        
        model.close()

    json = {"pointmap":model_points,"connected_points":model_connections}
    r = requests.patch("http://127.0.0.1:8000/upload/",json=json)
    print(r)
    print(r.json())

#just reference these somewhere, to test if they work fine