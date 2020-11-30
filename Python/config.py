import os

cwd = os.path.dirname(__file__)

# Database.
server = "localhost"
database = "practicaltrainingmarket"
user = "postgres"
password = "Bavian2018*"

# File paths.
file_log = os.path.join(cwd, 'scrapedata', 'log.txt')
file_distances = os.path.join(cwd, 'scrapedata', 'distances.txt')
distances_facility_issue = os.path.join(cwd, 'scrapedata', 'distances_facility_issue.txt')
file_financials = os.path.join(cwd, 'scrapedata', 'financials.txt')

# Scraping.
defaultTimeout = 5
ratelimit = 1
chromedriverPath = os.path.join(cwd, 'chromedriver.exe')
url_Krak = "https://map.krak.dk/?mode=route"
url_Proff_base = "https://proff.dk/"