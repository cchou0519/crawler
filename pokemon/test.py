import time
import os
from instance import PokemonRadarInstance
import requests
import pytz
import logging
import datetime

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
tz = pytz.timezone('Asia/Taipei')

# options = webdriver.ChromeOptions()
#
# browser = webdriver.Chrome(options=options)
# browser.get("https://www.google.com")
# pickle.dump(browser.get_cookies(), open("cookies.pkl", "wb"))
# breakpoint()

# cookies = pickle.load(open("cookies.pkl", "rb"))
# print(cookies)
# breakpoint()


# 24.721547,120.891013
INIT_LAT = os.environ.get('INIT_LAT') if os.environ.get('INIT_LAT') is not None else 24.721547
INIT_LON = os.environ.get('INIT_LON') if os.environ.get('INIT_LON') is not None else 120.891013
EXECUTOR = os.environ.get('REMOTE_EXECUTOR') if os.environ.get('REMOTE_EXECUTOR') is not None else "http://localhost:4444/wd/hub"


os.makedirs("img", exist_ok=True)

instance = PokemonRadarInstance(EXECUTOR, init_lat=INIT_LAT, init_lon=INIT_LON)

instance.open_url()

# road cookies
instance.delete_all_cookies()
instance.load_cookies(cookie_name="config/cookies3.pkl")
instance.refresh()

# change filter
instance.click_filter_btn()
time.sleep(5)

# change to default area
for i in range(3):
    instance.zoom_out()
    time.sleep(5)

# 查找並返回100的列表
list_100 = instance.find_100()
print(list_100)

if len(list_100) > 0:
    for _l in list_100:
        img = requests.get(_l[1])
        img_name = "img/" + _l[1].split("/")[-1] + ".jpg"

        # 判斷圖片是否存在，不存在則寫入
        if os.path.exists(img_name) is not True:
            with open(img_name, "wb") as file:
                file.write(img.content)

# instance.save_cookies(cookie_name="cookies3.pkl")




# instance.save_cookies()
