from __future__ import division
import socket, urllib2, json, random, math
from config.config import channels, password, nickname
from bs4 import BeautifulSoup
from tools import *
from auto_kick import akick_list
from access import access_list
import subprocess, os
import re
from pyvirtualdisplay import Display
from selenium import webdriver

def ball(s, args, channel):
	ball = [
	"Signs point to yes.",
	"Yes.",
	"Reply hazy, try again.",
	"Without a doubt.",
	"My sources say no.",
	"As I see it, yes.",
	"You may rely on it.",
	"Concentrate and ask again.",
	"Outlook not so good.",
	"It is decidedly so.",
	"Better not tell you now.",
	"Very doubtful.",
	"Yes - definitely.",
	"It is certain.",
	"Cannot predict now.",
	"Most likely.",
	"Ask again later.",
	"My reply is no.",
	"Outlook good.",
	"Don't count on it."]
	send(s, "PRIVMSG %s :%s" % (channel, random.choice(ball)))

def join(s, channel, leftover):
	send(s, "JOIN %s" % channel)

def part(s, channel, leftover):
	send(s, "PART %s" % channel)

def autoJoin(s, args, leftover):
	for channel in channels:
		send(s, "JOIN %s" % channel)
	send(s, "PRIVMSG nickserv identify %s %s" % (nickname, password))

def getUser(data):
	return data.split("!")[0].split(":")[1]

def whois(s, name):
	s.send("WHOIS " + name + "\r\n")
	f = s.recv(1048)
	print f
	if f.find("Iris " + name + " " + name + " :is logged in as") != -1:
		return True
	else:
		return False

def send(s, data):
	s.send("%s\r\n" % data);

def find(data, startTag, endTag): 
  content = data.split(startTag)[1]
  print content
  print content.split(endTag)[0]
  return content

def news(s, args, channel):
	url = 'http://www.cnn.com'
	openurl = urllib2.urlopen(url).read()
	soup = BeautifulSoup(openurl)   
	problem_text = soup.find("h2", {"class":"banner-text banner-text--natural"}).text
	problem_summary = soup.find("h3", {"class":"cd__headline"}).text
	send(s, 'PRIVMSG ' + channel + ' :Top headline - ' + problem_text.strip().encode('utf8')+ '\r\n')
	send(s, 'PRIVMSG ' + channel + ' :Summary - ' + problem_summary.strip().encode('utf8')+ '\r\n')
def nsfw(s, args, channel):
	url = 'http://imgur.com/r/nsfw'
	openurl = urllib2.Request(url, headers={ 'User-Agent' : 'Iris by /u/Iris' })
	openurl = urllib2.urlopen(url).read()
	soup = BeautifulSoup(openurl)
	problem_text = soup.find_all("img", {"original-title": ""})
	print problem_text
	send(s, 'PRIVMSG ' + channel + ' :Enjoy ;) - http:' + random.choice(problem_text)['src'].strip().replace("b.", ".").encode('utf8'))
def btc(s, args, channel):
	try:	
		reponse = urllib2.urlopen("http://api.coindesk.com/v1/bpi/currentprice.json").read()
		btc_info = reponse.strip()
		btc_info = json.loads(btc_info)
		send(s, "PRIVMSG %s :Current BTC price: %s USD" % (channel, str(btc_info['bpi']['USD']['rate_float']))) 
	except Exception as e:
		print e
		send(s, "PRIVMSG %s :Connection to BTC api failed." % channel) 
def settopic(s, top, channel):
	if top == "":
		send(s, "PRIVMSG %s :Please provide something to append to the topic" % (channel))
	else:
		send(s, "TOPIC %s :%s" % (channel, top))
		topic = top
		t = open("topics/current_topic_%s.txt" % channel, "w+")
		t.write(topic)
		t.close()	
