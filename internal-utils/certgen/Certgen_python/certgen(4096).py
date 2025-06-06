import os
import subprocess
from configparser import ConfigParser
import json
from jwcrypto import jwk

# Read properties from cert.properties file
PROP_FILE = 'cert.properties'
config = ConfigParser()
config.read(PROP_FILE)

partner_name = config.get('DEFAULT', 'partner_name')
country = config.get('DEFAULT', 'country')
state = config.get('DEFAULT', 'state')
locality = config.get('DEFAULT', 'locality')
organisation = config.get('DEFAULT', 'organisation')
email_id = config.get('DEFAULT', 'email_id')
common_name = config.get('DEFAULT', 'common_name')
keystore_password = config.get('DEFAULT', 'keystore_password')
daysCA = config.get('DEFAULT', 'daysCA')
daysPartner = config.get('DEFAULT', 'daysPartner')

print(f"{partner_name} is the name of the partner.")

# Using current working directory
path = os.getcwd()
cert_path = os.path.join(path, 'certs', partner_name)
print(cert_path)

# Check if the directory already exists
if not os.path.exists(cert_path):
    os.makedirs(cert_path)
else:
    print(f"Directory {cert_path} already exists. Skipping cert creation.")
    exit(0)

# Create root-openssl.cnf
root_openssl_cnf = os.path.join(cert_path, 'root-openssl.cnf')
with open(root_openssl_cnf, 'w') as f:
    f.write(f"""
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = {country}
ST = {state}
L = {locality}
O = {organisation}
CN = {common_name}-Root
[v3_req]
keyUsage = critical, digitalSignature, keyAgreement
extendedKeyUsage = serverAuth
basicConstraints = critical, CA:true
""")

# Create client-openssl.cnf
client_openssl_cnf = os.path.join(cert_path, 'client-openssl.cnf')
with open(client_openssl_cnf, 'w') as f:
    f.write(f"""
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = {country}
ST = {state}
L = {locality}
O = {organisation}
CN = TESTUNIT-{partner_name}
[v3_req]
# Extensions for client certificates (`man x509v3_config`).
basicConstraints = CA:FALSE
nsCertType = objsign
nsComment = "OpenSSL Generated Client Certificate"
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer
keyUsage = critical, nonRepudiation, digitalSignature, keyEncipherment
""")

print(f"OpenSSL configuration files written to {cert_path}")

print("==================== Creating CA certificate")
subprocess.run(['openssl', 'genrsa', '-out', os.path.join(cert_path, 'RootCA.key'), '4096'])
subprocess.run(['openssl', 'req', '-x509', '-new', '-key', os.path.join(cert_path, 'RootCA.key'), '-sha256', '-days', daysCA, '-out', os.path.join(cert_path, 'RootCA.pem'), '-config', root_openssl_cnf])

print("==================== Creating partner certificate")
subprocess.run(['openssl', 'genrsa', '-out', os.path.join(cert_path, 'Client.key'), '4096'])
subprocess.run(['openssl', 'req', '-new', '-key', os.path.join(cert_path, 'Client.key'), '-out', os.path.join(cert_path, 'Client.csr'), '-config', client_openssl_cnf])
subprocess.run(['openssl', 'x509', '-req', '-days', daysPartner, '-extensions', 'v3_req', '-extfile', client_openssl_cnf, '-in', os.path.join(cert_path, 'Client.csr'), '-CA', os.path.join(cert_path, 'RootCA.pem'), '-CAkey', os.path.join(cert_path, 'RootCA.key'), '-CAcreateserial', '-out', os.path.join(cert_path, 'Client.pem')])

subprocess.run(['openssl', 'pkcs12', '-export', '-in', os.path.join(cert_path, 'Client.pem'), '-inkey', os.path.join(cert_path, 'Client.key'), '-out', os.path.join(cert_path, 'keystore.p12'), '-name', partner_name, '-password', f'pass:{keystore_password}'])

print("Cert generation complete")

# Conversion to JWK
print("Converting certificate to JWK")

CERTIFICATE_FILE = os.path.join(cert_path, 'Client.pem')

# Extract the public key from the certificate in PEM format
pubkey_pem = subprocess.check_output(['openssl', 'x509', '-in', CERTIFICATE_FILE, '-pubkey', '-noout'])

# Convert the PEM public key to JWK format
public_key = pubkey_pem.decode('utf-8').encode('ascii')
jwk_key = jwk.JWK.from_pem(public_key)
jwk_json = jwk_key.export(as_dict=True)

with open(os.path.join(cert_path, 'pubkey.jwk'), 'w') as jwk_file:
    json.dump(jwk_json, jwk_file, indent=4)

print("JWK conversion complete")
