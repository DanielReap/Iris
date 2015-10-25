from config.config import nickname, username, password, realname, channels, host, port
from core.Iris import main
import os, sys
running = main(nickname, username, realname, channels, password)
if running == False:
	os.execv(sys.executable, [sys.executable] + sys.argv)