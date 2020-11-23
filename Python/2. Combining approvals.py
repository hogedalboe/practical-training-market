import psycopg2
import pandas
import numpy
import datetime

import objects
import config

db = objects.Database(config.server, config.database, config.user, config.password)

################################################################################################################################

# List of limitation codes implying approval overlap.
overlapLimits = ['1128', '1129', '1421']

# Get approvals and limitations in database.
dfApprovals = db.Read("SELECT * FROM approval")
dfLimits = db.Read("SELECT * FROM limits")

# Prepare new dataframe to be populated to database table 'CombinedApproval'.
dfCombinedApprovals = pandas.DataFrame(columns=['edunum', 'pnum', 'approvalamount', 'currentamount'])

# Avoid handling the same production unit more than once.
handled = []

# Combine approvals by production unit and education.
for i, row_orig in dfApprovals.iterrows():

    if str(row_orig['pnum'])+str(row_orig['edunum'])  not in handled:

        # Get the limitations relevant to the production unit and education.
        temp_dfLimits = dfLimits.loc[(dfLimits['pnum'] == row_orig['pnum']) & (dfLimits['edunum'] == row_orig['edunum'])]
        temp_dfLimits = temp_dfLimits[temp_dfLimits['limitationcode'].isin(overlapLimits)]

        # Find other approvals for the same production unit and education.
        temp_dfApprovals = dfApprovals.loc[(dfApprovals['pnum'] == row_orig['pnum']) & (dfApprovals['edunum'] == row_orig['edunum'])]

        # Handle approvals with limitations implying overlap.
        if len(temp_dfLimits.index) > 0:

            # Only relevant if more than one approval within the education.
            if len(temp_dfApprovals.index) > 1:

                employed = 0
                highest = 0

                for j, row_temp in temp_dfApprovals.iterrows():
                    # Accumulate to number of employed students.
                    employed += row_temp['currentamount']

                    # The approval with the highest amount of allowed students within a production unit's overlapping approvals is the true amount.
                    if row_temp['approvalamount'] > highest:
                        highest = row_temp['approvalamount']
                
                dfCombinedApprovals.loc[len(dfCombinedApprovals)] = [row_orig['edunum'], row_orig['pnum'], highest, employed]

            # Otherwise just let the one approval cover the whole education and add it to the dataframe for the combined approvals.
            else:
                dfCombinedApprovals.loc[len(dfCombinedApprovals)] = [row_orig['edunum'], row_orig['pnum'], row_orig['approvalamount'], row_orig['currentamount']]

        # No limitations implying overlap.
        else:
            # Combine by accumulation of values if there's more than one approval within an education for the production unit.
            pass

        handled.append(str(row_orig['pnum'])+str(row_orig['edunum']))

print(dfCombinedApprovals.head(60))


















################################################################################################################################
################################################################################################################################
###################################################### DELETE ##################################################################
################################################################################################################################
################################################################################################################################ Removing approvals with certain limitation codes (cascading removal of limitation relationships)

# Limitation codes causing removal:
#	1141 2 pr. år
#	1152 Overlap max. 12 mdr.
#	1158 Overlap max. 18 mdr.
#	1159 Overlap max 24 mdr.
#	1161 Min. 1 år imellem
#	1162 Min. 1,5 år imellem
#	1164 Ny efter 1/2 læretid
#	1204 Max 3 mdr. dette sted
#	1206 Max 6 mdr. dette sted
#	1209 Max 9 mdr. dette sted
#	1212 Max 12 mdr. dette sted
#	1225 Max 24 mdr. dette sted
#	1230 Max 1/2 læretid her
#	1096 Kun til FGU
#	1097 Kun til VFU (virksomhedsforlagt undervisning, SKP)
#	1100 Gælder et specifikt uddannelsesforhold

limitations = [1141, 1152, 1158, 1159, 1161, 1162, 1164, 1204, 1206, 1209, 1212, 1225, 1230, 1096, 1097, 1100]

# Getting limitation relationships in the database.
dfLimits = db.Read("SELECT * FROM limits")

# Keeping track of limitation relationships to be removed (because the corresponding approval will be removed).
LimitsToRemove = []

# Keeping track of which companies and production units are affected by the removal of an approval.
companiesAffected = []
productionUnitsAffected = []

# Companies and production units no longer represented in the approval table.
companiesToDelete = []
productionUnitsToDelete = []

countLimitationsCauseForRemoval = 0

# Iterating limitation relationships and determining whether it should be removed.
for index, row in dfLimits.iterrows():
    if row['limitationcode'] in limitations:
        countLimitationsCauseForRemoval += 1
        print(str(countLimitationsCauseForRemoval))









################################################################################################################################ Remove production units that no longer have any relations with an approval












################################################################################################################################ Remove companies that no longer have any relations with a production unit