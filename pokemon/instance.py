from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
import json
import pickle
import time
import logging


class PokemonRadarInstance:
    def __init__(self, executor, pm_id_map_json, is_remote=False, track_list_100=[],
                 headless=False, wait_timeout=5,
                 init_lat=None, init_lon=None):
        # full screen chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        # enable headless mode
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        if is_remote:
            # connect to remote driver
            driver = webdriver.Remote(
                command_executor=executor,
                desired_capabilities=DesiredCapabilities.CHROME,
                options=options,
            )
            if (init_lat is not None) and (init_lon is not None):
                param = {
                    "latitude": float(init_lat),
                    "longitude": float(init_lon),
                    "accuracy": 100
                }
                rr = self.send(driver, "Emulation.setGeolocationOverride", param)
                logging.info(str(rr))
        else:
            # local driver
            driver = webdriver.Chrome(options=options, executable_path='chromedriver.exe')
            if (init_lat is not None) and (init_lon is not None):
                driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                    "latitude": init_lat,
                    "longitude": init_lon,
                    "accuracy": 100
                })

        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.BASE_URL = "https://twpkinfo.com/ipoke.aspx"
        self.track_list_100 = track_list_100
        self.pm_id_map_json = pm_id_map_json

    def send(self, driver, cmd, params):
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        return response.get('value')

    def open_url(self):
        self.driver.get(self.BASE_URL)

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()

    def save_cookies(self, cookie_name="config/cookies.pkl"):
        pickle.dump(self.driver.get_cookies(), open(cookie_name, "wb"))

    def load_cookies(self, cookie_name="config/cookies.pkl"):
        try:
            cookies = pickle.load(open(cookie_name, "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except:
            logging.info("load cookies error!")

    def refresh(self):
        self.driver.refresh()

    def click_filter_btn(self, is_100=True, is_pvp=False):
        filter_btn = self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "filterspan")
            )
        )
        filter_btn.click()

        retry = 3
        for i in range(retry):
            logging.info("waiting for high_iv_checkbox... retry " + str(i))
            time.sleep(5)
            try:
                show_high_iv_checkbox = self.wait.until(
                    EC.visibility_of_element_located(
                        (By.ID, "show_high_iv")
                    )
                )
                high_iv_span = self.wait.until(
                    EC.visibility_of_element_located(
                        (By.ID, "lang_span_overiv")
                    )
                )
                if is_100:
                    if show_high_iv_checkbox.is_selected() is not True:
                        high_iv_span.click()
                else:
                    if show_high_iv_checkbox.is_selected() is True:
                        high_iv_span.click()
                break
            except:
                pass

        for i in range(retry):
            logging.info("waiting for lang_span_pvp_poke... retry " + str(i))
            time.sleep(5)
            try:
                show_pvp_poke_checkbox = self.wait.until(
                    EC.visibility_of_element_located(
                        (By.ID, "show_pvp_poke")
                    )
                )
                pvp_poke_span = self.wait.until(
                    EC.visibility_of_element_located(
                        (By.ID, "lang_span_pvp_poke")
                    )
                )
                if is_pvp:
                    if show_pvp_poke_checkbox.is_selected() is not True:
                        pvp_poke_span.click()
                else:
                    if show_pvp_poke_checkbox.is_selected() is True:
                        pvp_poke_span.click()
                break
            except:
                pass

        for i in range(retry):
            logging.info("waiting for hidden all pokemon... retry " + str(i))
            try:
                for j in range(1, 9):
                    self.wait.until(
                        EC.visibility_of_element_located(
                            (By.ID, "lang_a_tab" + str(j))
                        )
                    ).click()

                    self.wait.until(
                        EC.visibility_of_element_located(
                            (By.ID, "no_show_all_" + str(j))
                        )
                    ).click()
                break
            except:
                pass

        self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "close2_btn")
            )
        ).click()

    def zoom_out(self):
        time.sleep(5)
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="map"]/div[2]/div[1]/div[1]/a[2]')
            )
        ).click()

    def zoom_in(self):
        time.sleep(5)
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="map"]/div[2]/div[1]/div[1]/a[1]')
            )
        ).click()

    # def find_track_pokemon(self, is_100=True, is_pvp=False):
    #     output = []
    #     try:
    #         if is_100:
    #             list_100 = self.wait.until(
    #                 EC.visibility_of_all_elements_located(
    #                     (By.CLASS_NAME, 'poke_divIcon26_iv100_img')
    #                 )
    #             )
    #         if is_pvp:
    #             list_pvp = self.wait.until(
    #                 EC.visibility_of_all_elements_located(
    #                     (By.CLASS_NAME, 'poke_divIcon25_league_img')
    #                 )
    #             )

    def find_pvp(self):
        output = []
        try:
            list_pvp = self.wait.until(
                EC.visibility_of_all_elements_located(
                    (By.CLASS_NAME, 'poke_divIcon25_league_img')
                )
            )

            for item in list_pvp:
                pm_element = item.find_element_by_xpath('../img')
                pm_img = pm_element.get_attribute("src")

                index = pm_element.find_element_by_xpath('../..').get_attribute("style").split(": ")[-1][:-1]
                output.append([pm_element, pm_img, index])
        except Exception as e:
            pass
        return output

    def find_100(self):
        output = []
        try:
            logging.info("inside find_100 ...")
            list_100 = self.wait.until(
                EC.visibility_of_all_elements_located(
                    (By.CLASS_NAME, 'poke_divIcon26_iv100_img')
                )
            )
            logging.info("success find list_100_len ..." + str(len(list_100)))

            for item in list_100:
                pm_element = item.find_element_by_xpath('../../img')
                pm_img = pm_element.get_attribute("src")

                if len(self.track_list_100) > 0:
                    pm_number = pm_img.split('/')[-1].split(".")[0]

                    if pm_number not in self.track_list_100:
                        if pm_number in self.pm_id_map_json:
                            logging.info("skip " + pm_number)
                            continue

                index = pm_element.find_element_by_xpath('../..').get_attribute("style").split(": ")[-1][:-1]
                output.append([pm_element, pm_img, index])
        except Exception as e:
            logging.info(str(e))
        return output

    def get_pokemon_info(self, element, is_pvp=False):
        try:
            ActionChains(self.driver).move_to_element(element).perform()

            self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/div/span[1]/b')
                )
            )

            countdown = self.wait.until(
                EC.visibility_of_element_located(
                    (By.ID, "countdown")
                )
            ).text

            my_copyLocation = self.wait.until(
                EC.visibility_of_element_located(
                    (By.ID, "my_copyLocation")
                )
            ).text

            pokemon_other_txt = self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/div')
                )
            ).text
            
            # logging.info("pokemon_other_txt: " + str(pokemon_other_txt))

            pokemon_other_txt = str(pokemon_other_txt).splitlines()
            # print("---")
            # print("pokemon_other_txt", pokemon_other_txt)
            pokemon_name = pokemon_other_txt[0].split()[-1]
            
            pvp_out_list = []
            if is_pvp:
          
                for i in range(len(pokemon_other_txt)):
                    if "LV：" in pokemon_other_txt[i]:
                        start_index = i + 2
                        break
                        
                # 確定開始判斷的行號小於總長，這樣內容才有機會放對戰聯盟等資訊，這樣不是pvp的寶可夢就不會進以下block
                if start_index < len(pokemon_other_txt) - 1:
                    # 最後兩行是技能與google map
                    for i in range(start_index, len(pokemon_other_txt) - 2):
                        lines_split = pokemon_other_txt[i].split()
                        if "進化" in lines_split[0]:
                            pvp_pm_name = lines_split[1].upper()
                            if pvp_pm_name in self.pm_id_map_json:
                                pvp_pm_name = self.pm_id_map_json[pvp_pm_name]
                            pvp_pm_rank = lines_split[2]
                            pvp_pm_cp = lines_split[3]
                        else:
                            pvp_pm_name = pokemon_name
                            pvp_pm_rank = lines_split[0]
                            pvp_pm_cp = lines_split[1]

                        if int(pvp_pm_rank) > 1:
                            continue
                        
                        pvp_pm_cp = pvp_pm_cp.split("/")[-1][:-1]

                        if int(pvp_pm_cp) > 1500:
                            pvp_league = "UL"
                        else:
                            pvp_league = "GL"

                        pvp_out_list.append([pvp_pm_name, pvp_league, pvp_pm_rank, pvp_pm_cp])
                        logging.info(str([pvp_pm_name, pvp_league, pvp_pm_rank, pvp_pm_cp]))
                    
                    if len(pvp_out_list) < 1:
                        return []        
                    
            """
            pvp_out_list = []
            if is_pvp:
                trigger = False
                check_text_complete = False
                for lines in pokemon_other_txt:
                    if "技：" in lines:
                        break
                    if trigger:
                        lines_split = lines.split()
                        if "進化" in lines_split[0]:
                            pvp_pm_name = lines_split[1].upper()
                            if pvp_pm_name in self.pm_id_map_json:
                                pvp_pm_name = self.pm_id_map_json[pvp_pm_name]
                            pvp_pm_rank = lines_split[2]
                            pvp_pm_cp = lines_split[3]
                        else:
                            pvp_pm_name = pokemon_name
                            pvp_pm_rank = lines_split[0]
                            pvp_pm_cp = lines_split[1]

                        if int(pvp_pm_rank) > 1:
                            continue

                        pvp_pm_cp = pvp_pm_cp.split("/")[-1][:-1]

                        if int(pvp_pm_cp) > 1500:
                            pvp_league = "UL"
                        else:
                            pvp_league = "GL"

                        pvp_out_list.append([pvp_pm_name, pvp_league, pvp_pm_rank, pvp_pm_cp])
                        logging.info(str([pvp_pm_name, pvp_league, pvp_pm_rank, pvp_pm_cp]))
                    if "聯盟" in lines:
                        trigger = True
                
                if len(pvp_out_list) < 1 and trigger:
                    return []
            """
        except Exception as e:
            return []
        return [pokemon_name, my_copyLocation, countdown, pvp_out_list]

    def set_track_list_100(self, new_list=[]):
        self.track_list_100 = new_list

    def set_pm_id_map_json(self, new_json):
        self.pm_id_map_json = new_json

    def close(self):
        self.driver.close()

    # def logout(self):
    #     self.driver.find_element(
    #         By.CSS_SELECTOR, ".profile-toggle-parent .icon-profile"
    #     ).click()
    #     self.wait.until(
    #         EC.visibility_of_element_located(
    #             (By.CSS_SELECTOR, "#dap-open-logout-modal > span")
    #         )
    #     ).click()
    #     self.wait.until(
    #         EC.visibility_of_element_located((By.ID, "logout-modal-commit"))
    #     ).click()


