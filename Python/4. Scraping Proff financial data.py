import pandas
import numpy
import time

import config
import objects

db = objects.Database(config.server, config.database, config.user, config.password)

logger = objects.Logger()

# Get companies from the database
dfCompanies = db.Read("SELECT * FROM company")

# Target amount of companies.
target = len(dfCompanies.index)

# Get Chrome ready for scraping.
scraper = objects.ProffScraper()

# Get previous scrapings and amount.
def previousScrapings():
    previous = []
    with open(config.file_financials, 'r+') as f:
        previous = f.readlines()
    return previous

previous = previousScrapings()
count = len(previous)-1

# Function to determine if substring is in a list of strings.
def substringInList(substring, listOfStrings):
    for item in listOfStrings:
        if substring in item:
            return True
    return False

# Avoid duplicates.
scraped = []

# Scrape.
for i, row in dfCompanies.iterrows():
    try:
        cvr = str(row['cvrnum'])

        if not substringInList(cvr, previous):
            if cvr not in scraped:
                # Scrape
                result = scraper.scrape(cvr)

                if result != None:
                    # Parse result to a csv row.
                    csv_row = "{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};\n".format(
                        cvr, 
                        result['employees'], 
                        result['established'], 
                        result['pubyear'], 
                        result['liquidityratio'], 
                        result['roi'], 
                        result['solvencyratio'], 
                        result['netturnover'], 
                        result['grossprofit'], 
                        result['equity'],
                        result['netresult'],
                        result['currency'],
                        )

                    # Append result to file.
                    with open(config.file_financials, 'a') as f:
                        f.write(csv_row)

                    # Implement rate limit.
                    time.sleep(config.ratelimit)

                    # Clear fields.
                    scraper.initiate()

                    # Avoid duplicates.
                    scraped.append(cvr)

                    # Show progress.
                    count += 1
                    print("{0} / {1}".format(str(count),str(target)))
            
    except Exception as e:
        logger.log(str(e))
        print(str(e))
        time.sleep(2)
        scraper.reset()
        previous = previousScrapings()
    

