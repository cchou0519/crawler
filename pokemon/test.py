from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time

# options = webdriver.ChromeOptions()
#
# browser = webdriver.Chrome(options=options)
# browser.get("https://www.google.com")
# pickle.dump(browser.get_cookies(), open("cookies.pkl", "wb"))
# breakpoint()

# cookies = pickle.load(open("cookies.pkl", "rb"))
# print(cookies)
# breakpoint()


class Pokemon_Radar_Instance:
    def __init__(self, headless=False, wait_timeout=60):
        # full screen chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        # enable headless mode
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        # local driver
        driver = webdriver.Chrome(options=options, executable_path='D:\Workspace\python\selenium\webdrivers\chromedriver_win32.exe')

        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": 24.154827,
            "longitude": 120.621834,
            "accuracy": 100
        })
        # connect to remote driver
        '''
        driver = webdriver.Remote(
            command_executor=executor,
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options,
        )
        '''
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.BASE_URL = "https://twpkinfo.com/ipoke.aspx"

    def open_url(self):
        self.driver.get(self.BASE_URL)

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()

    def save_cookies(self, cookie_name="cookies.pkl"):
        pickle.dump(self.driver.get_cookies(), open(cookie_name, "wb"))

    def load_cookies(self, cookie_name="cookies.pkl"):
        try:
            cookies = pickle.load(open(cookie_name, "rb"))
            print(cookies)
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
            print("waiting for high_iv_checkbox")
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
                print(show_high_iv_checkbox.is_selected())
                if show_high_iv_checkbox.is_selected() is not True:
                    high_iv_span.click()
                break
            except:
                pass

        for i in range(retry):
            print("waiting for lang_span_pvp_poke")
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
                print(show_pvp_poke_checkbox.is_selected())
                if show_pvp_poke_checkbox.is_selected() is True:
                    pvp_poke_span.click()
                break
            except:
                pass

        for i in range(retry):
            print("waiting for hidden all pokemon")
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
        for i in range(4):
            time.sleep(5)
            self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="map"]/div[2]/div[1]/div[1]/a[2]')
                )
            ).click()

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


instance = Pokemon_Radar_Instance()

instance.open_url()
instance.delete_all_cookies()
instance.load_cookies(cookie_name="cookies3.pkl")

instance.refresh()
# instance.open_url()
instance.click_filter_btn()
instance.zoom_out()
# instance.save_cookies(cookie_name="cookies3.pkl")
time.sleep(5)
instance.refresh()




# instance.save_cookies()
