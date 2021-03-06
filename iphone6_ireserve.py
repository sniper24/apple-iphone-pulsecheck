#!/usr/bin/python
import urllib2
import os
import smtplib
import json
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import datetime
import sys
import time
import iphoneconfig

def sendGmailSmtp(strGmailUser,strGmailPassword,strRecipient,strSubject,strContent):
    strMessage = MIMEMultipart()
    strMessage['From'] = strGmailUser
    strMessage['To'] = strRecipient
    strMessage['Subject'] = strSubject
    strMessage.attach(MIMEText(strContent))
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(strGmailUser, strGmailPassword)
    mailServer.sendmail(strGmailUser, strRecipient, strMessage.as_string())
    mailServer.close()
    return 'send ' + strSubject

#
# read data
#
model_data = open(iphoneconfig.model_data)
store_data = open(iphoneconfig.store_data)
modeljson = json.load(model_data)
storejson = json.load(store_data)

def run():
	#
	# url is defined above.
	#
	try:
		url = "https://reserve.cdn-apple.com/HK/en_HK/reserve/iPhone/availability.json"
		response = urllib2.urlopen(url);
	except Exception, e:
		print datetime.datetime.now().isoformat() + ": %s" % e
		print sendGmailSmtp(iphoneconfig.emailgatewayID,iphoneconfig.emailpwd,iphoneconfig.systememail,'Error', "%s\n" %e + url)
		sys.exit(0)
	#
	# Was hoping text would contain the actual json crap from the URL, but seems not...
	#
	html=response.read()
	#sampledata = open('/home/ubuntu/apple-iphone-pulsecheck/sample')
	#iphonejson = json.load(sampledata)
	iphonejson = json.loads(html)
	#print iphonejson
	#
	# checking
	#
	if html.find("true") == -1:
	#if html.find("true") != -1:
		if html.find("false") > -1:
			print datetime.datetime.now().isoformat() + ": No iReserve - all items are false: " + str(iphonejson["updated"])
		else:
			print datetime.datetime.now().isoformat() + ": No iReserve CODE and no data: " + str(response.code)
	else:
		print datetime.datetime.now().isoformat() + ": iReserve!!"
		print iphonejson
		#
		# Catch Data
		#
		haveStock = ""
		haveplus = ""
		for store in storejson:
			for model in iphonejson[store]:
				if iphonejson[store][model] == True:
					haveStock += "\n" + str(iphonejson["updated"]) + ": " + storejson[store] + " " + modeljson[model]
					if modeljson[model].find("5.5")>-1:
						haveplus += "\n" + str(iphonejson["updated"]) + ": " + storejson[store] + " " + modeljson[model]
		if len(haveStock) > 0:
			print sendGmailSmtp(iphoneconfig.emailgatewayID,iphoneconfig.emailpwd,iphoneconfig.receivemail,'IPhone iReserve avaliable', 'Go https://reserve-hk.apple.com/HK/zh_HK/reserve/iPhone\nhttps://reserve-hk.apple.com/HK/zh_HK/reserve/iPhone/availability\nhttps://reserve-hk.apple.com/HK/zh_HK/reserve/iPhone?execution=e1s2\n' + haveStock)
		if len(haveplus) > 0:
			print sendGmailSmtp(iphoneconfig.emailgatewayID,iphoneconfig.emailpwd,iphoneconfig.iphoneplusmail,'IPhone 6+ iReserve avaliable', 'Go https://reserve-hk.apple.com/HK/zh_HK/reserve/iPhone\nhttps://reserve-hk.apple.com/HK/zh_HK/reserve/iPhone/availability\nhttps://reserve-hk.apple.com/HK/zh_HK/reserve/iPhone?execution=e1s2\n' + haveplus)

count = 0
times = 4
interval = 15
while count < times:
	run()
	count+=1
	time.sleep(interval)
