from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

import psycopg2
import pandas
import numpy
import time
from datetime import datetime

import config

class Logger:
    def __init__(self, logfile = config.file_log):
        self.logfile = logfile

    def log(self, text):
        try:
            with open(self.logfile, 'a') as f:
                timestamp = str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
                f.write("{0}\n{1}\n\n".format(timestamp,str(text)))
        except:
            pass

class Database:
    """ ... """

    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self.cur = None
        self.Connect()
    
    def Connect(self):
        try:
            # https://www.postgresqltutorial.com/postgresql-python/connect/

            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            
            self.cur = self.conn.cursor()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    
    def Disconnect(self):
        try:
            self.cur.close()
            self.conn.close()

        except Exception as error:
            print(type(error), error)
    
    def Reconnect(self):
        self.Disconnect()
        self.Connect()

    def Insert(self, sql):
        try:
            self.cur.execute(sql)
            return True
        except Exception as error:
            print(type(error), error)
            return False

    def Read(self, sql):
        try:
            return pandas.io.sql.read_sql(sql, self.conn)
        except Exception as error:
            print(type(error), error)
            return None

    def Commit(self):
        try:
            self.conn.commit()
        except Exception as error:
            print(type(error), error)

class KrakScraper:
    """ ... """

    def __init__(self, chromedriver=config.chromedriverPath, url=config.url_Krak):
        self.chromedriver = chromedriver
        self.url = url
        self.driver = webdriver.Chrome(executable_path=self.chromedriver)
        self.initiate()
        self.acceptCookies()
    
    def reset(self):
        try:
            self.initiate()
        except:
            try:
                self.driver.close()
            except:
                pass
            self.driver = webdriver.Chrome(executable_path=self.chromedriver)
            self.initiate()
            self.acceptCookies()

    def initiate(self):
        self.driver.get(self.url)

    def acceptCookies(self):
        try:
            WebDriverWait(self.driver, config.defaultTimeout).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='qc-cmp2-ui']/div[2]/div/button[3]"))).click()
        except:
            pass
    
    def scrape(self, origin, destination):
        # Input route parameters and submit.
        WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='topleft']/div[1]/div[1]/div[2]/span[2]/input"))).send_keys(origin)
        WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='topleft']/div[1]/div[1]/div[1]/span[2]/input"))).send_keys(destination)
        WebDriverWait(self.driver, config.defaultTimeout).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='topleft']/div[1]/div[1]/div[4]/button"))).click() 

        # Get duration and distance by car.
        strResultDurationCar = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='topleft']/div[1]/div[3]/p[1]/span[1]"))).text
        strResultDistanceCar = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='topleft']/div[1]/div[3]/p[1]/span[2]"))).text

        # Parse duration.
        splitDuration = strResultDurationCar.split()
        if len(splitDuration) == 4:
            hours = splitDuration[0]
            minutes = splitDuration[2]
        elif len(splitDuration) == 2:
            hours = 0
            minutes = splitDuration[0]
        else:
            hours = "NULL"
            minutes = "NULL"

        # Parse distance.
        splitDistance = strResultDistanceCar.split()
        km = splitDistance[0].replace('(','')

        return [km,hours,minutes]

class ProffScraper:
    """ ... """

    def __init__(self, chromedriver=config.chromedriverPath, url=config.url_Proff_base):
        self.chromedriver = chromedriver
        self.url = url

        self.options = Options()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--ignore-certificate-errors-spki-list')

        self.driver = webdriver.Chrome(chrome_options=self.options, executable_path=self.chromedriver)
        self.initiate()
        self.acceptCookies()
    
    def reset(self):
        try:
            self.initiate()
        except:
            try:
                self.driver.close()
            except:
                pass
            self.driver = webdriver.Chrome(chrome_options=self.options, executable_path=self.chromedriver)
            self.initiate()
            self.acceptCookies()
    
    def acceptCookies(self):
        try:
            WebDriverWait(self.driver, config.defaultTimeout).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='coi-tcf-modal-main']/div/div/div[3]/button[2]"))).click()
        except:
            pass

    def initiate(self):
        self.driver.get(self.url)
    
    def scrape(self, cvr):

        # Search CVR number.
        url_q = "{0}branchesøg?q={1}".format(self.url, cvr)
        self.driver.get(url_q)
        
        # Click the first result.
        try:
            WebDriverWait(self.driver, config.defaultTimeout).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='main-content']/div[2]/section/div[3]/div/div/div[1]/div/header/h3/a"))).click()
        except:
            WebDriverWait(self.driver, config.defaultTimeout).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='main-content']/div[3]/section/div[3]/div[1]/div/div[1]/div/header/h3/a"))).click()

        # Verify that the company page corresponds to the CVR number.
        pageCvr = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='page-title']/div[3]/header/span[1]/em[1]"))).text
        if cvr in pageCvr:

            # Get information.
            employees = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='overview_company']/section/ul/li[5]/em"))).text
            established = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='overview_company']/section/ul/li[4]/em"))).text
            
            # Navigate to key figures and scrape them.
            time.sleep(config.ratelimit)
            url_keyFigures = self.driver.current_url.replace('firma','nogletal')
            self.driver.get(url_keyFigures)

            tmpPubyear = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='keyFigures_companyAccounts']/section[1]/div[3]/table/thead/tr/th[2]/span"))).text
            
            pubyear = tmpPubyear.split('-')[0]
            roi = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='keyFigures_companyAccounts']/section[1]/div[3]/table/tbody/tr[7]/td[1]"))).text # Afkastningsgrad.
            liquidityratio = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='keyFigures_companyAccounts']/section[1]/div[3]/table/tbody/tr[9]/td[1]"))).text # Likviditetsgrad.
            solvencyratio = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='keyFigures_companyAccounts']/section[1]/div[3]/table/tbody/tr[11]/td[1]"))).text # Soliditetsgrad.
            
            # Navigate to financial reports and scrape the latest (same publication year as the key figures).
            time.sleep(config.ratelimit)
            url_reports = self.driver.current_url.replace('nogletal','regnskab')
            self.driver.get(url_reports)

            netturnover = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='keyFigures_companyAccounts']/section[1]/div[5]/table/tbody/tr[2]/td[1]"))).text
            grossprofit = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='keyFigures_companyAccounts']/section[1]/div[5]/table/tbody/tr[8]/td[1]"))).text
            equity = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='keyFigures_companyAccounts']/section[1]/div[6]/table/tbody/tr[54]/td[1]"))).text
            netresult = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='keyFigures_companyAccounts']/section[1]/div[5]/table/tbody/tr[34]/td[1]"))).text
            currency = WebDriverWait(self.driver, config.defaultTimeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='keyFigures_companyAccounts']/section[1]/div[5]/table/tbody/tr[1]/td[1]"))).text

            result = {
                'employees': employees,
                'established': established,
                'pubyear': pubyear,
                'roi': roi,
                'liquidityratio': liquidityratio,
                'solvencyratio': solvencyratio,
                'netturnover': netturnover,
                'grossprofit': grossprofit,
                'equity': equity,
                'netresult': netresult,
                'currency': currency
            }

            return result
        
        return None
