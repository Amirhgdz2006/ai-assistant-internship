import requests
import json

option = input("which one you want to choose? GET OR POST :\nYou: ").lower()

if option == 'get' :

    url = "https://jsonplaceholder.typicode.com/posts/1"

    data = requests.get(url)

    print(json.dumps(data.json() , indent=4))

elif option == 'post':

    url = "https://jsonplaceholder.typicode.com/posts"

    json_data = {
        "userId" : int(input('Enter user ID (integer) : ')),
        "title" : str(input('Enter the title (string) : ')),
        "body" : str(input('Enter the body (string) : '))
    }

    data = requests.post(url , json=json_data)
    print(json.dumps(data.json() , indent=4))

else:
    print('Incorrect entry.')


