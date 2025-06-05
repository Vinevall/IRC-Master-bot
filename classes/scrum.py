import time
import socket
from datetime import date, datetime
from .printlog import Log
from .calendar import CalendarManager

TODAY = date.today()
YEAR = TODAY.year

# Constructing the log class
log = Log()

# Constructing the calendar
cm = CalendarManager(YEAR)

class ScrumMaster():
    def __init__(self, irc: socket.socket, channel: str):
        self.irc = irc
        self.channel = channel
        self.irc.send(f"JOIN {self.channel}\r\n".encode('utf-8'))
        log.info("Scrum Master is activated.")

    def start_daily_standup(self):
        log.info("Scheduler started. Waiting for 06:00...")
        while True:
            now = datetime.now()
            week = now.isocalendar() [1]
            today = date.today()
            today_str = today.strftime("%y%m%d")
            matches = cm.check_date(today_str)
                
            if now.hour == 6 and now.minute == 0 and now.second == 0:
                if matches:
                    log.info(f"Idag ({today_str}) är det {', '.join(matches)}")
                else:
                    log.info("Idag är det arbersdag!")
                    print(f">> PRIVMSG {self.channel} :Vecka: {week}")
                    self.irc.send(f"PRIVMSG {self.channel} :Vecka: {week}\r\n".encode('utf-8'))
                    print(f">> PRIVMSG {self.channel} :Vad gjorde jag igår?")
                    self.irc.send(f"PRIVMSG {self.channel} :Vad gjorde jag igår?\r\n".encode('utf-8'))
                    print(f">> PRIVMSG {self.channel} :Vad ska jag göra idag?")
                    self.irc.send(f"PRIVMSG {self.channel} :Vad ska jag göra idag?\r\n".encode('utf-8'))
                    print(f">> PRIVMSG {self.channel} :Ser jag några hinder för att utföra mitt uppdrag?")
                    self.irc.send(f"PRIVMSG {self.channel} :Ser jag några hinder för att utföra mitt uppdrag?\r\n".encode('utf-8'))
                
                time.sleep(86300) #86400  
            else:
                time.sleep(1)