def trimtopic(s, query, channel):
	if query == "":
		send(s, "PRIVMSG %s :Please provide something to query" % channel)
	else:
		try:
			t = open("topics/current_topic_%s.txt" % channel, "r+")
			topic = t.read()
			t.close()
			topic = topic.replace(query, "")
			send(s, "TOPIC %s :%s" % (channel, topic))
			t = open("topics/current_topic_%s.txt" % channel, "w+")
			t.write(topic)
			t.close()			
		except Exception as e:
			send(s, "PRIVMSG %s :Query not found" % [channel])
		pass
def topicappend(s, append, channel):
	if append == "":
		send(s, "PRIVMSG %s :Please provide something to append to the topic" % (channel))
	else:
		#topic = open("current_topic").read().strip().split("\n")[0]
		if os.path.exists("topics/current_topic_%s.txt" % channel,):
			t = open("topics/current_topic_%s.txt" % channel, "r+")
			topic = t.read()
			t.close()
		else:
			topic = ""
		send(s, "TOPIC %s :%s\r\n" % (channel, topic.strip()+" | "+append))
		global topic
		topic = topic + " | " + append
		t = open("topics/current_topic_%s.txt" % channel, "w+")
		t.write(topic)
		t.close()			
#Reddit config		REDO THIS
global reddit_topics
reddit_topics = []
global rCounter #Stores the number of which topic you are on
rRounter = 0
def reddit(s, args, channel):
	if len(args) > 0:
			url = "http://reddit.com/r/"+args
	else:
		url = "http://reddit.com"
	print url
	page = urllib2.Request(url, headers={ 'User-Agent' : 'Iris by /u/Iris' })
	page = urllib2.urlopen(page)
	results = BeautifulSoup(page.read())
	posts = results.find_all("div", {"class":"entry unvoted"})
	print posts
	global reddit_topics
	reddit_topics = []
	reddit_topics = posts
	global rCounter
	rCounter = 0
	send(s, "PRIVMSG %s :%s" % (channel, str(reddit_topics[0].a.contents[0]).encode("ascii")))
	if str(reddit_topics[0].a['href']).encode("ascii").startswith("/r/"):
		send(s, "PRIVMSG %s :%s" % (channel, "http://reddit.com"+str(reddit_topics[0].a['href']).encode("ascii")))
	else:
		send(s, "PRIVMSG %s :%s" % (channel, str(reddit_topics[0].a['href']).encode("ascii"))) 
	
def reddit_next(s, args, channel):
	if "rCounter" in globals():
		global rCounter
		rCounter += 1
		global reddit_topics
		send(s, "PRIVMSG %s :%s" % (channel, str(reddit_topics[rCounter].a.contents[0]).encode("ascii")))
		if str(reddit_topics[0].a['href']).encode("ascii").startswith("/r/"):
			send(s, "PRIVMSG %s :%s" % (channel, "http://reddit.com"+str(reddit_topics[rCounter].a['href']).encode("ascii")))
		else:
			send(s, "PRIVMSG %s :%s" % (channel, str(reddit_topics[rCounter].a['href']).encode("ascii"))) 
	else:
		send(s, "PRIVMSG %s :Please pick a topic first using !subreddit <topic>" % (channel))

def ping(s, host, channel):
	send(s, "PRIVMSG %s :Pong" % channel)

def serverPing(s, hashkey, channel):
	send(s, "PONG %s" % hashkey)

def geoIP(s, ip, channel):
	try:
		reponse = urllib2.urlopen("http://ip-api.com/json/"+ip).read()
		ip_info = reponse.strip()
		ip_info = json.loads(ip_info)
		print(ip_info)
		if(ip_info['status'] == 'fail'):
			send(s, "PRIVMSG %s :Failed to find information on IP" % (channel))
		#print ip_info
		#s.send('PRIVMSG %s : %s - %s\r\n' % (channel, ip_info)
		else:
			send(s, 'PRIVMSG %s :%s - %s, %s, %s, %s, %s, TimeZone: %s, Owner: %s' % (channel, ip, ip_info['city'], ip_info['regionName'], ip_info['zip'], ip_info['country'], ip_info['isp'], ip_info['timezone'], ip_info['as'] ))
	except(ValueError, IndexError, urllib2.HTTPError):
		send(s, 'PRIVMSG %s : Could not get IP information' % (channel))
		pass
