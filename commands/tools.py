import socket
import re
import urllib
               
def getIp(s, site, channel):
        ip = socket.gethostbyname(site)
        if site == "rile5.com":
                s.send('PRIVMSG ' + channel + ' :' + site + "'s ip is - 198.57.47.136\r\n")    
        else:
                s.send('PRIVMSG ' + channel + ' :' + site + "'s ip is - " + ip + "\r\n")