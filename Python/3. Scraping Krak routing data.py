import pandas
import numpy
import time

import config
import objects

db = objects.Database(config.server, config.database, config.user, config.password)

logger = objects.Logger()

# Get addresses for school facilities and production units.
dfProductionUnits = db.Read("SELECT * FROM productionunit")
dfFacilities = db.Read("SELECT * FROM facility")

# Reverse the dataframes (only used to toggle iteration direction).
dfProductionUnits = dfProductionUnits.iloc[::-1]
dfFacilities = dfFacilities.iloc[::-1]

# Target amount of distances.
target = len(dfProductionUnits['postalcode'].unique())*len(dfFacilities.index)

# Get Chrome ready for scraping.
scraper = objects.KrakScraper()

## Iterate and scrape school facility addresses to identify issues (live visual inspection or validation via the log file).
#inspectionIterated = []
#for j, row_fac in dfFacilities.iterrows():
#    origin = "Middelfart Station" # Random address.
#    destination = "{0} {1}, {2} {3}".format(row_fac['street'], row_fac['streetnumber'], str(row_fac['postalcode']), row_fac['city'])
#
#    if not destination in inspectionIterated:
#        inspectionIterated.append(destination)
#        try:
#            result = scraper.scrape(origin, destination)
#            time.sleep(1)
#            scraper.initiate()
#            time.sleep(1)
#        except:
#            time.sleep(1)
#            scraper.initiate()
#            with open(config.distances_facility_issue, 'a') as f:
#                f.write(destination + "\n")
#
#input("Press any button to begin scraping...")

# Get previous scrapings and amount.
def previousScrapings():
    previous = []
    with open(config.file_distances, 'r+') as f:
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

# City name corrections.
correction = {}

# Scrape.
for i, row_pu in dfProductionUnits.iterrows():

    postal_pu = str(row_pu['postalcode'])
    city_pu = str(row_pu['city'])

    # Use previous city name correction.
    if postal_pu in correction:
        city_pu = correction[postal_pu]

    for j, row_fac in dfFacilities.iterrows():
        facilityid = str(row_fac['id'])

        csvStr = "{0};{1};{2};".format(postal_pu, city_pu, facilityid)

        try:
            if not substringInList(csvStr, previous):
                if csvStr not in scraped:

                    retry = True
                    attempts = 0

                    while retry:
                        try:
                            # Get distance and duration.
                            origin = "{0} {1}".format(postal_pu, city_pu)
                            destination = "{0} {1}, {2} {3}".format(row_fac['street'], row_fac['streetnumber'], str(row_fac['postalcode']), row_fac['city'])

                            result = scraper.scrape(origin, destination)

                            csv_row_result = "{0};{1};{2};{3};{4};{5}\n".format(postal_pu, city_pu, facilityid, result[0], result[1], result[2])

                            # Append result to file.
                            with open(config.file_distances, 'a') as f:
                                f.write(csv_row_result)
                            
                            # Avoid duplicates.
                            scraped.append(csvStr)

                            # Implement rate limit.
                            time.sleep(1)

                            # Clear fields.
                            scraper.initiate()

                            # Show progress.
                            count += 1
                            print("{0} / {1}".format(str(count),str(target)))

                            # Do not retry.
                            retry = False

                        except:
                            # If the scrape fails, it might be due to incorrect city spelling. Get the correct city name from the postal area table in the database and try again.
                            realCity = db.Read("SELECT city FROM postalarea WHERE postalcode = {0}".format(postal_pu))
                            if not realCity.empty:
                                if not postal_pu in correction:
                                
                                    newCity = realCity['city'].iloc[0]
                                    correctionInfo = "{0} was corrected to {1} (postal area code: {2})".format(city_pu, newCity, postal_pu)
                                    print(correctionInfo)
                                    logger.log(correctionInfo)
                                    city_pu = newCity
                                    correction[postal_pu] = city_pu

                            if attempts > 1:
                                retry = False

                            scraper.initiate()
                            
                            attempts += 1

        except Exception as e:
            logger.log(str(e))
            time.sleep(2)
            scraper.reset()
            previous = previousScrapings()

