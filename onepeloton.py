from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class PeolotonStudios:

    def __init__(self, wait_between_refreshes):
        self.driver = None
        self.wait = None
        self.wait_between_refreshes = wait_between_refreshes

    def login(self, username, password):
        opts = ChromeOptions()
        opts.add_argument("--window-size=1400,1000")
        self.driver = webdriver.Chrome(options=opts)

        # Load the Peloton home page
        self.driver.get("https://studio.onepeloton.com")

        self.wait = WebDriverWait(self.driver,10)

        # Click the login button to open the login form
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='logInButton']")))
        element = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='logInButton']").click()

        # Type in the username
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='usernameOrEmail']")))
        element = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='usernameOrEmail']")
        element.clear()
        element.send_keys(username)

        # Type in the password
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='password']")))
        element = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='password']")
        element.clear()
        element.send_keys(password)

        # Click the login button to submit the form
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='loginButton']")))
        element = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='loginButton']")
        element.click()

    def pick_book_date(self, month, day):

        # Hardcoded for current need
        if month != 'April':
            raise NotImplementedError("Only April is currently supported")
        if day != 16 and day != 23 and day != 30:
            raise NotImplementedError("Only 16, 23, and 30 are currently supported")

        # Click the "Book your spot" link
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='homeHeroCtaButton']")))
        element = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='homeHeroCtaButton']")
        element.click()    
        
        # Switch to the iframe containing the schedule
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='teamup-widget-7248695-0-container']/iframe")))
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH, "//*[@id='teamup-widget-7248695-0-container']/iframe"))

        # Open "pick date" calendar input
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='sticky-container']/div/div/div[1]/div[2]/div[2]/div/div/div/div[1]/button")))
        element = self.driver.find_element(By.XPATH, "//*[@id='sticky-container']/div/div/div[1]/div[2]/div[2]/div/div/div/div[1]/button")
        element.click()

        # Open the "pick month" list
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='headlessui-listbox-button-5']")))
        element = self.driver.find_element(By.XPATH, "//*[@id='headlessui-listbox-button-5']")
        element.click()

        # Pick "April"
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='headlessui-listbox-option-11']/div/div")))
        element = self.driver.find_element(By.XPATH, "//*[@id='headlessui-listbox-option-11']/div/div")
        element.click()
        
        if day == 23:
            path= "//*[@id='sticky-container']/div/div/div[1]/div[2]/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div[5]/div[5]/button"
        elif day == 30:
            path = "//*[@id='sticky-container']/div/div/div[1]/div[2]/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div[6]/div[5]/button"
        else:
            # April 16th
            path = "//*[@id='sticky-container']/div/div/div[1]/div[2]/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div[4]/div[5]/button"
            
        # Pick the target day in April (select at the top)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, path)))
        element = self.driver.find_element(By.XPATH, path)
        element.click()

        # Click "OK" on the calendar input
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='sticky-container']/div/div/div[1]/div[2]/div[2]/div/div/div/div[2]/div/div/div[2]/button[1]")))
        element = self.driver.find_element(By.XPATH, "//*[@id='sticky-container']/div/div/div[1]/div[2]/div[2]/div/div/div/div[2]/div/div/div[2]/button[1]")
        element.click()

    def get_classes(self):       

        # Return list of:
        # {
        #     "day": "2026-04-16",
        #     "weekday": "THURSDAY",
        #     "time": 1300,
        #     "course": "CYCLING",
        #     "title": "Peloton 101",
        #     "status": "BOOK", "FULL", "JOIN WAITLIST"        
        #     "cursor": (day_pos,time_pos,index)  # For use in the XPATH to click the "Join" button for this class
        # }

        # Wait for the spinners in the list of classes to go away
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content-wrapper"]/div[1]/div[2]/div[3]/main/div/div[3]')))
        while True:    
            element = self.driver.find_element(By.XPATH, '//*[@id="content-wrapper"]/div[1]/div[2]/div[3]/main/div/div[3]')
            data = element.get_attribute('innerHTML')
            if "spinner" not in data:
                break    
            time.sleep(2) 
        element = self.driver.find_element(By.XPATH, '//*[@id="content-wrapper"]/div[1]/div[2]/div[3]/main/div/div[3]')
        data = element.get_attribute('innerHTML')

        # Day, Time, Index
        all_classes = []
        pos = 0
        while True:
            i = data.find('eventitem-name', pos)
            if i<0:
                break
            j = data.find('h6 ',i)    
            j = data.find('>',j)+1
            k = data.find('</h6>',j)
            title = data[j:k]
            title = title.replace('<!---->','').strip()
            #print('>'+title+'<')

            j = data.rfind('name="202',0,i)
            k = data.find('"',j+6)
            day = data[j+6:k]
            #print('>'+day+'<')
            j = data.find('datetime',k)
            j = data.find('>',j)+1
            k = data.find('<',j)
            wkday = data[j:k].upper()
            y = wkday.find(' ')
            if y>0:
                wkday = wkday[:y]
            #print('>'+wkday+'<')

            j = data.rfind('<time ',0,i)
            j = data.find('>',j)+1
            k = data.find('<',j)
            tm = data[j:k]
            x = tm.find(':')
            hr = int(tm[:x])
            mn = int(tm[x+1:x+3])
            if tm.endswith('pm') and hr<12:
                hr += 12
            tm = hr*100+mn
            #print('>'+tm+'<')

            j = data.find('uppercase">',i)+11
            k = data.find('<',j)
            course = data[j:k].strip().upper()
            #print('>'+course+'<')

            j = data.find('<button ',i)
            j = data.find('>',j)+1
            k = data.find('<',j)
            status = data[j:k].upper().strip()
            #print('>'+status+'<')

            all_classes.append(
                {
                    "day": day, 
                    "time": tm, 
                    "course": course, 
                    "title": title, 
                    "status": status, 
                    "weekday": wkday
                })

            pos = i+1

        if not all_classes:
            return all_classes

        day_pos = 1
        day_str = all_classes[0]['day']
        time_pos = 1
        time_str = all_classes[0]['time']
        index = 1

        for c in all_classes:
            if c['day'] != day_str:
                day_pos += 1
                day_str = c['day']
                time_pos = 1
                time_str = c['time']
                index = 1
            if c['time'] != time_str:
                time_pos += 1
                time_str = c['time']
                index = 1
            c['cursor'] = (day_pos,time_pos,index)
            index += 1

        return all_classes

    def refresh(self):
        self.driver.refresh()
        time.sleep(self.wait_between_refreshes)  # No need to slam the server
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='teamup-widget-7248695-0-container']/iframe")))
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH, "//*[@id='teamup-widget-7248695-0-container']/iframe")) 

    def click_on_class(self, class_info):
        cursor = class_info['cursor']
        join_path = '//*[@id="content-wrapper"]/div[1]/div[2]/div[3]/main/div[1]/div[3]/div/div/div[%day%]/div/div[%time%]/div/div[%index%]/div/div[3]/button'   
        path = join_path.replace('%day%',str(cursor[0])).replace('%time%',str(cursor[1])).replace('%index%',str(cursor[2]))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, path)))        
        element = self.driver.find_element(By.XPATH, path)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.driver.execute_script("arguments[0].click();", element)

        if class_info['status'] == 'JOIN WAITLIST':
            print(">>> JOINING THE WAITLIST")
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='ds-async-button']")))
            element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='ds-async-button']")
            element.click()
            print(">>> YOU ARE ON THE WAITLIST")
            return
        
        if class_info['status'] != 'BOOK':
            raise Exception("Don't know how to handle status "+class_info['status'])
        
        print(">>> BOOKING THE CLASS")

        # The current page has a "VIEW REGISTRATION OPTIONS" button. Click that.
        # The next page has the cost of the class as a button. Click that.
        # The next page has the "Purchase" button. Click that.
        # The next page is a confirmation for your records -- nothing to click.     S

        print(">>> CLICKING THE 'VIEW REGISTRATION OPTIONS' BUTTON")        
        self.wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div/aside/div[2]/div/div[3]/div[2]/div/div/div[2]/button")))
        element = self.driver.find_element(By.XPATH, "/html/body/div[3]/div/div/aside/div[2]/div/div[3]/div[2]/div/div/div[2]/button")
        element.click()
        
        time.sleep(2)

        print(">>> CLICKING THE 'PAY FOR SINGLE SESSION' BUTTON")
        self.wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div/aside/div[2]/div/div[3]/div[2]/div/div/div/div/div[2]/button")))
        element = self.driver.find_element(By.XPATH, "/html/body/div[3]/div/div/aside/div[2]/div/div[3]/div[2]/div/div/div/div/div[2]/button")
        element.click()

        time.sleep(2)

        print(">>> CLICKING THE 'PURCHASE' BUTTON")
        self.wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div/div[4]/div/form/div[5]/button")))
        element = self.driver.find_element(By.XPATH, "/html/body/div/div/div/div/div[4]/div/form/div[5]/button")
        element.click()

        print(">>> YOU ARE BOOKED")
