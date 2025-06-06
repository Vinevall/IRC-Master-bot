import socket
import ssl
import sys
import threading
import time
import re
from datetime import date
from .printlog import Log
from .scrum import ScrumMaster, cm

isRunning = True

# Move this to the config
TEAM=["Jessica", "Jonas", "Michael"]

# Constructing the log class
log = Log()

class IRC:
    def __init__(self, nickname: str, username: str, fullname: str, password: str, server_password: str = ""):
        self.irc: socket.socket
        self.nickname = nickname
        self.username = username
        self.password = password
        self.fullname = fullname
        self.server_password = server_password

    def send(self, message: str):
        global isRunning
        try:
            if message.lower() in ("exit", "quit"):
                self.irc.send("QUIT\r\n".encode('utf-8'))
                self.close
                isRunning = False
                sys.exit(0)
            if not message.endswith("\r\n"):
                message += "\r\n"
                print(f">> {message.strip()}")
                self.irc.send(message.encode('utf-8'))
        except Exception as e:
            log.error(f"[INPUT ERROR] {e}")

    def connect(self, server: str, port: int, use_ssl: bool):
        log.info(f"Connecting to IRC server with IP-address: {server}, on port: {port}, with SSL: {use_ssl}")
        context = ssl.create_default_context()
        raw_socket = socket.create_connection((server, port))
        self.irc = context.wrap_socket(raw_socket, server_hostname=server) if use_ssl else raw_socket
        time.sleep(1)

        if self.server_password:
            self.send(f"PASS {self.server_password}")

        self.send(f"NICK {self.nickname}")
        self.send(f"USER {self.username} 0 * :{self.fullname}")
        threading.Thread(target=self.server_event, args=(), daemon=True).start()
        time.sleep(2)
        self.send(f"PRIVMSG NickServ :IDENTIFY {self.password}")

        return self.irc

    def server_event(self):
        while True:
            try:
                data = self.irc.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    break

                for line in data.strip().split('\r\n'):
                    #match = re.match(r"^:(\w+)!.*?PRIVMSG\s+(#[\w\-]+)\s+:(.*)", line)
                    match = re.match(r"^:(\w+)!.*?PRIVMSG\s+([#\w\-]+)\s+:(.*)", line)

                    if line.startswith("PING"):
                        print(f"<< {line}")
                        token = line.split(' ', 1)[1]
                        pong_response = f"PONG {token}\r\n"
                        print(f">> {pong_response.strip()}")
                        self.irc.send(pong_response.encode('utf-8'))
                    elif match:
                        username = match.group(1)
                        channel = match.group(2)
                        message = match.group(3)
                        print(f"<< [{channel}] [{username}] {message}")
                        if message.startswith("!"):
                            self.handle_comman(channel, username, message)
                    else:
                        print(f"<< {line}")

            except Exception as e:
                print(f"[SERVER ERROR] {e}")
                break  

    def handle_comman(self, channel: str, user: str, command: str):
        # Need to split the command here!
        # !hjälp
        # !ledig [+/-v30 eller +/-250606]
        # !jobbar
        command_list = ""
        variables = ""

        if " " in command:
            command_list = command.split()

        if isinstance(command_list, list):
            command = command_list[0]
            variables = command_list[1]
        
        log.info(f"Command: {command} in channel: {channel}")
        if channel == "scrum_master" or channel == "ScrumMaster":
            if command == "!hjälp" or command == "!help":
                #log.info("Nu ska vi skriva ut hjälpen")
                message_list = [f"Vad behöver du hjälp med, {user}?"]
                message_list.append("==----------------------------------oOo----------------------------------==")
                message_list.append("\x02!hjälp\x02                               - Se denna hjälp.")
                message_list.append("\x02!jobbar\x02                              - Visar alla som arbeter.")
                message_list.append("\x02!semester\x02 [+/-v30 eller +/-250704]   - Registrera eller radera din semester")
                message_list.append("==----------------------------------oOo----------------------------------==")
                for message in message_list:
                    time.sleep(0.1)
                    self.send(f"PRIVMSG {user} {message}")
            elif command == "!jobbar" or command == "!working":
                today = date.today()
                today_str = today.strftime("%y%m%d")
                message = cm.todays_work_force(f"{today_str}", TEAM)
                self.send(f"PRIVMSG {user} {message}")
            elif command == "!semester" or command == "!vacation":
                if not variables:
                    cm.list_all_vacations()
                else:
                    self.send(f"PRIVMSG {user} {variables}")
                    if variables.startswith('+'):
                        # lägga till en vecka eller dag
                        print("Pruutt")
                    elif variables.startswith('-'):
                        # Bort med en vecka eller dag
                        print("Jätte!")



    def activate_scrum_master(self):
        # Constructing the master
        self.sm = ScrumMaster(self.irc, "#Daily-stand-up")
        threading.Thread(target=self.sm.start_daily_standup, args=(), daemon=True).start()
 

    def close(self):
        log.info("Closing the connection to the IRC server...")
        self.irc.close()
        sys.exit(0)


