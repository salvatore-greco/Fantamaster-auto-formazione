from dotenv import load_dotenv
import os 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.firefox.options import Options


# accetta cookie button class  css-1j32juq
# submit button class css-edufnu

class AutoLineup:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.driver = webdriver.Firefox()
        self.squad_name = None
        
    def login(self):
        self.driver.get('https://leghe.fantamaster.it/login/')
        
        # Rejecting cookie
        reject_cookie_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "qc-cmp2-close-icon")))
        reject_cookie_btn.click()
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
    
if __name__ == '__main__':
    auto_lineup = AutoLineup()
    auto_lineup.login()
    auto_lineup.get_info()
    auto_lineup.check_lineup_submitted()
    auto_lineup.driver.quit()
    print('Done')