## Guide to use certificate generator (For Testing purposes only)

1. The user must download the zip file in whole and extract the files
2. The user only needs to update the cert.properties 
3. The partner name has to be changed before each use as the script doesn't create duplicate certificates.
4. All other variables can also be changed as per user requirement.
5. The daysCA and daysPartner variables control the number of days the certs will be valid for and daysCA must always be higher than daysPartner.

HOW TO EXECUTE

1. Make sure following libraries are installed 
   pem 
   jwcrypto
   configparser
   ####They can all be installed using cmd pip install pem jwcrypto configparser

2. Make sure the changes in cert.properties is made and saved.
3. Use python3 certgen.py to run the script. 
4. You can collect the RootCA.pem and CLient.pem & p12 and the jwk public key from the file named after your partner.
