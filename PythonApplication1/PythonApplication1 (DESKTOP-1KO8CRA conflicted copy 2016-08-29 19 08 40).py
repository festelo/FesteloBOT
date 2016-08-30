	 # -*- coding: utf-8 -*-
import urllib
import subprocess as s
import os
import argparse
import threading
import sys
import time
import re
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

def checkAkk(cookie, mode=0):
	opener = urllib.request
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	opener.addheaders = [('Cookie', 'express.sid=' + cookie)]
	a = 0
	try:
		req = urllib.request('https://csgo500.com/', headers={'User-Agent': 'Mozilla/5.0', 'Cookie': 'express.sid=' + cookie })
		f = opener.open('https://csgo500.com/')
	except urllib2.URLError:
		print("Отсутствие интернет-соединения")
		return 1
	result = f.read()
	try:
		rewDate = re.findall('rewardDate = "(.*?) GMT', result)[0]
		if mode == 0:
				nick = re.findall('<div id="account-username">\n(.*?)\n</div>', result)[0]
				balance = re.findall('value = (.*?);', result)[0]
				return "Nick: {} | Balance: {} | Reward Date: {} UTC".format(nick, balance, rewDate)
		  else: return rewDate
	 except IndexError:
		  print("Ошибка авторизации, данные указаны верно?")
		  return 2

def test(cookie, i):
	 print("Send request on CSGO500, cookie: ".decode('utf-8') + cookie)
	 headers = {'User-agent': 'Mozilla/5.0', 'Cookie': 'express.sid=' + cookie}
 
	 opener = urllib2.build_opener()
	 opener.addheaders = [('Cookie', 'express.sid=' + cookie)]
	 opener.addheaders += [('User-agent', 'Mozilla/5.0')]
	 res = ""
	 try:
		  f = opener.open('https://csgo500.com/')
		  res = f.read()
	 except urllib2.URLError:
		  print("Error with access to site! Check internet connection!")
		  s.call(['notify-send','Ошибка доступа к сайту CSGO500.com. Проверьте интернет-соединение!','FesteloBot'])
		  return 0
	 token = re.findall('csrfToken = "(.*?)";', res)
 
	 app_xml = parse(path + "/data.xml")
	 element = app_xml.childNodes[0].getElementsByTagName('Cookie')[i]
	 if '<div id="login-content">' in res:
		  print("Login error! Cookie #" + str(i))
		  s.call(['notify-send','Ошибка в авторизации при отправлении запроса на CSGO500.com. Cookie #' + str(i),'FesteloBot'])
		  element.tagName = "OUTDATE"
	 else:
		  requestdata = {'_csrf' : token[0]}
		  params_auth = urllib.urlencode(requestdata)
		  r = urllib2.Request('https://csgo500.com/reward', params_auth, headers)
		  try:
				data = urllib2.urlopen(r)
		  #r = requests.post('https://csgo500.com/reward/',requestdata,
		  #headers=headers)
		  except urllib2.HTTPError:
				s.call(['notify-send','Ошибка запроса или время ежедневного бонуса еще не пришло. Cookie #' + str(i),'FesteloBot'])
				print("The daily bonus has not yet come. Cookie #" + str(i))
				return 0
		  #print r.cookies['']
		  element.removeAttribute("time")
		  element.setAttribute("time", str(time.time()))
		  s.call(['notify-send','Запрос на CSGO500.com отправлен успешно. Cookie #' + str(i),'FesteloBot'])
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
	 custom = refrCookieList()
	 i = 0
	 for s in custom:
		  if float(s.time) > 0 and time.time() >= float(s.time) + 86400:  
				test(s.value, i)
		  i = i + 1
	 threading.Timer(60.0, go).start()



#Начало программы: Разбор аргументов
namespace = createParser().parse_args(sys.argv[1:])
checkArgs = 0
if namespace.new != None: 
	 checkArgs = 1
	 try:
		  print("\nПроцесс может занять некоторое время, в зависимости от скорости вашего интернет-соединения")
		  okda = 1
		  data = []
		  for s in namespace.new:
				a = checkAkk(s, 1)
				if a != 1 and a != 2:
					 data.append(a)
				else:
					 print("Произошли ошибки в процессе добавления Cookie, измените запрос и/или повторите попытку позже.\nCookie: " + s)
					 okda = 0
					 break
		  if okda == 1:
				app_xml = parse(path + "/data.xml")
				i = 0
				for s in namespace.new:
					 newCo = app_xml.createElement("Cookie")
					 a = time.strptime(data[i], "%a %b %d %Y %H:%M:%S")
					 b = time.mktime(a)
					 c = b - time.altzone - 86400
					 newCo.setAttribute("time", str(c))
					 newCo.appendChild(app_xml.createTextNode(s))
					 app_xml.childNodes[0].appendChild(newCo)
					 i = i + 1
				res = open(path + "/data.xml", "w")
				app_xml.childNodes[0].writexml(res)
				res.close()
				if len(namespace.new) == 1: 
					 print("\nДобавлен Cookie: " + namespace.new[0])
				else:
					 print("\nДобавлено Cookies: " + format(len(namespace.new)))
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
				print(namespace.info[0] + ": " + a)

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
#Ууууу
#path = "/home/" + os.getlogin() + "/festeloApp/"
#test()
if checkArgs == 0:
	 go()