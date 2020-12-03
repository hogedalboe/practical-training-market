import psycopg2
import pandas
import numpy
import datetime

import objects
import config

db = objects.Database(config.server, config.database, config.user, config.password)

# Get approvals and limitations in database.
dfApprovals = db.Read("SELECT * FROM approval")
dfLimits = db.Read("SELECT * FROM limits")

# List of limitation codes implying approval overlap.
overlapLimits = ['1128', '1129', '1421']

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

        # Only relevant to accumulate if the production unit has more than one approval within the education.
        if len(temp_dfApprovals.index) > 1:

            # Handle approvals with limitations implying overlap.
            if len(temp_dfLimits.index) > 0:

                employed = 0
                highest = 0

                for j, row_temp in temp_dfApprovals.iterrows():
                    # Accumulate the number of employed students.
                    employed += row_temp['currentamount']

                    # The approval with the highest amount of allowed students within a production unit's overlapping approvals is the true amount.
                    if row_temp['approvalamount'] > highest:
                        highest = row_temp['approvalamount']
                
                dfCombinedApprovals.loc[len(dfCombinedApprovals)] = [row_orig['edunum'], row_orig['pnum'], highest, employed]

            # No limitations implying overlap.
            else:
                # Combine by accumulation of values if there's more than one approval within an education for the production unit.
                # A pitfall might be, that some approvals, without limitation codes implying any overlap, are in fact overlapping, thereby resulting in incorrecty high approval amounts for some production units.
                # It was not possible to find a durable procedure to account for these unregistered overlaps, and it will have to suffice to simply accumulate approvalamount and currentamount values.
                pass


        # Otherwise just let the one approval cover the whole education and add it to the dataframe for the combined approvals.
        else:
            dfCombinedApprovals.loc[len(dfCombinedApprovals)] = [row_orig['edunum'], row_orig['pnum'], row_orig['approvalamount'], row_orig['currentamount']]

        handled.append(str(row_orig['pnum'])+str(row_orig['edunum']))

dfCombinedApprovals.sort_values('pnum')
print(dfCombinedApprovals.head(98))

input("stop")







