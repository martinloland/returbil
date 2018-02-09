# -*- coding: utf-8 -*-
import requests
import time
from datetime import datetime, timezone, timedelta
import time
import re
from bs4 import BeautifulSoup
import collections
import smtplib
import os.path
import pickle
from .private import send_to_email, send_from_email, server_username, server_pwd

Tur = collections.namedtuple('Tur', ('ref', 'dato', 'fra', 'til'))
link = 'http://returbil.no/freecar.asp'
treff = []

def main():
	load_from_file()

	while True:
		scrape()
		log_add_line(current_state())
		time.sleep(240)

def load_from_file():
	global treff
	if os.path.isfile('database.pickle'):
		with open('database.pickle', 'rb') as f:
			treff = pickle.load(f)
			print("Loaded results from file")

def save_to_file():
	with open('database.pickle', 'wb') as f:
		pickle.dump(treff, f, pickle.HIGHEST_PROTOCOL)
		print("Saved results to file")

def log_add_line(text):
	with open('log.txt', 'a+') as f:
		f.write(text+"\r\n")

def current_state():
	delta = timedelta(seconds=60*60*2) #Two hours
	return str(datetime.now(timezone.utc)+delta)+" Scraping website..."

def scrape():
	print(current_state())
	page = requests.get(link)
	soup = BeautifulSoup(page.content, 'html.parser')
	html = list(soup.children)[1]
	body = list(html.children)[11]
	table0 = list(body.children)[1]
	table1 = list(table0.children)[5]
	content = table1.get_text()
	lines = content.split("\n")
	juice = []

	for line in lines:
		if len(line) > 200:
			juice.append(line)

	turer = re.split(r'\s{2,}', juice[1])
	for tur in turer:
		try:
			fields = tur.split()
			ref = fields[0][0:5]
			dato = fields[0][5:]

			tid_sted = fields[1]
			tid = tid_sted[0:5]
			lokasjoner = tid_sted[5:].split("-")
			fra = lokasjoner[0]
			til = lokasjoner[1]
			if fra == "Trondheim" or fra == "TRONDHEIM LUFTHAVN VÆRNES":
				found_tur(Tur(ref, dato, fra, til))

		except:
			pass

def found_tur(funn):
	if funn not in treff:
		treff.append(funn)
		print(tur_to_string(funn))
		save_to_file()
		try:
			pass
			send_email(tur_to_string(funn))
		except:
			pass

def send_email(body_text):
	print("Email sent")
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(server_username, server_pwd)

	msg = "\r\n".join([
  "From: {}".format(send_from_email),
  "To: {}".format(send_to_email),
  "Subject: Nytt treff paa returbil.no",
  "",
  body_text
  ])

	server.sendmail(send_from_email, send_to_email, msg)
	server.quit()

def tur_to_string(tur):
	return "{} - {}, dato: {}, ref: {}".format(tur.fra, tur.til, tur.dato, tur.ref)

if __name__ == "__main__": main()