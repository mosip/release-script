# Generating certificates and publickey (jwk ) with certgen script
Note: This guide intends to use the "certgen script " in test use/scenarios only.

## Downloading certgen and editing the configuration file (cert.properties) before you run/execute the certgen script
- Download the certgen.zip (for Windows only(git bash installment needed) in whole and extract the files. (Once you extract the files you will need to make few changes with the configuration file i.e. "cert.properties" file).
    - In the `cert.properties` file change the `partnername` before every use (as the script will not create duplicate certificates and exit).
    - You can also change other variables such as `country, state, locality` as you may need.
-  The `CAcertvalidityperiod` and `Partnercertvalidityperiod` variables controls the number of days the CA cert and partner certs will be valid for and value for `CAcertvalidityperiod` must always be higher than or equal to that of `Partnercertvalidityperiod`.

### Windows
The certgen archive file (zip) you downloaded contains the sh file you can run. 

Note: Make sure the changes in `cert.properties` is made and saved (As explained in steps above).

**To Execute**
-  run ./certgen.sh

**Results**

You can collect the p12 and the jwk public key from the file named after your partnername inside certs folder.
