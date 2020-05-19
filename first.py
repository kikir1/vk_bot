import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import requests
from base64 import b64encode
import os
import telegram
from bs4 import BeautifulSoup

access_token = ""
version = 5.103
myDomain = ""
sosDomain = []
myId = -194708925
sosId = [-146937630, -112665283, -124497715]
oauth = ''


def rash(url):

    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    class_ = 'style'

    i = 250
    head = []
    while i != 0:
        try:
            head = soup.find('div', class_=class_ + str(i))
            if len(head) != 0:
                break
            else:
                i -= 25
        except BaseException:
            i -= 25

    url = head.find_all(class_='dashiconsUrl')
    urldp = str(url[0]).split('>')[1].split('?')[0]

    return urldp


def deeplink(url):
    url = rash(url)

    client_id = ""
    client_secret = ""
    data = (client_id + ':' + client_secret).encode()
    data_b64_encoded = b64encode(data)

    urlt = 'https://api.admitad.com/token/?grant_type=client_credentials&client_id=' + client_id + '&scope=statistics websites public_data deeplink_generator advcampaigns advcampaigns_for_website'
    headers = {'Authorization': 'Basic '.encode() + data_b64_encoded}

    authInfo = requests.post(urlt, headers=headers)

    accessToken = json.loads(authInfo.text)['access_token']

    headers = {'Authorization': 'Bearer ' + accessToken}
    w_id = 1421258

    c_id = 22586

    urlt = 'https://api.admitad.com/deeplink/' + str(w_id) + '/advcampaign/' + str(c_id) + '/?ulp=' + str(url)
    res = requests.get(urlt, headers=headers).text

    return res[2:-2]


def download_photo(url_photo):
    filenames = []
    for photo in url_photo:
        r = requests.get(photo, stream=True)

        filename = photo.split('/')[-1]
        filenames.append(filename)
        with open(filename, 'bw') as file:
            for chunk in r.iter_content(4096):
                file.write(chunk)

    return filenames


def getPost(lastTime, k):
    response = requests.get('https://api.vk.com/method/wall.get',
                            params={
                                'access_token': access_token,
                                'v': version,
                                'domain': sosDomain[k],
                                'count': 2
                            }
                            )
    numberPost = 0;
    try:
        checkIsPinned = response.json()['response']['items'][numberPost]['is_pinned']
        numberPost = 1;
    except BaseException:
        print('пост не закреплен')

    time = int(response.json()['response']['items'][numberPost]['date'])

    if time != int(lastTime):

        data = response.json()['response']['items'][numberPost]['text']

        str = data.split(' ')

        res = []

        check = False
        if str.count('Ozon') != 0 or str.count('OZON') != 0 or str.count('ozon') != 0:
            check = True
            for st in str:
                if st.find('OZON7C0JOG') != -1:
                    st = 'OZON0CH43D'

                res.append(st)
        else:
            for st in str:
                if st.find('ali.pub') != -1:
                    check = True
                    r = st.split('\n')
                    dl = st.split("/")
                    url = "https://www.websiteplanet.com/ru/webtools/redirected/?url=http%3A%2F%2Fali.pub%2F" + dl[3][0:6]
                    st = deeplink(url) + '\n' + dl[3][6:]
                    #st = shortLink(dplink) + '\n' + dl[3][6:]

                res.append(st)

        if check:
            url_photos = []
            count_photo = response.json()['response']['items'][numberPost]['attachments']
            for i in count_photo:
                photo = i['photo']['sizes']
                url_photo = photo[len(photo) - 1]['url']

                url_photos.append(url_photo)

            names_photos = download_photo(url_photos)

            text = ' '.join(res)

            photos = []

            for photo in names_photos:
                upload_url = photosGetUpload()
                params = photosUploadPhotoToURL(upload_url, photo)
                photos.append(photosSaveWallPhoto(params))

            try:
                setPost(text, photos, k)
            except BaseException:
                print('cмени токен или выставил 50 постов за день')

            try:
                telegram.postMyChannel(text, names_photos)
            except BaseException:
                print('что-то с телегой')

            try:
                delPhotos(names_photos)
            except BaseException:
                print('не удалось удалить фотки')
        else:
            print('в посте не было ссылок')
    else:
        print('пост уже был выставлен')

    return time


def shortLink(url):
    opts = Options()
    opts.headless = True
    assert opts.headless  # без графического интерфейса.

    browser = webdriver.Firefox(options=opts)
    browser.get('https://www.admitad.com/ru/webmaster/shortlink/')
    login = ''
    pasw = ''
    class_login = 'fields__input'
    id_login = 'id_login'
    id_pasw = 'id_password'
    id_button = 'id_sign_in'
    browser.find_element_by_id(id_login).clear()
    browser.find_element_by_id(id_login).send_keys(login)
    browser.find_element_by_id(id_pasw).clear()
    browser.find_element_by_id(id_pasw).send_keys(pasw)
    browser.find_element_by_id(id_button).click()
    browser.find_element_by_id('id_url').clear()
    browser.find_element_by_id('id_url').send_keys(url)
    elements = browser.find_element_by_class_name('cta.cta_primary')
    elements = browser.find_elements_by_tag_name('button')
    sleep(1)
    elements[13].click()
    print()

    test = browser.find_elements_by_id('id_result-url')
    test = browser.find_element_by_xpath('/html/body/main/section/form/div[3]/input')

    url = test.get_attribute('value')

    print()
    browser.quit()
    return url


def photosGetUpload():
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer',
                            params={
                                'access_token': oauth,
                                'v': version,
                                'group_id': str(myId)[1:]
                            })

    upload_url = response.json()['response']['upload_url']

    return upload_url


def photosUploadPhotoToURL(upload_url, photo):
    response = requests.post(upload_url, files={'photo': open(photo, "rb")})

    params = [response.json()['server'], response.json()['photo'], response.json()['hash']]

    return params


def photosSaveWallPhoto(params):
    response = requests.get('https://api.vk.com/method/photos.saveWallPhoto',
                            params={
                                'server': params[0],
                                'photo': params[1],
                                'hash': params[2],
                                'v': version,
                                'access_token': oauth,
                                'group_id': str(myId)[1:]
                            })

    id = response.json()['response'][0]['id']
    owner_id = str(response.json()['response'][0]['owner_id'])
    
    return 'photo' + owner_id + '_' + str(id)


def setPost(text, photos, k):
    response = requests.get('https://api.vk.com/method/wall.post',
                            params={
                                'access_token': oauth,
                                'v': version,
                                'owner_id': myId,
                                'message': text,
                                'scope': 'wall',
                                'attachment': ','.join(photos),
                                'from_group': 1,
                                'close_comments': 0,
                                'mark_as_ads': 0,
                                'mute_notifications': 0
                            }
                            )

    id_post = response.json()['response']['post_id']
    print('выставлена запись: id = ' + str(id_post) + ' с группы ' + sosDomain[k])


def delPhotos(photos):
    for photo in photos:
        os.remove(photo)


if __name__ == '__main__':
    last_time = [0, 0, 0]

    n = int(input('из скольких групп тянуть? '))
    while True:
        for i in range(n):
            last_time[i] = getPost(last_time[i], i)
            sleep(120)
