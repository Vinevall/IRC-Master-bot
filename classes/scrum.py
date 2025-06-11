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
            dayofweek = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]

            if now.hour == 6 and now.minute == 0 and now.second == 0:
                if matches:
                    log.info(f"Idag ({today_str}) är det {matches}")
                    self.irc.send(f"TOPIC {self.channel} :{matches}\r\n".encode('utf-8'))
                else:
                    self.irc.send(f"TOPIC {self.channel} :{today}\r\n".encode('utf-8'))

                    message = ["==----------------------------oOo----------------------------=="]
                    message.append(f"Vecka: {week}")
                    message.append(f"Idag är det {dayofweek[today.weekday()]} den {today.day}/{today.month} {now.year}")
                    message.append("Vad gjorde jag igår?")
                    message.append("Vad ska jag göra idag?")
                    message.append("Ser jag några hinder för att utföra mitt uppdrag?")
                    message = ["==----------------------------oOo----------------------------=="]

                    for line in message:
                        self.irc.send(f"PRIVMSG {self.channel} :{line}\r\n".encode('utf-8'))
                        time.sleep(0.1)
                
                time.sleep(86300) #86400  
            else:
                time.sleep(1)

