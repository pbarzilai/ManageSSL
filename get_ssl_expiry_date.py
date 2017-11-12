#! /usr/bin/env python

import socket
from OpenSSL import SSL
import datetime
import psycopg2
from config import config

def ssl_expiry_date():

	try:	
		params = config()
		conn_sql = psycopg2.connect(**params)
		cur = conn_sql.cursor()
		cur.execute('SELECT hostname FROM ssl')
		for hostname in cur:
			try:
				cur = conn_sql.cursor()
				hostname = str(''.join(hostname))

				context = SSL.Context(SSL.TLSv1_METHOD)
				sock = socket.socket()
				sock = SSL.Connection(context, sock)
				sock.connect((hostname, 443))
				sock.do_handshake()
				x509 = sock.get_peer_certificate()
				x509notAfter = x509.get_notAfter()
				ssldate_format = r'%Y%m%d%H%M%SZ'
				d = datetime.datetime.strptime(x509notAfter, ssldate_format)
				expirydate = d.strftime('%Y-%m-%d')
				
				query = "UPDATE ssl SET SSL_EXPIRY = %s where HOSTNAME = %s"
				data = (expirydate, hostname)
				cur.execute(query, data)
				conn_sql.commit()
				sock.close()
			except psycopg2.ProgrammingError as e:
				pass
	except psycopg2.ProgrammingError as e:
		print e
	cur.close()
	conn_sql.close()
	
def main():
	ssl_expiry_date()
	
if __name__ == "__main__":
	main()
