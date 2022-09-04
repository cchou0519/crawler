import time
import os
from instance import PokemonRadarInstance
import requests
import pytz
import logging
import pygsheets

tz = pytz.timezone('Asia/Taipei')
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

# 24.687080,121.772213
INIT_LAT = os.environ.get('INIT_LAT') if os.environ.get('INIT_LAT') is not None else 24.687080
INIT_LON = os.environ.get('INIT_LON') if os.environ.get('INIT_LON') is not None else 121.772213
EXECUTOR = os.environ.get('REMOTE_EXECUTOR') if os.environ.get('REMOTE_EXECUTOR') is not None else ""
LINE_TOKEN = os.environ.get('LINE_TOKEN') if os.environ.get('LINE_TOKEN') is not None else ""
IS_100 = os.environ.get("IS_100") if os.environ.get('IS_100') is not None else "False"
IS_PVP = os.environ.get("IS_PVP") if os.environ.get('IS_PVP') is not None else "True"
ZOOM_OUT_TIMES = int(os.environ.get("ZOOM_OUT_TIMES")) if os.environ.get('ZOOM_OUT_TIMES') is not None else 5
survey_url = os.environ.get("SURVEY_URL") if os.environ.get('SURVEY_URL') is not None else "https://docs.google.com/spreadsheets/d/1LBhE66v6AJnsN4PtmdAiM2X6TMyK1yYyrefF0oqlOiU/"
worksheet_name = os.environ.get("WORK_SHEET_NAME") if os.environ.get('WORK_SHEET_NAME') is not None else "豪豪的特別條件區2"

if IS_100.lower() == 'true':
    IS_100 = True
else: 
    IS_100 = False
    
if IS_PVP.lower() == 'true':
    IS_PVP = True
else: 
    IS_PVP = False

    
def get_id_map_json():
    gc = pygsheets.authorize(service_account_file='config/google-sheet-key.json')
    sh = gc.open_by_url(survey_url)
    wks2 = sh.worksheet_by_title(worksheet_name)
    c = wks2.get_as_df(numerize=False).astype('str')[["ID", "名稱"]]
    output = {}
    output_2 = {}
    for (_id, name) in zip(c["ID"], c["名稱"]):
        output[_id] = name
        output_2[name] = _id

        if "_" in name:
            # 野蠻鱸魚(RED_STRIPED) -> [野蠻鱸魚, RED_STRIPED)]
            tmp = name.split("(")

            # RED_STRIPED) -> [RED, STRIPED)] -> RED
            tmp1 = tmp[1].split("_")[0]

            # 野蠻鱸魚(RED)
            name2 = tmp[0] + "(" + tmp1 + ")"

            output[name2] = name
    return output, output_2


def get_track_list_100():
    gc = pygsheets.authorize(service_account_file='config/google-sheet-key.json')
    sh = gc.open_by_url(survey_url)
    wks2 = sh.worksheet_by_title(worksheet_name)
    c = wks2.get_as_df(numerize=False).astype('str')

    return list(c["ID"].loc[c['4*'].str.contains('X')])


def get_track_list_pvp():
    gc = pygsheets.authorize(service_account_file='config/google-sheet-key.json')
    sh = gc.open_by_url(survey_url)
    wks2 = sh.worksheet_by_title(worksheet_name)
    c = wks2.get_as_df(numerize=False).astype('str')

    gl_list = list(c["名稱"].loc[c['GL'].str.contains('X')])
    ul_list = list(c["名稱"].loc[c['UL'].str.contains('X')])
    return gl_list, ul_list


def lineNotifyMessage(msg, img_path=None):
    headers = {
        "Authorization": "Bearer " + LINE_TOKEN,
    }
    data = {
        'message': msg
    }
    if img_path is not None:
        try:
            image = open(img_path, 'rb')
            imageFile = {'imageFile': image}
            r = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data, files=imageFile)
        except:
            r = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)
    else:
        r = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

    return r.status_code


def save_screenshot(driver, path):
    driver.save_screenshot(path)


os.makedirs("img", exist_ok=True)

if IS_100:
    track_list_100 = get_track_list_100()
else:
    track_list_100 = []

if IS_PVP:
    track_list_pvp_gl, track_list_pvp_ul = get_track_list_pvp()

id_map_json, name_to_id_json = get_id_map_json()

if EXECUTOR != "":
    is_remote = True
else:
    is_remote = False

instance = PokemonRadarInstance(EXECUTOR, pm_id_map_json=id_map_json, is_remote=is_remote,
                                init_lat=INIT_LAT, init_lon=INIT_LON, track_list_100=track_list_100)

instance.open_url()

# load cookies
instance.delete_all_cookies()
instance.load_cookies(cookie_name="config/cookies3.pkl")
instance.refresh()

# change filter
instance.click_filter_btn(is_pvp=IS_PVP, is_100=IS_100)

# change to default area
for i in range(ZOOM_OUT_TIMES):
    instance.zoom_out()