def skype(s, ip, channel):
	try:
		display = Display(visible=0, size=(800, 600))
		display.start()
		browser = webdriver.Firefox()
		browser.get('http://api.predator.wtf/resolver/?arguments=' + ip )
		res =  re.findall("<body>(.*)</body>", browser.page_source)
		if len(res) > 0:
			res = res[0]
		if("Crap, No IP Was Found!" in browser.page_source):
			send(s, "PRIVMSG %s :%s - Failed to find IP" % (channel, ip))
		else:
			send(s, 'PRIVMSG %s :%s - %s' % (channel, ip, res))
		browser.quit()
		display.stop()
	except Exception as e:
		send(s, 'PRIVMSG %s :Could not get IP information' % (channel))
		send(s, 'PRIVMSG %s :%s' % (channel, e))	
		pass
def cf(s, ip, channel):
	try:
		display = Display(visible=0, size=(800, 600))
		display.start()
		browser = webdriver.Firefox()
		browser.get('http://api.predator.wtf/cfresolve/?arguments=' + ip )
		res =  re.findall(r'[0-9]+(?:\.[0-9]+){3}', browser.page_source)
		if len(res) > 0:
			res = res[0]
		if("This Domain Is Not Vulnerable To Our Method!" in browser.page_source):
			send(s, "PRIVMSG %s :%s - Failed to find IP" % (channel, ip))
		else:
			send(s, 'PRIVMSG %s :%s - %s' % (channel, ip, res))
		browser.quit()
		display.stop()
	except Exception as e:
		send(s, 'PRIVMSG %s :Could not get IP information' % (channel))
		send(s, 'PRIVMSG %s :%s' % (channel, e))	
		pass

def getskype(s, ip, channel):
	try:
		display = Display(visible=0, size=(800, 600))
		display.start()
		browser = webdriver.Firefox()
		browser.get('http://api.predator.wtf/lookup/?arguments=' + ip )
		res =  re.findall("<body>(.*)</body>", browser.page_source)[0]
		browser.quit()
		display.stop()
		if("Athena Found No Results!" in res):
			send(s, "PRIVMSG %s :%s - Failed to find Skype Name" % (channel, ip))
		else:
			send(s, 'PRIVMSG %s :%s - %s' % (channel, ip, res))
	except Exception as e:
		send(s, 'PRIVMSG %s :Could not get IP information' % (channel))
		send(s, 'PRIVMSG %s :%s' % (channel, e))	
		pass

def hello(s, args, channel):
	send(s, "PRIVMSG %s :Hello!" % channel)

def getIp(s, site, channel):
	try:
		ip = socket.gethostbyname(site)
		if site == "rile5.com":
			send(s, 'PRIVMSG ' + channel + ' :' + site + "'s ip is - 198.57.47.136")	
		else:
			send(s, 'PRIVMSG ' + channel + ' :' + site + "'s ip is - " + ip)
	except Exception as e:
		send(s, "PRIVMSG %s :Ip not found" % channel)

def getIpv6(s, site, channel):
	ipv6 = dns.resolver.query(site, "AAAA")
	s.send('PRIVMSG ' + channel + ' :' + site + "'s ipv6 is - " + str(ipv6[0]) + "\r\n")
