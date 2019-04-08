# fv-legacy-validation
Validates that all data from legacy site has been correctly transferred to the new site.  Gathers and compares data from the FirstVoices legacy database and the new site.  Then creates csv reports listing the amount of data on the new site compared to the legacy site, discrepencies between the site data, and any items that are missing required fields.  It can also upload these reports to nuxeo as well as export csvs of data from the legacy database for each dialect.


## Setup ##
To use, the computer running the program must be able to access the FirstVoices legacy database.

To allow access to the legacy database and nuxeo, create a python file called authorization.py in the src directory which follows the format below, filling in the correct access information.

```
from nuxeo.client import Nuxeo
import cx_Oracle


class Authorize:

    nuxeoUser = ""
    nuxeoPassword = ""
    nuxeoUrl = ""
    legacyUser = ""
    legacyPassword = ""
    legacyUrl = ""  # in the format "@host:port/database"
    nuxeo = Nuxeo(host=nuxeoUrl, auth=(nuxeoUser, nuxeoPassword))
    connection = cx_Oracle.connect(legacyUser+'/'+legacyPassword+legacyUrl)
    cursor = cur = connection.cursor()
    
```

## Running it ##
The main program is run from the file LegacyValidator.  In main(), you can input the legacy ids and names of specific dialects to be validated or let the legacy database query the dialects. 
