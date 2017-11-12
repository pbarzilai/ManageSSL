#! /usr/bin/env python

import socket
from OpenSSL import SSL
import psycopg2
from config import config

def ssl_option():

	try:	
		params = config()
		conn_sql = psycopg2.connect(**params)
		cur = conn_sql.cursor()
		cur.execute('SELECT hostname FROM sites_full order by id')
		#cur.execute('SELECT hostname FROM sites_full where id = 132')
		for hostname in cur:
			#print hostname
			try:
				cur = conn_sql.cursor()
				hostname = str(''.join(hostname))

				context = SSL.Context(SSL.TLSv1_METHOD)
				sock = socket.socket()
				sock = SSL.Connection(context, sock)
				sock.connect((hostname, 443))
				sock.do_handshake()
				x509 = sock.get_peer_certificate()
				x = x509.get_subject()
				if hostname in str(x):
					query = "UPDATE sites_full SET SSL = %s where HOSTNAME = %s"
					data = ('true', hostname)
					cur.execute(query, data)
					conn_sql.commit()
					sock.close()
				else:
					#print hostname + ' ' + str(x)
					sock.close()
			except (psycopg2.ProgrammingError, SSL.SysCallError, SSL.Error, socket.error) as e:
				print hostname + ' ' + str(e)
				pass
	except psycopg2.ProgrammingError as e:
		#print e
		pass
	cur.close()
	conn_sql.close()
	
def main():
	ssl_option()
	
if __name__ == "__main__":
	main()
