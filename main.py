from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import json

class EasyApplyLinkedin:

    def __init__(self, data):
        """Parameter initialization"""

        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        option = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options = option)
        self.driver.get('https://www.google.com/')


    def login_linkedin(self):
        """This function logs into your personal LinkedIn profile"""
        # go to the LinkedIn login url
        self.driver.get("https://www.linkedin.com/login")

        # introduce email and password and hit enter
        
        login_email = self.driver.find_element('name','session_key')
        login_email.clear()
        login_email.send_keys(self.email)
        login_pass = self.driver.find_element('name','session_password')
        login_pass.clear()
        login_pass.send_keys(self.password)
        login_pass.send_keys(Keys.RETURN)
        try:
            # Wait until the user has logged in by checking for an element on the homepage
            WebDriverWait(self.driver, 150).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search']"))
            )
        except TimeoutException:
            print("Timed out waiting for user to solve CAPTCHA or login.")
        
    def job_search(self):
    #This function goes to the 'Jobs' section and looks for all the jobs that match the keywords and location
        self.driver.get("https://www.linkedin.com/jobs")
    
    # Wait for the search input fields to be present
        wait = WebDriverWait(self.driver, 15)
    
        search_keywords = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")))
        search_keywords.clear()
        search_keywords.send_keys(self.keywords)
        
        search_location = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")))
        search_location.clear()
        search_location.send_keys(self.location)
        search_keywords.send_keys(Keys.RETURN)

    def filter(self):
    #"""This function filters the job results by 'Easy Apply'"""
        wait = WebDriverWait(self.driver, 10)  # Wait up to 10 seconds

        try:
        # Look for the "Easy Apply" button in the top filter bar
            easy_apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Easy Apply filter.')]")))
            easy_apply_button.click()
            print("Clicked 'Easy Apply' filter button")
            
            # Wait for the results to update
            time.sleep(5)  # Increased wait time to ensure page updates
            results_count = self.driver.find_element(By.CSS_SELECTOR, "small.jobs-search-results-list__text").text
            print(f"Current results count: {results_count}")
            
            print("Filter application completed")
        except TimeoutException:
            print("Could not find 'Easy Apply' button. The page structure might have changed.")
        except Exception as e:
            print(f"An error occurred while applying the filter: {str(e)}")

        # Proceed regardless of whether we could confirm the filter application

        #easy_apply_button.click()
        time.sleep(1)

        time.sleep(2)  # Wait for results to load

    def find_offers(self):
        #"""This function finds all the offers through all the pages result of the search and filter"""
        wait = WebDriverWait(self.driver, 30)
        try:
            total_results = self.driver.find_element(By.CSS_SELECTOR, "small.jobs-search-results-list__text").text
            print(f"Total results: {total_results}")
        except (NoSuchElementException, ValueError, IndexError):
            print("Could not determine total number of results. Proceeding with available listings.")
            total_results = 0
        # find the total amount of results
        #total_results = self.driver.find_element(By.CLASS_NAME, "display-flex.t-12.t-black--light.t-normal")
        #total_results_int = int(total_results.text.split(' ',1)[0].replace(",",""))
        print(total_results)

        time.sleep(2)
        # get results for the first page
        current_page = self.driver.current_url
        results = self.driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")

        # for each job add, submits application if no questions asked
        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_elements(By.CSS_SELECTOR, 'a.job-card-list__title')            
            for title in titles:
                self.submit_apply(title)

        # if there is more than one page, find the pages and apply to the results of each page
        if total_results_int > 24:
            time.sleep(2)

            # find the last page and construct url of each page based on the total amount of pages
            find_pages = self.driver.find_elements(By.CSS_SELECTOR, "li.artdeco-pagination__indicator")
            if find_pages:
                total_pages = find_pages[-1].text
            total_pages = find_pages[len(find_pages)-1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            get_last_page = self.driver.find_element(By.XPATH, "//button[@aria-label='Page "+str(total_pages_int)+"']")
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.driver.current_url
            total_jobs = int(last_page.split('start=',1)[1])

            # go through all available pages and job offers and apply
            for page_number in range(25,total_jobs+25,25):
                self.driver.get(current_page+'&start='+str(page_number))
                time.sleep(2)
                results_ext = self.driver.find_elements(By.CLASS_NAME, "occludable-update.artdeco-list__item--offset-4.artdeco-list__item.p0.ember-view")
                for result_ext in results_ext:
                    hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                    hover_ext.perform()
                    titles_ext = result_ext.find_elements(By.CLASS_NAME, 'job-card-search__title.artdeco-entity-lockup__title.ember-view')
                    for title_ext in titles_ext:
                        self.submit_apply(title_ext)
        else:
            self.close_session()

    def submit_apply(self,job_add):
        """This function submits the application for the job add found"""

        print('You are applying to the position of: ', job_add.text)
        job_add.click()
        time.sleep(2)
        
        # click on the easy apply button, skip if already applied to the position
        try:
            in_apply = self.driver.find_element(By.CLASS_NAME, 'jobs-apply-button artdeco-button artdeco-button--3 artdeco-button--primary ember-view')
            in_apply.click()
        except NoSuchElementException:
            print('You already applied to this job, go to next...')
            pass
        time.sleep(1)

        # try to submit if submit application is available...
        try:
            submit = self.driver.find_element(By.XPATH, "//button[@data-control-name='submit_unify']")
            submit.send_keys(Keys.RETURN)
        
        # ... if not available, discard application and go to next
        except NoSuchElementException:
            print('Not direct application, going to next...')
            try:
                discard = self.driver.find_element(By.XPATH, "//button[@data-test-modal-close-btn]")
                discard.send_keys(Keys.RETURN)
                time.sleep(1)
                discard_confirm = self.driver.find_element(By.XPATH, "//button[@data-test-dialog-primary-btn]")
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(1)
            except NoSuchElementException:
                pass

        time.sleep(1)

    def close_session(self):
        """This function closes the actual session"""
        
        print('End of the session, see you later!')
        self.driver.close()

    def apply(self):
        """Apply to job offers"""

        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        self.job_search()
        self.filter()
        job_offers = self.find_offers()
        for job in job_offers:
            self.submit_apply(job)
        self.close_session()


if __name__ == '__main__':

    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.apply()