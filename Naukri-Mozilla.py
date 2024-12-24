import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

firstname = 'Tejas'  # Add your FirstName
lastname = 'Raikar'  # Add your LastName
joblink = []         # Initialized list to store links
maxcount = 50        # Max daily apply quota for Naukri
keywords = ['Network Engineer', 'Technical specialist']  # List of roles you want to apply for
location = ''        # Add your location/city name for within India or remote
applied = 0          # Count of jobs applied successfully
failed = 0           # Count of jobs failed
applied_list = {
    'passed': [],
    'failed': []
}                    # Saved list of applied and failed job links for manual review

try:
    options = Options()
    profile_path = r"C:\Users\Tejas Raikar\AppData\Roaming\Mozilla\Firefox\Profiles\g2ip8typ.default-esr"
    options.set_preference("profile", profile_path)
    driver = webdriver.Firefox(options=options)
except Exception as e:
    print('Webdriver exception:', e)

time.sleep(10)

for k in keywords:
    for i in range(2):
        if location == '':
            url = f"https://www.naukri.com/{k.lower().replace(' ', '-')}-{i+1}"
        else:
            url = f"https://www.naukri.com/{k.lower().replace(' ', '-')}-jobs-in-{location.lower().replace(' ', '-')}-{i+1}"
        
        driver.get(url)
        print(url)
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        results = soup.find(class_='list')
        job_elems = results.find_all('article', class_='jobTuple bgWhite br4 mb-8')
        
        for job_elem in job_elems:
            joblink.append(job_elem.find('a', class_='title fw500 ellipsis').get('href'))

for i in joblink:
    time.sleep(3)
    driver.get(i)
    
    if applied <= maxcount:
        try:
            time.sleep(3)
            driver.find_element_by_xpath("//*[text()='Apply']").click()
            time.sleep(2)
            applied += 1
            applied_list['passed'].append(i)
            print('Applied for', i, "Count", applied)

        except Exception as e:
            failed += 1
            applied_list['failed'].append(i)
            print(e, "Failed", failed)
        
        try:
            if driver.find_element_by_xpath("//*[text()='Your daily quota has been expired.']"):
                print('MAX Limit reached. Closing browser.')
                driver.close()
                break
            if driver.find_element_by_xpath("//*[text()=' 1. First Name']"):
                driver.find_element_by_xpath("//input[@id='CUSTOM-FIRSTNAME']").send_keys(firstname)
            if driver.find_element_by_xpath("//*[text()=' 2. Last Name']"):
                driver.find_element_by_xpath("//input[@id='CUSTOM-LASTNAME']").send_keys(lastname)
            if driver.find_element_by_xpath("//*[text()='Submit and Apply']"):
                driver.find_element_by_xpath("//*[text()='Submit and Apply']").click()
        except:
            pass
            
    else:
        driver.close()
        break

print('Completed applying. Closing browser and saving applied jobs to CSV.')
try:
    driver.close()
except:
    pass

csv_file = "naukriapplied.csv"
final_dict = {k: pd.Series(v) for k, v in applied_list.items()}
df = pd.DataFrame.from_dict(final_dict)
df.to_csv(csv_file, index=False)