#4chan config	
global fourchan_topics
fourchan_topics = []
global fourchan_names
fourchan_names = []
global fourchan_dates
fourchan_dates = []
global fourchan_messages
fourchan_messages = []
global fourchan_urls
fourchan_urls = []
global fCounter #Stores the number of which topic you are on
fRounter = 0
def fourchan(s, request, channel):
	try:
		global fCounter
		board = "/"+request+"/"
		page = urllib2.Request("http://4chan.org"+ board, headers={'User-agent' : 'Mozilla/5.0'})
		request = urllib2.urlopen(page)
		request = BeautifulSoup(request.read())
		details = request.find_all("div", {"class" : "thread"})
		global fourchan_topics
		fourchan_topics = details
		name = details[0].find_all("span", {"class" : "name"})
		send(s, "PRIVMSG %s :%s" % (channel, name[0].text))
		date = details[0].find_all("span", {"class" : "dateTime"})
		send(s, "PRIVMSG %s :%s" % (channel, date[0].text))
		url = details[0].a['href']
		send(s, "PRIVMSG %s :%s" % (channel, "http://boards.4chan.org"+board+url))
		problem_text = details[0].find_all("blockquote",{"class":"postMessage"})
		send(s, "PRIVMSG %s :%s" % (channel, problem_text[0].text))
		fCounter = 0
		global current_board
		current_board = board
	except urllib2.HTTPError:
		send(s, "PRIVMSG %s :Throttled by tor." % channel)

def fourchannext(s, dust, channel):
	global fourchan_topics
	global current_board
	global fCounter
	fCounter += 1
	send(s, "PRIVMSG %s :%s\r\n" % (channel, fourchan_topics[fCounter].find_all("span", {"class" : "name"})[0].text))
	send(s, "PRIVMSG %s :%s\r\n" % (channel, fourchan_topics[fCounter].find("span", {"class" : "dateTime"}).text))
	send(s, "PRIVMSG %s :%s\r\n" % (channel, "http://boards.4chan.org"+current_board+fourchan_topics[fCounter].a['href']))
	send(s, "PRIVMSG %s :%s\r\n" % (channel, fourchan_topics[fCounter].find("blockquote",{"class":"postMessage"}).text))

safe = [2, 3, 4, 5, 6]
def roulette(s, data, channel):
	name = data.split("!")[0].split(":")[1]
	kick = 1
	roll = random.randint(1,6)
	global safe
	if name == 'arthur':
		send(s, "KICK %s %s\r\n" % (channel, name))
	else:
		if roll in safe:
			send(s, "PRIVMSG %s :You got lucky this time... Re-spin?\r\n" % (channel))
			s.send("PRIVMSG %s :%s chance of getting kicked\r\n" % (channel, str(round((1-(len(safe)/6))*100)) + "%"))
			del safe[-1]
		else:
			send(s, "KICK %s %s Bang\r\n" % (channel, name))
			safe = [2, 3, 4, 5, 6]
def akick(s, arg, channel):
	arg = arg.strip()
	try:
		if arg == 'list':
			send(s, "PRIVMSG %s :Auto-kick list: %s" % (channel, str(akick_list)))
		if arg.startswith('add'):
			arg = arg.split('add ')[1].strip()
			akick_list.append(arg.strip())
			file = open("auto_kick.py", "w+")
			file.write("akick_list = " + str(akick_list))
			file.close()
			send(s, "PRIVMSG %s :%s added to auto-kick list" % (channel, arg))
		if arg.startswith('del'):
			arg = arg.split('del ')[1].strip()
			akick_list.remove(arg.strip())
			file = open("auto_kick.py", "w+")
			file.write("akick_list = " + str(akick_list))
			file.close()
			send(s, "PRIVMSG %s :%s deleted from auto-kick list" % (channel, arg))
	except Exception as e:
		send(s, "PRIVMSG %s :Please provide a valid name to add to the auto-kick list" % (channel))

