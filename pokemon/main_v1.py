import time
import os
from instance import PokemonRadarInstance
import requests
import pytz
import logging
import pygsheets
import base64


tz = pytz.timezone('Asia/Taipei')
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

# 24.721547,120.891013
INIT_LAT = os.environ.get('INIT_LAT') if os.environ.get('INIT_LAT') is not None else 24.721547
INIT_LON = os.environ.get('INIT_LON') if os.environ.get('INIT_LON') is not None else 120.891013
# http://localhost:4444/wd/hub
EXECUTOR = os.environ.get('REMOTE_EXECUTOR') if os.environ.get(
    'REMOTE_EXECUTOR') is not None else ""
# LINE_TOKEN = os.environ.get('LINE_TOKEN')
LINE_TOKEN = os.environ.get('LINE_TOKEN') if os.environ.get('LINE_TOKEN') is not None else ""


def get_track_list():
    gc = pygsheets.authorize(service_account_file='config/google-sheet-key.json')

    survey_url = 'https://docs.google.com/spreadsheets/d/1LBhE66v6AJnsN4PtmdAiM2X6TMyK1yYyrefF0oqlOiU/edit#gid=1745896057'
    sh = gc.open_by_url(survey_url)
    wks2 = sh.worksheet_by_title("豪豪的特別條件區")
    c = wks2.get_as_df([["ID", "4*"]]).astype('str')

    return list(c["ID"].loc[c['4*'].str.contains('X')])


def lineNotifyMessage(msg, img_path=None):
    headers = {
        "Authorization": "Bearer " + LINE_TOKEN,
    }
    data = {
        'message': msg
    }
    if img_path is not None:
        image = open(img_path, 'rb')
        imageFile = {'imageFile': image}

        r = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data, files=imageFile)
    else:
        r = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

    return r.status_code


def save_screenshot(driver, path):
    driver.save_screenshot(path)
    #with open(path, "rb") as img_file:
    #    my_string = base64.b64encode(img_file.read())
    #logging.info("screenshot base64 encoding: \n" + my_string.decode("utf-8"))


os.makedirs("img", exist_ok=True)
track_list = get_track_list()

if EXECUTOR != "":
    is_remote = True
else:
    is_remote = False
instance = PokemonRadarInstance(EXECUTOR, is_remote=is_remote,
                                init_lat=INIT_LAT, init_lon=INIT_LON, track_list=track_list)

instance.open_url()

# road cookies
instance.delete_all_cookies()
instance.load_cookies(cookie_name="config/cookies3.pkl")
instance.refresh()

# change filter
instance.click_filter_btn()

# change to default area
for i in range(5):
    instance.zoom_out()

time.sleep(5)

# start find_100 loop!!!
is_zoom_in = True
pokemon_buffer = {}
init_track_time = time.time()
try:
    while True:
        logging.info("scanning...")
        this_time = time.time()

        # 每小時去抓一次google sheet
        if this_time - init_track_time > 60 * 60:
            track_list = get_track_list()
            instance.set_track_list(track_list)
            init_track_time = this_time

        # clean buffer
        for key in list(pokemon_buffer.keys()):
            if pokemon_buffer[key]["expire_in"] < this_time:
                pokemon_buffer.pop(key, None)

        # track_list = []
        # instance.set_track_list(track_list)

        # 查找並返回100的列表
        list_100 = instance.find_100()
        time.sleep(5)
        logging.info(str(list_100))

        for _l in list_100:
            img = requests.get(_l[1])
            img_name = "img/" + _l[1].split("/")[-1]

            # 判斷圖片是否存在，不存在則寫入
            if os.path.exists(img_name) is not True:
                with open(img_name, "wb") as file:
                    file.write(img.content)

            pminfo = instance.get_pokemon_info(_l[0])
            if len(pminfo) > 0:
                if pminfo[1] in pokemon_buffer:
                    continue
                if "少於" in pminfo[2]:
                    continue
                remain = pminfo[2]
                expire_in = int(pminfo[2].replace("大約", "").replace("分鐘(僅供參考)", "")) * 60 + \
                            time.time()
                pokemon_buffer[pminfo[1]] = {
                    "pokemon": pminfo[0],
                    "expire_in": expire_in,
                    "location": pminfo[1],
                    "remain": "剩餘" + remain
                }

                # 傳送line通知
                lineNotifyMessage(msg=pminfo[0] + "\n" + pminfo[1] + "\n" + "剩餘" + remain, img_path=img_name)

        if is_zoom_in:
            is_zoom_in = False
            instance.zoom_in()
        else:
            is_zoom_in = True
            instance.zoom_out()
            
        time.sleep(30)
except Exception as e:
    save_screenshot(instance.driver, "/tmp/%s.png" % str(this_time))
    lineNotifyMessage(msg="掛了QQ", img_path="/tmp/%s.png" % str(this_time))


# instance.save_cookies(cookie_name="cookies3.pkl")
