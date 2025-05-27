#!/bin/env python3
import sys
import time
import threading
from classes.config import ConfigHandler
from classes.irc import IRC
from classes.git import GitWatch


if __name__ == "__main__":
    # Reading the config file
    config = ConfigHandler()

    # Connecting to the server
    irc_server = IRC(config.nickname, config.username, config.realname, config.user_password, config.server_password)
    irc_socket = irc_server.connect(config.host, config.port, config.ssl)
   
    # Enabeling the git server watcher
    git_watch = GitWatch(irc_socket, "/tmp/git-push-msg", "#Git")
    threading.Thread(target=git_watch.start_watching, args=(), daemon=True).start()
    
    time.sleep(2)
    irc_server.send("JOIN #Daily-stand-up")
    
    time.sleep(2)    
    irc_server.send(input())

    sys.exit(0)