time.sleep(5)

# start find_100 loop!!!
is_zoom_in = True
pokemon_buffer = {}
init_track_time = time.time()
this_time = init_track_time
try:
    while True:
        logging.info("scanning...")
        this_time = time.time()

        # 每小時去抓一次google sheet
        if this_time - init_track_time > 10 * 60:

            id_map_json, name_to_id_json = get_id_map_json()
            instance.set_pm_id_map_json(id_map_json)

            if IS_100:
                track_list_100 = get_track_list_100()
                instance.set_track_list_100(track_list_100)

            if IS_PVP:
                track_list_pvp_gl, track_list_pvp_ul = get_track_list_pvp()

            init_track_time = this_time

        # clean buffer
        for key in list(pokemon_buffer.keys()):
            if pokemon_buffer[key]["expire_in"] < this_time:
                pokemon_buffer.pop(key, None)

        #track_list = []
        #instance.set_track_list_100(track_list)

        # 查找並返回100或pvp的列表
        if IS_100:
            list_100 = instance.find_100()
        else:
            list_100 = []
        if IS_PVP:
            list_pvp = instance.find_pvp()
        else:
            list_pvp = []
            
        logging.info("is_100..." + str(IS_100))
        logging.info("list_100_len:" + str(len(list_100)))
        logging.info("is_pvp..." + str(IS_PVP))
        logging.info("list_pvp_len:" + str(len(list_pvp)))
        list_all = list_100 + list_pvp
        
        # save_screenshot(instance.driver, "/tmp/%s.png" % str(this_time))
        processing_list_100 = True
        time.sleep(5)
        for i in range(len(list_all)):
            if i >= len(list_100):
               processing_list_100 = False
            
            _l = list_all[i]
            img_name = "img/" + _l[1].split("/")[-1]

            # 判斷圖片是否存在，不存在則寫入
            if not os.path.exists(img_name):
                img = requests.get(_l[1])
                with open(img_name, "wb") as file:
                    file.write(img.content)

            pminfo = instance.get_pokemon_info(_l[0], is_pvp=IS_PVP)
            if len(pminfo) > 0:
                if pminfo[1] in pokemon_buffer:
                    continue
                if "少於" in pminfo[2]:
                    continue

                remain = pminfo[2]
                expire_in = int(pminfo[2].replace("大約", "").replace("分鐘(僅供參考)", "")) * 60 + time.time()
                pokemon_buffer[pminfo[1]] = {
                    "pokemon": pminfo[0],
                    "expire_in": expire_in,
                    "location": pminfo[1],
                    "remain": "剩餘" + remain,
                    "pvp_info": pminfo[3]
                }

                msg = "\n" + pminfo[0] + \
                      "\n" + pminfo[1] + \
                      "\n剩餘" + remain

                is_in_track_pvp_list = False
                if len(pminfo[3]) > 0:
                    for pvp_info in pminfo[3]:
                        # if "(" not in pvp_info[0]:
                        if pvp_info[1] == "UL":
                            if pvp_info[0] not in track_list_pvp_ul:
                                continue
                        if pvp_info[1] == "GL":
                            if pvp_info[0] not in track_list_pvp_gl:
                                continue
                        is_in_track_pvp_list = True
                        msg += "\n" + pvp_info[1] + " " + pvp_info[0]
                else:
                    if processing_list_100:
                        is_in_track_pvp_list = True
                        msg = "\n這隻100!!!" + msg

                if is_in_track_pvp_list:
                    logging.info(msg)

                    # print(msg)
                    if pminfo[0] in name_to_id_json:
                        img_name = "img/" + name_to_id_json[pminfo[0]] + ".png"
                        # 判斷圖片是否存在，不存在則寫入
                        if not os.path.exists(img_name):
                            try:
                                img = requests.get("https://twpkinfo.com/images/poke1/" + name_to_id_json[pminfo[0]] + ".png")
                                with open(img_name, "wb") as file:
                                    file.write(img.content)
                            except:
                                lineNotifyMessage(msg="錯誤!!也許連結不存在: https://twpkinfo.com/images/poke1/" + name_to_id_json[pminfo[0]] + ".png")
                    else:
                        lineNotifyMessage(msg="錯誤!!google sheet內沒有存放" + pminfo[0] + "的ID! img_url是: " + str(_l[1]))

                    # 傳送line通知
                    logging.info(str(pokemon_buffer[pminfo[1]]))
                    lineNotifyMessage(msg=msg, img_path=img_name)

        if is_zoom_in:
            is_zoom_in = False
            instance.zoom_in()
        else:
            is_zoom_in = True
            instance.zoom_out()

        time.sleep(10)
except Exception as e:
    logging.info(str(e))
    save_screenshot(instance.driver, "/tmp/%s.png" % str(this_time))
    lineNotifyMessage(msg="掛了QQ", img_path="/tmp/%s.png" % str(this_time))
finally:
    instance.close()

# instance.save_cookies(cookie_name="cookies3.pkl")
