#!/bin/env python3
import sys
import time
import threading
from classes.config import ConfigHandler
from classes.irc import IRC
from classes.git import GitWatch
from classes.calendar import CalendarManager

isRunning = True

if __name__ == "__main__":
    # Reading the config file
    config = ConfigHandler()

    # Reading the calendar file
    cm = CalendarManager(2025)

    # Connecting to the server
    irc_server = IRC(config.nickname, config.username, config.realname, config.user_password, config.server_password)
    irc_socket = irc_server.connect(config.host, config.port, config.ssl)
   
    # Enabeling the git server watcher
    git_watch = GitWatch(irc_socket, "/tmp/git-push-msg", "#Git")
    threading.Thread(target=git_watch.start_watching, args=(), daemon=True).start()
    time.sleep(1)

    # Enabeling the scrum master functions
    irc_server.send("JOIN #Daily-stand-up")
    time.sleep(1)

    # Wating for input
    irc_server.send(input())

    sys.exit(0)
