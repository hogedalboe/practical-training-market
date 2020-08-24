from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Requirements
# Install selenium via cmd: pip install selenium
# Download Chrome driver: https://chromedriver.chromium.org/downloads

# https://stackabuse.com/getting-started-with-selenium-and-python/
# https://selenium-python.readthedocs.io/waits.html

EXE_PATH = r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Python\chromedriver.exe"
driver = webdriver.Chrome(executable_path=EXE_PATH)
driver.get('https://map.krak.dk/?mode=route')

# Cookies
try:
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='qcCmpButtons']/button[2]"))).click() # Accept cookies
except:
    pass

# Input route parameters and submit
WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='topleft']/div[1]/div[1]/div[2]/span[2]/input"))).send_keys('Mercantec') # Origin
WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='topleft']/div[1]/div[1]/div[1]/span[2]/input"))).send_keys('Rundetårn') # Destination
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='topleft']/div[1]/div[1]/div[4]/button"))).click() 

# Get duration and distance by car
strResultDurationCar = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='topleft']/div[1]/div[3]/p[1]/span[1]"))).text
strResultDistanceCar = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='topleft']/div[1]/div[3]/p[1]/span[2]"))).text
print("------------- By car --------------\nDuration: {0}\nDistance: {1}".format(strResultDurationCar, strResultDistanceCar))

## Change route mode to public transportation and set parameters
#WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='topleft']/div[1]/div[1]/button[2]"))).click() # Change route mode to public transportation
#WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='topleft']/div[1]/div[1]/div[3]/select/option[2]"))).click() # Select 'arrival'
#WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='hoursList']/option[9]"))).click() # Select '8' hours
#WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='minutesList']/option[1]"))).click() # Select '0' minutes
#WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='topleft']/div[1]/div[1]/div[4]/button"))).click() 
#
## Get duration by public transportation
#strResultDurationPublic = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='topleft']/div[1]/div[3]/ul/li[1]/span[1]"))).text
#print("------------- By public transportation --------------\nDuration: {0}".format(strResultDurationPublic))

