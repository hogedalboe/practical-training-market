import psycopg2
import pandas
import numpy
import datetime

import objects
import config

db = objects.Database(config.server, config.database, config.user, config.password)

# Prepare new dataframe to be populated to database table 'CombinedApproval'.
df_Nearest = pandas.DataFrame(columns=['edunum', 'pnum', 'nearestfacilitykm', 'nearestfacilityminutes'])

############################################################################################################################################## Identify shortest routes

df_CombinedApprovalPostalCodes = db.Read(
    """
    SELECT combinedapproval.pnum, combinedapproval.edunum, productionunit.postalcode
	FROM combinedapproval
	LEFT JOIN productionunit
		ON productionunit.pnum = combinedapproval.pnum
    """
)

df_Facilities = db.Read("SELECT id, edunum, postalcode FROM facility")

df_Distances = db.Read("SELECT postalcode, facilityid, km, hours, minutes FROM distance")

df_PostalAreas = db.Read("SELECT postalcode, municipalitycode FROM postalarea")

# Postal areas with missing route data.
missing = []
substitutes = []

# Postal areas which have not been substituted.
unsubstituted = []

def FindRoutes(edunum, pnum, postalcode):
    # Match facilities on education.
    df_MatchingFacilities = df_Facilities.loc[df_Facilities['edunum'] == edunum]
    #print("Matching facilities for combined approval (education '{0}' / production unit '{1}' / postal code '{2}'):\n{3}\n".format(str(edunum), pnum, postalcode, str(df_MatchingFacilities.head(5))))

    # Get distances which contain the matching facility ids and the postal code of the production unit.
    df_MatchingDistances = df_Distances.loc[(df_Distances['facilityid'].isin(df_MatchingFacilities['id'])) & (df_Distances['postalcode'] == postalcode)]
    #print("Distances between the postal area of the approved production unit and the relevant school facilities (matching education):\n{0}\n".format(str(df_MatchingDistances.head(5))))

    return df_MatchingDistances

# Iterate the postal area codes of the combined approvals to determine closest school facility within same education.
for i, approval in df_CombinedApprovalPostalCodes.iterrows():

    postalcode = approval['postalcode']
    
    df_Routes = FindRoutes(approval['edunum'], approval['pnum'], postalcode)

    # If no routes have been found, then try to match on the nearest other postal area instead.
    if not len(df_Routes.index) > 0:

        # Get the municipality code of the original postal code.
        municipalitycode = df_PostalAreas[df_PostalAreas['postalcode'] == postalcode].iloc[0]['municipalitycode']

        # Get a list of all postal codes within the same municipality as the current production unit and remove the current postal code to avoid using it as substitute (for itself).
        postalCodes = df_PostalAreas[df_PostalAreas['municipalitycode'] == municipalitycode]['postalcode'].tolist()
        postalCodes.remove(postalcode)

        substitute = None
        while substitute == None:

            try:
                # Get the nearest postal area code.
                potentialSubstitute = min(postalCodes, key=lambda x:abs(x-postalcode))

                # Search for routes with the substitue postal code.
                df_Routes = FindRoutes(approval['edunum'], approval['pnum'], potentialSubstitute)

                # Check that routes exist.
                if len(df_Routes.index) > 0:
                    substitute = potentialSubstitute

                # Remove the potential substitute postal code from list.
                postalCodes.remove(potentialSubstitute)

            except:
                print("Exception was thrown while trying to find substitute postal code for (pnum, edunum, postalcode, municipalitycode)=({0}, {1}, {2}, {3})".format(approval['pnum'], approval['edunum'], postalcode, municipalitycode))

                # Attempt to find another route outside the municipality of the current production unit.
                postalCodes = df_PostalAreas['postalcode'].tolist()
                postalCodes.remove(postalcode)

        # Add missing postal area and its substitue to list.
        if postalcode not in missing:
            missing.append(postalcode)
            substitutes.append(substitute)
            print("No routes found for the postal area code '{0}'. It was substituted for postal area code '{1}'".format(str(postalcode), str(substitute)))

        # Use the substituted postal code.
        postalcode = substitute

    else:
        if postalcode not in unsubstituted:
            unsubstituted.append(postalcode)
    
    # Find the shortest route.
    shortestRouteKm = df_Routes[df_Routes['km'] == df_Routes['km'].min()].iloc[0]['km']
    #print("The shortest route is {0} km.".format(str(shortestRouteKm)))

    # Find the shortest travel time in minutes.
    df_shortestRouteHours = df_Routes[df_Routes['hours'] == df_Routes['hours'].min()]
    result_shortestRouteMinutes = df_shortestRouteHours[df_shortestRouteHours['minutes'] == df_shortestRouteHours['minutes'].min()].iloc[0]['minutes']
    shortestRouteHours = df_shortestRouteHours.iloc[0]['hours']
    shortestRouteMinutes = (shortestRouteHours*60) + result_shortestRouteMinutes
    #print("The route with the shortes travel time (by car) is {0} minutes.".format(str(shortestRouteMinutes)))

    # Write the route to the prepared dataframe for later database insertion.
    df_Nearest.loc[len(df_Nearest)] = [approval['edunum'], approval['pnum'], shortestRouteKm, shortestRouteMinutes]

