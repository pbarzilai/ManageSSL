#! /usr/bin/env python

import psycopg2
from config import config
import pycurl
import cStringIO
import datetime

def ssl_option():

	try:	
		params = config()
		conn_sql = psycopg2.connect(**params)
		cur = conn_sql.cursor()
		cur.execute('SELECT hostname FROM sites_full order by id')
		#cur.execute('SELECT hostname FROM sites_full where id = 26')
		for hostname in cur:
			#print hostname
			try:
				cur = conn_sql.cursor()
				hostname = str(''.join(hostname))
				#print hostname
				curl = pycurl.Curl()
				buff = cStringIO.StringIO()
				curl.setopt(pycurl.URL, 'https://'+hostname)
				curl.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36')
				curl.setopt(pycurl.FOLLOWLOCATION, 1)
				curl.setopt(pycurl.WRITEFUNCTION, buff.write)
				curl.setopt(pycurl.SSL_VERIFYPEER, 0)
				curl.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_TLSv1_0)
				curl.setopt(pycurl.OPT_CERTINFO, 1)
				curl.perform()

				certinfo = curl.getinfo(pycurl.INFO_CERTINFO)
				certinfo = certinfo[0]
				certinfo_dict = {}
				for entry in certinfo:
					certinfo_dict[entry[0]] = entry[1]
				x = certinfo_dict['X509v3 Subject Alternative Name']
				ssldate_format = r'%b %d %H:%M:%S %Y %Z'
				d = datetime.datetime.strptime(certinfo_dict['Expire date'], ssldate_format)
				expirydate = d.strftime('%Y-%m-%d')
				if hostname in str(x):
					query = "UPDATE sites_full SET ssl = %s, ssl_expiry = %s where HOSTNAME = %s"
					data = ('true', expirydate, hostname)
					cur.execute(query, data)
					conn_sql.commit()
				else:
					#print hostname + ' ' + str(x)
					pass
			except (psycopg2.ProgrammingError, IndexError) as e:
				#print hostname + ' ' + str(e)
				pass
			except pycurl.error as e2:
				#print hostname + ' ' + str(e2)
				pass
	except psycopg2.ProgrammingError as e3:
		#print e3
		pass
	cur.close()
	conn_sql.close()
	
def main():
	ssl_option()
	
if __name__ == "__main__":
	main()
