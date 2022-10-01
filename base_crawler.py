from selenium import webdriver
import os
from dotenv import load_dotenv
import logging 
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from utils import init_query_list, human_like_mouse_move
import time 
from tinydb import TinyDB

class BaseCrawler():
    def __init__(self):
        """Initializes driver and xpath element dict
        
        Parameters:
            driver (WebDriver): Selenium Webdriver 
            xpath_dict (dict): Dict containing all xpath element identifiers.
            wait_secs (int, optional): Time in seconds for drive implicitly_wait 

        Returns:
            None
        """

        # Load .env to environment variables
        load_dotenv()

        # Init driver
        self.base_url = os.environ.get('BASE_URL')

        # Init identifiers for input related elements
        self.xpath_input_ids = {
            'RECAPTCHA_BOX': os.environ.get('RECAPTCHA_BOX'),
            'CAPTCHA_IMAGE_BOX': os.environ.get('CAPTCHA_IMAGE_BOX'),
            'CAPTCHA_AUDIO_ICON': os.environ.get('CAPTCHA_AUDIO_ICON'),
            'DOWNLOAD_ICON': os.environ.get('DOWNLOAD_ICON'),
            'CAPTCHA_AUDIO_TEXT': os.environ.get('CAPTCHA_AUDIO_TEXT'),
            'CAPTCHA_AUDIO_BUTTON': os.environ.get('CAPTCHA_AUDIO_BUTTON')
        }

        # Init identifiers for data related elements
        self.xpath_data_ids = {
            'PROCCESS_NUMBER': os.environ.get('PROCCESS_NUMBER'),
            'LAST_ACTION': os.environ.get('LAST_ACTION'),
        }

    def _check_for_captcha(self, driver, index):
        iframes = driver.find_elements('tag name', "iframe")
        logging.info("Checking for presearch catpcha...")
        logging.info("iframes: "+ str(len(iframes)))
        detected = False
        try:
            driver.switch_to.frame(iframes[index])
            captcha_box = driver.find_element('xpath', self.xpath_input_ids['CAPTCHA_IMAGE_BOX'])
            detected = True
        except Exception as e:
            logging.info("Captcha not detected.")

        driver.switch_to.default_content()
        
        return detected

    def _do_audio_captcha(self, driver, iframe):
        logging.info("AUDIO CAPTCHA!!!!")
        driver.switch_to.frame(iframe)
        audio_input = driver.find_element('xpath', self.xpath_input_ids['CAPTCHA_AUDIO_ICON'])
        audio_input.click()
        download_input = driver.find_element('xpath', self.xpath_input_ids['DOWNLOAD_ICON'])

        mp3file = urllib.request.urlopen(download_input.get_attribute('href'))
        with open('captcha.mp3', 'wb') as audio_mp3:
            audio_mp3.write(mp3file.read())
        transcription = audio_transcript.transcript('captcha.mp3')

        text_input = driver.find_element('xpath', self.xpath_input_ids['CAPTCHA_AUDIO_TEXT'])
        text_input.send_keys(transcription)

        button = driver.find_element('xpath', self.xpath_input_ids['CAPTCHA_AUDIO_BUTTON'])
        button.click()
        driver.switch_to.default_content()

    def _do_captcha_box(self, driver):
        iframes = driver.find_elements('tag name', "iframe")
        print(iframes)
        logging.info("Checking for captcha box...")
        check_box = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                ('xpath', self.xpath_input_ids['RECAPTCHA_BOX'])
            )
        )

        action = ActionChains(driver)
        human_like_mouse_move(action, check_box)
        check_box.click()

    def run(self, driver):
        driver.get(self.base_url)

        # solve click captcha
        self._do_captcha_box(driver)
        self._do_audio_captcha(driver)
        

if __name__ == "__main__":
    service = Service(GeckoDriverManager().install())
    options = Options()
    options.headless = False
    driver = webdriver.Firefox(options=options, service=service)

    scrapper = BaseCrawler()
    scrapper.run(driver)