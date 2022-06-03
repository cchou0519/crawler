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
    def __init__(self, executor, track_list=[], headless=False, wait_timeout=10, init_lat=None, init_lon=None):
        # full screen chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        # enable headless mode
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        # local driver
        driver = webdriver.Chrome(options=options, executable_path='chromedriver.exe')
        if (init_lat is not None) and (init_lon is not None):
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": init_lat,
                "longitude": init_lon,
                "accuracy": 100
            })

        # connect to remote driver
        '''
        driver = webdriver.Remote(
            command_executor=executor,
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options,
        )
        if (init_lat is not None) and (init_lon is not None):
            param = {
                "latitude": init_lat,
                "longitude": init_lon,
                "accuracy": 100
            }            
            self.send("Emulation.setGeolocationOverride", param)
        # '''

        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.BASE_URL = "https://twpkinfo.com/ipoke.aspx"
        self.track_list = track_list

    def send(self, cmd, params):
        resource = "/session/%s/chromium/send_command_and_get_result" % self.driver.session_id
        url = self.driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = self.driver.command_executor._request('POST', url, body)
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
            # print(cookies)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except:
            pass

    def refresh(self):
        self.driver.refresh()

    def click_filter_btn(self):
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
                if show_high_iv_checkbox.is_selected() is not True:
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

    def find_100(self):
        output = []
        try:
            list_100 = self.wait.until(
                EC.visibility_of_all_elements_located(
                    (By.CLASS_NAME, 'poke_divIcon26_iv100_img')
                )
            )

            for item in list_100:
                pm_element = item.find_element_by_xpath('../../img')
                pm_img = pm_element.get_attribute("src")

                if len(self.track_list) > 0:
                    pm_number = pm_img.split('/')[-1].split(".")[0]

                    if pm_number not in self.track_list:
                        if "_" not in pm_number:
                            continue

                index = pm_element.find_element_by_xpath('../..').get_attribute("style").split(": ")[-1][:-1]
                output.append([pm_element, pm_img, index])
        except:
            pass
        return output

    def get_pokemon_info(self, element):
        # check no leaflet-popup plane
        # try:
        #     self.driver.find_element(By.CLASS_NAME, "leaflet-popup-close-button").click()
        #
        #     # popup_close_button = self.wait.until(
        #     #     EC.visibility_of_element_located(
        #     #         (By.CLASS_NAME, "leaflet-popup-close-button")
        #     #     )
        #     # )
        #     # popup_close_button.click()
        # except:
        #     pass
        try:
            ActionChains(self.driver).move_to_element(element).perform()

            pokemon_name = self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/div/span[1]/b')
                )
            ).text

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
        except:
            return []
        return [pokemon_name, my_copyLocation, countdown]

    def set_track_list(self, new_list=[]):
        self.track_list = new_list

    def logout(self):
        self.driver.find_element(
            By.CSS_SELECTOR, ".profile-toggle-parent .icon-profile"
        ).click()
        self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#dap-open-logout-modal > span")
            )
        ).click()
        self.wait.until(
            EC.visibility_of_element_located((By.ID, "logout-modal-commit"))
        ).click()

    def close(self):
        self.driver.close()