from urllib import request

url = 'https://priem.bmstu.ru/lists/upload/registered/registered-magister-Moscow.pdf'
name = "Списки подавших.pdf"
path = "tmp/" + name 

def update_file():
    request.urlretrieve(url, path)
    return path