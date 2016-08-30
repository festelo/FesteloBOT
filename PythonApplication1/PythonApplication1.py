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
 
def createParser(): #Настройка аргументов
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', '--new', nargs='+', help="Добавляет новый Cookie в базу данных")
	parser.add_argument('-r', '--run', nargs=1, help="Запускает вручную скрипт для выбранного Cookie")
	parser.add_argument('-i', '--info', nargs  ='+', help="Получает информацию об аккаунте из выбранного Cookie")
	parser.add_argument('-rm', '--remove', nargs=1, help="Удаляет Cookie из базы данных")
	parser.add_argument('-ls', '--list', default=False, action='store_true', help="Выводит список Cookie")

	return parser

def checkAkk(cookie): #Проверка Cookie аккаунта / получение данных об аккаунте 
	try:
		#Открытие CSGO500 для получения данных об аккаунте
		f = urlopen(Request('https://csgo500.com/', headers={'User-Agent': 'Mozilla/5.0', 'Cookie': 'express.sid=' + cookie }))
	except urllib.error.HTTPError:
		print("Ошибка соединения")
		return 1
	result = f.read().decode('utf-8') # Записывание кода HTML страницы в переменную
	try:
		# Ищет на странице данные и записывает в переменные
		rewDate = re.findall('rewardDate = "(.*?) GMT', result)[0]
		nick = re.findall('<div id="account-username">\n(.*?)\n</div>', result)[0]
		balance = re.findall('value = (.*?);', result)[0]
		return [nick, balance, rewDate] # Возвращает массив с полученными данными
	except IndexError:
		#Происходит если какие-то данные на странице не обнаружены.
		print("Ошибка авторизации, данные указаны верно?")
		return 2

def test(cookie, i):
	print("Send request on CSGO500, cookie: " + cookie)
	headers = {'User-agent': 'Mozilla/5.0', 'Cookie': 'express.sid=' + cookie}
	try:
		f = urlopen(Request('https://csgo500.com/', headers=headers)) #Открывает страницу для получения HTML
		res = f.read().decode("UTF-8") #Записывает данные в переменную
	except urllib.error.HTTPError:
		print("Error with access to site! Check internet connection!")
		## ДЛЯ УБУНТЫ РАЗКОММЕНТИРОВАТЬ!!!
		#s.call(['notify-send','Ошибка доступа к сайту CSGO500.com. Проверьте интернет-соединение!','FesteloBot'])
		return 0
	token = re.findall('csrfToken = "(.*?)";', res) #Ищет CSRF токен на странице и записывает в переменную
	app_xml = parse(path + "/data.xml") #Открывает XML документ для чтения
	element = app_xml.childNodes[0].getElementsByTagName('Cookie')[i] #Находит нужный элемент Cookie по индексу i
	if '<div id="login-content">' in res: #Происходит если на странице есть кнопка входа
		print("Login error! Cookie #" + str(i))
		## ДЛЯ УБУНТЫ РАЗКОММЕНТИРОВАТЬ!!!
		#s.call(['notify-send','Ошибка в авторизации при отправлении запроса на CSGO500.com. Cookie #' + str(i),'FesteloBot'])
		element.tagName = "OUTDATE"
	else:
		requestdata = {'_csrf' : token[0]} #Формирует csrf данные для POST запроса
		params_auth = urllib.parse.urlencode(requestdata) 
		try:
			#Отправляет POST запрос для получения ежедневного бонуса
			data = urlopen(Request('https://csgo500.com/reward', data=params_auth.encode("UTF-8"), headers=headers))
		#r = requests.post('https://csgo500.com/reward/',requestdata,
		#headers=headers)
		except urllib.HTTPError: #Происходит когда 1) Нет соединения. 2) Сервер отвечает кодом ошибки
			## ДЛЯ УБУНТЫ РАЗКОММЕНТИРОВАТЬ!!!
			#s.call(['notify-send','Ошибка запроса или время ежедневного бонуса еще не пришло. Cookie #' + str(i),'FesteloBot'])
			print("The daily bonus has not yet come. Cookie #" + str(i))
			return 0
		#print r.cookies['']
		element.removeAttribute("time") #Обновляет данные времени ежедневного бонуса в XML документе
		element.setAttribute("time", str(time.time()))
		## ДЛЯ УБУНТЫ РАЗКОММЕНТИРОВАТЬ!!!
		#s.call(['notify-send','Запрос на CSGO500.com отправлен успешно. Cookie #' + str(i),'FesteloBot'])
		print("Task complete succesful! Cookie # " + str(i))
	res = open(path + "/data.xml", "w") #Открывает XML документ для записи
	app_xml.childNodes[0].writexml(res) #Записывает в него обновленные данные
	res.close() #Закрывает XML документ

