import socket
import ssl
import sys
import threading
import time

class IRC:
    def __init__(self, nickname: str, username: str, fullname: str, password: str, server_password: str = ""):
        self.irc: socket.socket
        self.nickname = nickname
        self.username = username
        self.password = password
        self.fullname = fullname
        self.server_password = server_password

    def send(self, message: str):
        try:
            if message.lower() in ("exit", "quit"):
                self.irc.send("QUIT\r\n".encode('utf-8'))
                self.close
            if not message.endswith("\r\n"):
                message += "\r\n"
                print(f">> {message.strip()}")
                self.irc.send(message.encode('utf-8'))
        except Exception as e:
            print(f"[INPUT ERROR] {e}")

    def connect(self, server: str, port: int, use_ssl: bool):
        print(f"Connecting to IRC server with IP-address: {server}, on port: {port}, with SSL: {use_ssl}")
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

        #irc.send(f"JOIN #Git\r\n".encode('utf-8'))
        #send(irc, "JOIN #Git")
        #send(irc, "JOIN #Daily-stand-up")  
        #send(irc, input())

    def server_event(self):
        while True:
            try:
                data = self.irc.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    break

                for line in data.strip().split('\r\n'):
                    print(f"{line}")
                    if line.startswith("PING"):
                        token = line.split(' ', 1)[1]
                        pong_response = f"PONG {token}\r\n"
                        print(f">> {pong_response.strip()}")
                        self.irc.send(pong_response.encode('utf-8'))

            except Exception as e:
                print(f"[SERVER ERROR] {e}")
                break    

    def close(self):
        print("Closing the connection to the IRC server...")
        self.irc.close()
        sys.exit(0)


