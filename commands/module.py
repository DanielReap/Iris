from config.config import channels
from commands import *
import socket

commandHandler = {".ping" : ping,
			"!8ball": ball,
			"!cf": cf,
			"!skype": skype,
			"!getskype": getskype,
			"hello iris": hello,
			"hi iris": hello,
			"!reddit": reddit,
			"!subreddit ": reddit,
			"!4chan ": fourchan,
			"!4channext": fourchannext,
			"!nextpost": reddit_next,
			#"!tweet ": True,
			"!news": news,
			".j ": join,
			".p ": part,
			" 265 ": autoJoin, #This is to join a channel on start
			"PING ": serverPing,
			"!geo": geoIP,
			".ip ": getIp,
			"!topic ": settopic,
			"!topictrim ": trimtopic,
			"!topicappend ": topicappend,
			".akick ": akick,
			".access ": access,
			"!urbandic ": urbandic,
			".btc" : btc,
			".quoteadd ": quoteadd,
			".quotedel ": quotedel,
			".quoterand": quoterand,
			".quotes ": getquotes,
			".newestquote": newestquote,
			"!nsfw": nsfw,
			}

accessCommands = [".akick ", ".access ", "!topic ", "!topictrim ", "!topicappend "]

def commandInData(data):
	for command in commandHandler.keys():
		if command in data:
			return True
	return False

def getCommandArgs(data):
	for command in commandHandler.keys():
		try:
			result = data.split(command)[1].strip()
			return command, result
		except Exception as e:
			pass
def runCommand(s, command, args, channel, data):
	print "Command is" + command
	if command in accessCommands:
		name = getUser(data)
		if whois(s, name):
			if name in access_list:
				commandHandler[command](s, args, channel)
			else:
				send(s, "PRIVMSG %s :You do not have access to this command" % channel)
		else:
			send(s, "PRIVMSG %s :Please identify and try again." % channel)
	else:
		commandHandler[command](s, args, channel)
