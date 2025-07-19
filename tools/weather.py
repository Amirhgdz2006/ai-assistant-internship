import json

def get_current_weather(location:str , unit:str = 'celsius'):
    if 'tehran' in location.lower():
        return json.dumps({'location':'Tehran' , 'Temperature':33 , 'Unit':unit})
    elif 'esfahan' in location.lower():
        return json.dumps({'location':'Esfahan' , 'Temperature':31 , 'Unit':unit})
    elif 'mashhad' in location.lower():
        return json.dumps({'location':'Mashhad' , 'Temperature':32 , 'Unit':unit})
    else:
        return json.dumps({'location':'Mashhad' , 'Temperature':'unkknown' , 'Unit':unit})
    