#!/usr/bin/env bash

# Read properties from cert.properties file
PROP_FILE=cert.properties

# Function to read property values
function prop {
    grep "${1}=" ${PROP_FILE} | cut -d'=' -f2
}

# Assigning property values to variables
partner_name=$(prop 'partner_name')
country=$(prop 'country')
state=$(prop 'state')
locality=$(prop 'locality')
organisation=$(prop 'organisation')
email_id=$(prop 'email_id')
common_name=$(prop 'common_name')
keystore_password=$(prop 'keystore_password')
daysCA=$(prop 'CAcertvalidityperiod')
daysPartner=$(prop 'Partnercertvalidityperiod')
echo "$partner_name is the name of the partner."

echo "$keystore_password" > key.pwd

# Using current working directory
path=$(pwd)
cert_path=$path/certs/$partner_name
echo $cert_path

# Check if the directory already exists
if [ -d "$cert_path" ]; then
    echo "Directory $cert_path already exists. Skipping cert creation."
    exit 0
else
    mkdir -p $cert_path
fi

# Create root-openssl.cnf
root_openssl_cnf="$cert_path/root-openssl.cnf"
cat > $root_openssl_cnf <<EOL
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = $country
ST = $state
L = $locality
O = $organisation
CN = $common_name-Root
[v3_req]
keyUsage = critical, digitalSignature, keyAgreement
extendedKeyUsage = serverAuth
basicConstraints = critical, CA:true
EOL

# Create client-openssl.cnf
client_openssl_cnf="$cert_path/client-openssl.cnf"
cat > $client_openssl_cnf <<EOL
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = $country
ST = $state
L = $locality
O = $organisation
CN = $common_name-Client
[v3_req]
# Extensions for client certificates (\`man x509v3_config\`).
basicConstraints = CA:FALSE
nsCertType = objsign
nsComment = "OpenSSL Generated Client Certificate"
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer
keyUsage = critical, nonRepudiation, digitalSignature, keyEncipherment
EOL

echo "OpenSSL configuration files written to $cert_path"

echo "==================== Creating CA certificate"
openssl genrsa -out $cert_path/RootCA.key 2048
openssl req -x509 -new -key $cert_path/RootCA.key -sha256 -days $daysCA -out $cert_path/RootCA.pem -config $root_openssl_cnf

echo "==================== Creating partner certificate"
openssl genrsa -out $cert_path/Client.key 2048
openssl req -new -key $cert_path/Client.key -out $cert_path/Client.csr -config $client_openssl_cnf
openssl x509 -req -days $daysPartner -extensions v3_req -extfile $client_openssl_cnf -in $cert_path/Client.csr -CA $cert_path/RootCA.pem -CAkey $cert_path/RootCA.key -CAcreateserial -out $cert_path/Client.pem

openssl pkcs12 -export -in $cert_path/Client.pem -inkey $cert_path/Client.key -out $cert_path/keystore.p12 -name $partner_name -password pass:$keystore_password

echo "Cert generation complete"

# Conversion to JWK
echo "Converting certificate to JWK"

CERTIFICATE_FILE=$cert_path/Client.pem

# Extract the public key from the certificate in PEM format
openssl x509 -in "${CERTIFICATE_FILE}" -pubkey -noout > $cert_path/pubkey.pem

# Convert the PEM public key to JWK format using the pem-jwk tool
npm install -g pem-jwk
pem-jwk $cert_path/pubkey.pem > $cert_path/pubkey.jwk

# Output the resulting JWK to the console
cat $cert_path/pubkey.jwk
rm $cert_path/pubkey.pem
rm ./key.pwd