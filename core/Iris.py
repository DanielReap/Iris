import socket
import os
import sys
from config.config import host, port, channels
from commands.module import *
from threading import Thread
def main(nick, user, real, channels, password):
	packets = ["NICK %s\r\n" % nick, "USER %s %s %s :%s\r\n" % (nick, nick, user, real)]
	#Connect to IRC Server
	s = socket.socket()
	s.connect((host, port));
	#Send packets
	for packet in packets:
		s.send(packet);
	channel = channels[0]
	connected = True
	while connected == True:
		data = (s.recv(1024)).strip()
		print data
		if data == "":
			connected = False
		if "PRIVMSG " in data:
			channel = data.split("PRIVMSG ")
			channel = channel[1].split(" :")[0].strip()
		#if "!roulette" in data:
		#	roulette(s, data, channel)
		if " has changed the topic to:" in data:
			#file = open("current_topic", "w+")
			#file.write(data.split(" has changed the topic to:")[1].strip())
			#file.close()
			topic = data.split(" has changed the topic to:")[1].strip()
			f = open("topics/current_topic_%s.txt" % channel, "w+")
			f.write(topic)
			f.close()	
		if "TOPIC %s :" % channel in data:
			#file = open("current_topic", "w+")
			#file.write(data.split(" has changed the topic to:")[1].strip())
			#file.close()
			topic = data.split("TOPIC %s :" % channel)[1].strip()
			f = open("topics/current_topic_%s.txt" % channel, "w+")
			f.write(topic)
			f.close()			
		if "332 %s %s :" % (nick, channel) in data:
			try:
				print "Found topic"
				#file = open("current_topic", "w+")
				#file.write(data.split(" 332 Iris " + channel + " :")[1].strip())
				#file.close()
				topic = data.split("332 %s %s :" % (nick, channel))[1].strip()
				f = open("topics/current_topic.txt")
				f.write(topic)
				f.close()
				print "topic updated"
			except Exception as e:
				pass
		if "!roulette" in data:
			if data.split("PRIVMSG %s :" % channel)[1].strip().startswith("!roulette"):
				roulette(s, data, channel)
		if commandInData(data):
			command, args = getCommandArgs(data)
			if (command.startswith(".")) or (command.startswith("!")):
				if data.split("PRIVMSG %s :" % channel)[1].strip().startswith(command):
					Thread(runCommand(s, command, args, channel, data)).start()
			else:
				Thread(runCommand(s, command, args, channel, data)).start()
				pass
	return False
