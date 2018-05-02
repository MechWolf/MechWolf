from OpenSSL import crypto, SSL

# modified from https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python

CERT_FILE = "ssl.cert"
KEY_FILE = "ssl.key"

def create_self_signed_cert():

	# create a key pair
	k = crypto.PKey()
	k.generate_key(crypto.TYPE_RSA, 4096)

	# create a self-signed cert
	cert = crypto.X509()
	cert.get_subject().C = "US"
	cert.get_subject().ST = "Massachussets"
	cert.get_subject().L = "Cambridge"
	cert.get_subject().O = "MechWolf"
	cert.get_subject().OU = "MechWolf"
	cert.get_subject().CN = gethostname()
	cert.set_serial_number(1636)
	cert.gmtime_adj_notBefore(0)
	cert.gmtime_adj_notAfter(10*365*24*60*60)
	cert.set_issuer(cert.get_subject())
	cert.set_pubkey(k)
	cert.sign(k, 'sha256')

	open(CERT_FILE, "wt").write(
		crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode())
	open(KEY_FILE, "wt").write(
		crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode())
