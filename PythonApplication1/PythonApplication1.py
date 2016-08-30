	# -*- coding: utf-8 -*-
import urllib
import subprocess as s
import os
import argparse
import threading
import sys
import time
import re
from urllib.request import Request, urlopen
import urllib.error
from xml.dom.minidom import parse

class CookieList:
	time = 0
	value = ""

path = os.path.expanduser("~/festeloApp/")
 
def createParser():
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', '--new', nargs='+', help="Добавляет новый Cookie в базу данных")
	parser.add_argument('-r', '--run', nargs=1, help="Запускает вручную скрипт для выбранного Cookie")
	parser.add_argument('-i', '--info', nargs  ='+', help="Получает информацию об аккаунте из выбранного Cookie")
	parser.add_argument('-rm', '--remove', nargs=1, help="Удаляет Cookie из базы данных")
	parser.add_argument('-ls', '--list', default=False, action='store_true', help="Выводит список Cookie")

	return parser

def checkAkk(cookie):
	a = 0
	try:
		f = urlopen(Request('https://csgo500.com/', headers={'User-Agent': 'Mozilla/5.0', 'Cookie': 'express.sid=' + cookie }))
	except urllib.error.HTTPError:
		print("курлык")
		return 1
	result = f.read().decode('utf-8')
	try:
		rewDate = re.findall('rewardDate = "(.*?) GMT', result)[0]
		nick = re.findall('<div id="account-username">\n(.*?)\n</div>', result)[0]
		balance = re.findall('value = (.*?);', result)[0]
		return [nick, balance, rewDate]
		#return  "Nick: {} | Balance: {} | Reward Date: {} UTC".format(nick, balance, rewDate) ]
	except IndexError:
		print("Ошибка авторизации, данные указаны верно?")
		return 2

def test(cookie, i):
	print("Send request on CSGO500, cookie: " + cookie)
	headers = {'User-agent': 'Mozilla/5.0', 'Cookie': 'express.sid=' + cookie}
	try:
		f = urlopen(Request('https://csgo500.com/', headers=headers))
		res = f.read().decode("UTF-8")
	except urllib.error.HTTPError:
		print("Error with access to site! Check internet connection!")
		## ДЛЯ УБУНТЫ РАЗКОММЕНТИРОВАТЬ!!!
		#s.call(['notify-send','Ошибка доступа к сайту CSGO500.com. Проверьте интернет-соединение!','FesteloBot'])
		return 0
	token = re.findall('csrfToken = "(.*?)";', res)
 
	app_xml = parse(path + "/data.xml")
	element = app_xml.childNodes[0].getElementsByTagName('Cookie')[i]
	if '<div id="login-content">' in res:
		print("Login error! Cookie #" + str(i))
		## ДЛЯ УБУНТЫ РАЗКОММЕНТИРОВАТЬ!!!
		#s.call(['notify-send','Ошибка в авторизации при отправлении запроса на CSGO500.com. Cookie #' + str(i),'FesteloBot'])
		element.tagName = "OUTDATE"
	else:
		requestdata = {'_csrf' : token[0]}
		params_auth = urllib.parse.urlencode(requestdata)
		try:
			data = urlopen(Request('https://csgo500.com/reward', data=params_auth.encode("UTF-8"), headers=headers))
		#r = requests.post('https://csgo500.com/reward/',requestdata,
		#headers=headers)
		except urllib.HTTPError:
			## ДЛЯ УБУНТЫ РАЗКОММЕНТИРОВАТЬ!!!
			#s.call(['notify-send','Ошибка запроса или время ежедневного бонуса еще не пришло. Cookie #' + str(i),'FesteloBot'])
			print("The daily bonus has not yet come. Cookie #" + str(i))
			return 0
		#print r.cookies['']
		element.removeAttribute("time")
		element.setAttribute("time", str(time.time()))
		## ДЛЯ УБУНТЫ РАЗКОММЕНТИРОВАТЬ!!!
		#s.call(['notify-send','Запрос на CSGO500.com отправлен успешно. Cookie #' + str(i),'FesteloBot'])
		print("Task complete succesful! Cookie # " + str(i))
	f.close()
	res = open(path + "/data.xml", "w")
	app_xml.childNodes[0].writexml(res)
	res.close()

def refrCookieList():
	try:
		dom = parse(path + "/data.xml")
		custom = []
		i = 0
		for node in dom.childNodes[0].getElementsByTagName('Cookie'):  # visit every node <bar />
			custom.append(CookieList())
			custom[i].time = node.getAttribute("time")
			custom[i].value = node.firstChild.nodeValue
			i = i + 1
		return custom
	except IOError:
		DataMake()

