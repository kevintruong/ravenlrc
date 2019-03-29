import json
import subprocess
import requests


def php(script_path, username,password):
    p = subprocess.Popen(['php', '-f', script_path, username,password], stdout=subprocess.PIPE)
    result = p.communicate()[0]
    return result


def gettoken():
    username = r'kevin.truong.ds@gmail.com'
    password = r'Oanhvu0505'
    payload = {'u': username, 'p': password}
    get_token = php('/mnt/Data/Project/Facebook-Api/gettoken.php', "{}".format(username),
                    "{}".format(password)).decode('utf-8')
    userinfo = json.loads(get_token)
    print(userinfo)
    token = userinfo['access_token']
    print(token)
    return token



token = gettoken()
print(token)

sine_time = input('Since: year-month-day: ')
until_time = input('Until: year-month-day: ')

payload = {'method': 'get', 'since': sine_time, 'until': until_time, 'access_token': token}
your_id = requests.get('https://graph.facebook.com/v2.10/me/feed', params=payload).json()

while True:
    try:
        for i in your_id['data']:
            payload = {
                'method': 'DELETE',
                'access_token': token
            }
            delete = requests.post('https://graph.facebook.com/v2.10/' + i["id"], params=payload).json()
            try:
                print
                delete['error']['message'], ' | ', i["id"], ' | ', i['created_time']

            except KeyError:
                print
                'deleted', ' | ', i["id"], ' | ', i['created_time']
        your_id = requests.get(your_id["paging"]["next"]).json()

    except KeyError:
        break