def refrCookieList(mode = 0):
	try:
		dom = parse(path + "/data.xml") #Открывает для чтения XML документ
		custom = []
		i = 0
		if mode == 0: ElementName = 'Cookie'
		else: ElementName = 'OUTDATE'
		# Цикл для каждого элемента в XML документе с именем Cookie или OUTDATE
		for node in dom.childNodes[0].getElementsByTagName(ElementName):
			custom.append(CookieList()) #Добавляет к массиву новый объект CookieList и заполняет его
			custom[i].time = node.getAttribute("time")
			custom[i].value = node.firstChild.nodeValue
			i = i + 1 #Счетчик
		return custom
	except IOError:
		DataMake()

def DataMake():
	print("Первый запуск. Подготовка файлов...")
	try:
		os.makedirs(path) #Создает рабочую директорию
		f = open(path + "/data.xml", 'w') #Создает и открывает документ XML
		f.write("<data/>") #Записывает в него XML тег и закрывает его и файл
		f.close
		print("Файлы созданы, добавьте cookie командой 'febot -n COOKIE''")
		exit(0)
	except OSError:
		print("Ошибка при создании файлов, путь: " + path)
		exit(0)

def go():  #Таймер проверки надобности отправления запроса на ежедневный бонус
	custom = refrCookieList() #Обновляет данные с XML документа
	i = 0 #Счетчик
	for s in custom: #Проверка каждого элемента
		if float(s.time) > 0 and time.time() >= float(s.time) + 86400:  
			test(s.value, i)
		i = i + 1
	threading.Timer(60.0, go).start() #Новый старт таймера



#������ ���������: ������ ����������
namespace = createParser().parse_args(sys.argv[1:]) #Парсер аргументов
checkArgs = False
if namespace.new != None: 
	checkArgs = True
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
	checkArgs = True
	custom = refrCookieList()
	if int(namespace.run[0]) >= len(custom) or int(namespace.run[0]) < 0:
		print("Ашибка")
	else:
		test(custom[int(namespace.run[0])].value, int(namespace.run[0]))

if namespace.info != None:
	checkArgs = True
	custom = refrCookieList()
	i = int(namespace.info[0])
	if i >= len(custom) or i < 0:
		print("Ашибка")
	else:
		a = checkAkk(custom[int(namespace.info[0])].value)
		if a != 1 and a != 2:
			print(namespace.info[0] + ": Nick: {} | Balance: {} | Reward Date: {} UTC".format(a[0], a[1], a[2]))

if namespace.remove != None:
	checkArgs = True
	dom = parse(path + "/data.xml")
	custom = refrCookieList()
	outdate = refrCookieList(1)
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
	checkArgs = True
	custom = refrCookieList()
	i = 0
	for s in custom:
		date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(float(custom[i].time)))
		print("\n{}: Recent action: {} UTC\nValue: {}".format(i, date, custom[i].value))
		i = i + 1
	outdate = refrCookieList(1)
	for s in outdate:
		date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(float(outdate[i - len(custom)].time)))
		print("\n{}: OUTDATE!! Recent action: {}(sste)\nValue: {}".format(i, date, outdate[i - len(custom)].value))
		i = i + 1
#�����
#path = "/home/" + os.getlogin() + "/festeloApp/"
#test()
if not checkArgs:
	go()