def access(s, arg, channel):
	if arg == "list":
		send(s, 'PRIVMSG ' + channel + ' :Access list: '+ str(access_list))
	if "add" in arg:
		name = arg.split('add ')[1]
		access_list.append(name.strip())
		print access_list
		send(s, 'PRIVMSG ' + channel + ' :User added to access list')
		f = open("commands/access.py", "w+")
		f.write("access_list = " + str(access_list))
		f.close()
	if "del" in arg:
		name = arg.split('del ')[1]
		if(name.strip() in access_list):
			access_list.remove(name.strip())
			send(s, 'PRIVMSG ' + channel + ' :User deleted from access list')
			f = open("commands/access.py", "w+")
			f.write("access_list = " + str(access_list))
			f.close()
		else:
			send(s, 'PRIVMSG ' + channel + ' :User not in access list\r\n')	

def urbandic(s, word, channel):
	word = word
	url = ("http://www.urbandictionary.com/define.php?term="+word)
	openurl = urllib2.urlopen(url)
	try:
		soup = BeautifulSoup(openurl.read())
		findtag = soup.find('div', {'class':'meaning'}).text
		send(s, "PRIVMSG %s :%s" % (channel, findtag.strip().encode('utf8')))
	except Exception as e:
		send(s, "PRIVMSG %s :Could not find a definition for %s" % (channel, word))
		pass

def quoterand(s, args, channel):
	f = open('quotes.txt', 'r')
	read = f.read()
	split = read.split('\n')
	send(s, "PRIVMSG %s :%s" % (channel, (random.choice(split))))

def getquotes(s, person, channel):
	theuser = person
	if os.path.isfile(theuser + '.txt'):
		f = open(theuser + '.txt', 'r')
		read = f.read()
		quoteslist = read.split('\n')
		quoteslist = ', '.join(quoteslist)
		quoteslist = quoteslist.rstrip(', ')
		if quoteslist == '':
			send(s, "PRIVMSG %s :Please add quotes for this user first!" % (channel))
		else:
			send(s, "PRIVMSG %s :%s" % (channel, quoteslist))
	else:
		send(s, "PRIVMSG %s :Please add quotes for this user first!" % (channel))

def newestquote(s, args, channel):
	f = open('quotes.txt', 'r')
	read = f.read()
	split_text = read.split('\n')
	join_text = ''.join(split_text)
	if join_text == '':
		send(s, 'PRIVMSG ' + channel + ' :Please enter a quote first!')
	else:
		send(s, 'PRIVMSG ' + channel + ' :' + split_text[-2])

def quoteadd(s, args, channel):
	user = args.split(" ")[0]
	quote = args.split(" ", 1)[1]
	if user != "":
		if os.path.isfile(user + '.txt'):
			f = open(user + '.txt', 'a+')
			f.write('"' + quote + '"\n')
			f.close()
			f = open('quotes.txt', 'a+')
			f.write(user + ' "' + quote + '"\n')
			f.close()
			send(s, "PRIVMSG %s :Quote was added!" % (channel))
		else:
			f = open(user + '.txt', 'w')
			f.close()
			f = open(user + '.txt', 'a+')
			f.write('"' + quote + '"\n')
			f.close()
			f = open('quotes.txt', 'a+')
			f.write(user + ' "' + quote + '"\n')
			f.close()
			send(s, "PRIVMSG %s :Quote was added!" % (channel))
	else:
		send(s, "PRIVMSG %s :Please provide a username!" % (channel))

def quotedel(s, args, channel):
	user = args.split(" ")[0]
	quote = args.split(" ", 1)[1]
	f = open(user + '.txt', 'r')
	lines = f.readlines()
	f.close()
	f = open(user + '.txt', 'w')
	for line in lines:
		if line != '"'+quote+'"\n':
			f.write(line)
		else:
			pass
	f = open('quotes.txt', 'r')
	lines = f.readlines()
	f.close()
	f = open('quotes.txt', 'w')
	for line in lines:
		if line != user +' "'+quote+'"\n':
			f.write(line)
		else:
			pass
	send(s, 'PRIVMSG ' + channel + ' :Quote deleted!\r\n')
	f.close()
