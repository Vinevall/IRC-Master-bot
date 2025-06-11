import os
import socket
import sys
import time
from inotify_simple import INotify, flags
from .printlog import Log

log = Log()

class GitWatch:
    def __init__(self, irc: socket.socket, git_push_file: str, channel: str):
        self.irc = irc
        self.channel = channel
        self.git_file = git_push_file
        log.info("The Git watcher is activated.")
        if not os.path.exists(self.git_file):
            try:
                with open(self.git_file, 'w') as f:
                    pass
                os.chmod(self.git_file, 0o666)
                log.info(f"Created the file: {self.git_file}")
            except Exception as e:
                log.error(f"Unable to create file {self.git_file}: {e}")
                sys.exit(1)

        self.irc.send(f"JOIN {self.channel}\r\n".encode('utf-8'))

    def start_watching(self):
        try:
            inotify = INotify()
            wd = inotify.add_watch(self.git_file, flags.MODIFY)
            last_size = os.path.getsize(self.git_file)

            while True:
                for event in inotify.read():
                    if event.mask & flags.MODIFY:
                        current_size = os.path.getsize(self.git_file)
                        if current_size > last_size:
                            with open(self.git_file, 'r') as f:
                                f.seek(last_size)
                                new_data = f.read()
                                for line in new_data.strip().split('\n'):
                                    if line:
                                        msg = f"PRIVMSG {self.channel} :{line}\r\n"
                                        print(f">> {msg.strip()}")
                                        self.irc.send(msg.encode('utf-8'))
                                        time.sleep(0.1)
                            last_size = current_size
        except Exception as e:
            log.error(f"[GIT WATCH ERROR] {e}")


