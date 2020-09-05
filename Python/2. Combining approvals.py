import psycopg2
import pandas
import numpy
import datetime

import objects
import config

db = objects.Database(config.server, config.database, config.user, config.password)

################################################################################################################################






















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