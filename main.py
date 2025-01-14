from dotenv import load_dotenv
import os 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import requests
from datetime import datetime, timedelta
import json
import platform
from pathlib import Path

# accetta cookie button class  css-1j32juq
# submit button class css-edufnu

class AutoLineup:
    def __init__(self):
        load_dotenv()
        self.path = Path(__file__).absolute().parent
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.squad_name = None
        self.api_url = 'https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/it.1.json' 


    def load_driver(self):
        options = Options()
        options.add_argument("--headless")
        if platform.machine() == 'aarch64':
            service = Service(executable_path=f'{self.path}/geckodriver')
            self.driver = webdriver.Firefox(options=options, service=service)
        elif platform.machine() == 'x86_64':
            self.driver = webdriver.Firefox(options=options)

    def login(self):
        self.driver.get('https://leghe.fantamaster.it/login/')
        # Rejecting cookie
        try:
            reject_cookie_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "qc-cmp2-close-icon")))
            reject_cookie_btn.click()
        except TimeoutException:
            print('Cookie button did not show up, skipping...')
        # Logging in 
        email_form = self.driver.find_element(By.NAME,'email')
        password_form = self.driver.find_element(By.NAME,'password')
        submit_button = self.driver.find_element(By.CLASS_NAME, 'css-edufnu')
        email_form.send_keys(self.email)
        password_form.send_keys(self.password)
        submit_button.click()
        print("Logged In")

    def get_info(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.url_contains('leghe.fantamaster.it/league'))
            self.league_url = self.driver.current_url
            self.squad_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "css-ay8i8h"))).get_attribute('textContent')
            print(f'Got info. Squad name: {self.squad_name}')
        except Exception as e:
            print(e)
            print(self.driver.current_url)
            self.driver.quit()


    def check_lineup_submitted(self):
        self.driver.get(self.league_url+'/lineups')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'css-1bp6795')))
        squads = self.driver.find_elements(By.CLASS_NAME, 'css-1bp6795') # so che così è sprecone ma bone, mi interessa che prenda tutti gli elementi
        squadsName = set()
        for squad in squads:
            squadsName.add(squad.get_attribute('innerText'))
        
        if self.squad_name not in squadsName:
            self.submit_lineup()
        else:
            print('Lineup already submitted')

    def submit_lineup(self):
        try:
            self.driver.get(self.league_url+'/mylineup')
            div = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME,'css-1puz141'))
                )
            buttons = div.find_elements(By.TAG_NAME, 'button')
            buttons[1].click()
            time.sleep(1)
            buttons[3].click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'css-13r7n1p'))
            ).click()
            print('Lineup submitted')
        except Exception as e:
            print(e)
            print(self.driver.current_url)
            print(self.league_url)

    def first_match_matchday(self) -> bool:
        response = requests.get(self.api_url)
        response = response.json()
        self.today = datetime.now()
        date = self.today.date()
        first_match = []
        n = 1
        for i in response['matches']:
            # matchday_date = date.fromisoformat(i['date'])
            if i['round'] == f'Matchday {n}':
                first_match.append(i)
                n += 1
        for item in first_match:
            matchday_date = date.fromisoformat(item['date'])
            diff = (matchday_date - date).days
            if diff >= 0 and diff < 10:
                next_matchday = item

        combined_time = datetime.fromisoformat(next_matchday['date']+' '+next_matchday['time'])
        due_date = combined_time - timedelta(minutes=30)
        return due_date

if __name__ == '__main__':
    auto_lineup = AutoLineup()
    due_date = auto_lineup.first_match_matchday()
    print(auto_lineup.today)
    if (due_date - auto_lineup.today) <= timedelta(days=0, hours=0, minutes=30):
        auto_lineup.load_driver()
        auto_lineup.login()
        auto_lineup.get_info()
        auto_lineup.check_lineup_submitted()
        auto_lineup.driver.quit()
    else:
        print(f'Still {due_date-auto_lineup.today} until due date')
    print('Done')