# Inform of postal areas which it has not been able to scrape distances for.
if len(missing) > 0:
    print("In total, {0} postal areas could not be located in the Krak mapping service.\n".format(str(len(missing))))
    print('original;substitue')
    for i, postalcode in enumerate(missing):
        print(str(postalcode) + ";" + str(substitutes[i]))

print(str(len(unsubstituted)) + " postal codes vere unsubstituted.")

############################################################################################################################################## Remove routes with unrealistic travel times

print("The mean travel distance is {0} km.".format(str(df_Nearest['nearestfacilitykm'].mean())))
print("The mean travel time is {0} minutes.".format(str(df_Nearest['nearestfacilityminutes'].mean())))

# Determine how many minutes it takes to drive a kilometer in each route.
df_Nearest['minutesPerKm'] = df_Nearest["nearestfacilityminutes"] / df_Nearest['nearestfacilitykm']
print("The longest travel times are:\n{0}\n".format(df_Nearest.sort_values(['minutesPerKm'], ascending=False).head(70)))
print("The shortest travel times are:\n{0}\n".format(df_Nearest.sort_values(['minutesPerKm'], ascending=True).head(70)))

# Determine minimum and maximum travel distances.
print("The longest travel distances are:\n{0}\n".format(df_Nearest.sort_values(['nearestfacilitykm'], ascending=False).head(5)))
print("The shortes travel distances are:\n{0}\n".format(df_Nearest.sort_values(['nearestfacilitykm'], ascending=True).head(5)))

############################################################################################################################################## Insert routes in the database

# Chunk size limit of the database (no more than 1000 observation should be inserted at once).
chunkLimit = 500
count = 0

# iterate routes and write them to the database (travel time in minutes is ignored due to authenticity concerns and unrealistic values).
for i, distance in df_Nearest.iterrows():

    # Insert route in database.
    sql = """UPDATE combinedapproval SET nearestfacilitykm = {0} WHERE edunum = {1} AND pnum = {2}""".format(
        distance['nearestfacilitykm'],
        distance['edunum'],
        distance['pnum']
    )

    print(sql)
    db.Insert(sql)

    # Manage insertion chunk sizes.
    count += 1

    # Commit every n queries.
    if count > chunkLimit:
        db.Commit()
        count = 0

db.Commit()

# Delete distances in the database where nearest facility is more than 800 km away (unrealistic distance in Denmark).
input("Press any key to delete combined approvals in the database where the nearest facility is more than 800 km away...")
db.Insert("""DELETE FROM combinedapproval WHERE nearestfacilitykm > 800""")
db.Commit()

################################################################################################################################ Disconnect database

db.Disconnect()