def refrOutDate():
	try:
		dom = parse(path + "/data.xml")
		custom = []
		i = 0
		for node in dom.childNodes[0].getElementsByTagName('OUTDATE'):  # visit every node <bar />
			custom.append(CookieList())
			custom[i].time = node.getAttribute("time")
			custom[i].value = node.firstChild.nodeValue
			i = i + 1
		return custom
	except IOError:
		DataMake()

def DataMake():
	print("Первый запуск. Подготовка файлов...")
	try:
		os.makedirs(path)
		f = open(path + "/data.xml", 'w')
		f.write("<data/>")
		f.close
		print("Файлы созданы, добавьте cookie командой 'febot -n COOKIE''")
		exit(0)
	except OSError:
		print("Ошибка при создании файлов, путь: " + path)
		exit(0)

def go():
	print("НАЧАЛОСЬ")
	custom = refrCookieList()
	i = 0
	for s in custom:
		if float(s.time) > 0 and time.time() >= float(s.time) + 86400:  
			test(s.value, i)
		i = i + 1
	threading.Timer(60.0, go).start()



#������ ���������: ������ ����������
namespace = createParser().parse_args(sys.argv[1:])
checkArgs = 0
if namespace.new != None: 
	checkArgs = 1
	try:
		print("\nПроцесс может занять некоторое время, в зависимости от скорости вашего интернет-соединения\n")
		okda = True
		data = []
		for s in namespace.new:
			a = checkAkk(s)
			if a != 1 and a != 2:
				data.append(a)
			else:
				print("Произошли ошибки в процессе добавления Cookie, измените запрос и/или повторите попытку позже.\nCookie: " + s)
				okda = False
				break
		if okda:
			app_xml = parse(path + "/data.xml")
			i = 0
			for s in namespace.new:
				newCo = app_xml.createElement("Cookie")
				a = time.strptime(data[i][2], "%a %b %d %Y %H:%M:%S")
				b = time.mktime(a)
				c = b - time.altzone + 86400
				newCo.setAttribute("time", str(c))
				newCo.appendChild(app_xml.createTextNode(s))
				app_xml.childNodes[0].appendChild(newCo)
				print("Добавлен COOKIE: Nick: {} | Balance: {} | Reward Date: {} UTC".format(data[i][0], data[i][1], data[i][2])) 
				i = i + 1
			res = open(path + "/data.xml", "w")
			app_xml.childNodes[0].writexml(res)
			res.close()
			#if len(namespace.new) == 1: 
			#	print("\nДобавлен Cookie:: " + namespace.new[0])
			#else:
			#	print("\nДобавлены Cookie:s: " + format(len(namespace.new)))
	except IOError:
		DataMake()

if namespace.run != None:
	checkArgs = 1
	custom = refrCookieList()
	if int(namespace.run[0]) >= len(custom) or int(namespace.run[0]) < 0:
		print("Ашибка")
	else:
		test(custom[int(namespace.run[0])].value, int(namespace.run[0]))

if namespace.info != None:
	checkArgs = 1
	custom = refrCookieList()
	i = int(namespace.info[0])
	if i >= len(custom) or i < 0:
		print("Ашибка")
	else:
		a = checkAkk(custom[int(namespace.info[0])].value)
		if a != 1 and a != 2:
			print(namespace.info[0] + ": Nick: {} | Balance: {} | Reward Date: {} UTC".format(a[0], a[1], a[2]))

if namespace.remove != None:
	checkArgs = 1
	dom = parse(path + "/data.xml")
	custom = refrCookieList()
	outdate = refrOutDate()
	if int(namespace.remove[0]) >= len(custom) + len(outdate) or int(namespace.remove[0]) < 0:
		print("Ашибка")
		exit(0)
	else:
		if(int(namespace.remove[0]) >= len(custom)):
			dom.childNodes[0].removeChild(dom.childNodes[0].getElementsByTagName('OUTDATE')[int(namespace.remove[0]) - len(custom)])
		else:
			dom.childNodes[0].removeChild(dom.childNodes[0].getElementsByTagName('Cookie')[int(namespace.remove[0])])
		res = open(path + "/data.xml", "w")
		dom.childNodes[0].writexml(res)
		res.close()

if namespace.list:
	checkArgs = 1
	custom = refrCookieList()
	i = 0
	for s in custom:
		date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(float(custom[i].time)))
		print("\n{}: Recent action: {} UTC\nValue: {}".format(i, date, custom[i].value))
		i = i + 1
	outdate = refrOutDate()
	for s in outdate:
		date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(float(outdate[i - len(custom)].time)))
		print("\n{}: OUTDATE!! Recent action: {}(sste)\nValue: {}".format(i, date, outdate[i - len(custom)].value))
		i = i + 1
#�����
#path = "/home/" + os.getlogin() + "/festeloApp/"
#test()
if checkArgs == 0:
	go()