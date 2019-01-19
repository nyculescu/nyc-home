import argparse
import configparser
import requests
import smtplib
import sys
import jinja2
import mistune
import urllib.request
import re
from datetime import datetime
from collections import namedtuple
from requests import get
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# The latest IP will be stored here: last_ip.txt
last_ip_txt_file = 'last_ip.txt'

# Group the email configuration parameters
# Note the 'from_' to avoid using a reserved Python keyword (from)
EmailConfig = namedtuple('EmailConfig', ['user', 'password', 'from_', 'to'])

# Get the email templates from hard disk
EMAIL_TEMPLATE_FILE = 'email_template.md'
EMAIL_STYLING_FILE = 'email_styling.html'

with open(EMAIL_TEMPLATE_FILE) as md_file:
    EMAIL_TEMPLATE = md_file.read()

with open(EMAIL_STYLING_FILE) as html_file:
    EMAIL_STYLING = html_file.read()


def compose_email_body(ip_):
  text_body = EMAIL_TEMPLATE.format(
      **{'text_to_be_added': 'The new IP is: %s' % ip_,
         'timestamp': str(datetime.now()),
         'which_script': 'email_when_ip_changes'})

  html_content = mistune.markdown(text_body)
  html_body = jinja2.Template(EMAIL_STYLING).render(content=html_content)

  return text_body, html_body


def get_ISP_IP():
  ip_check_sites = ("https://api.ipify.org", "http://checkip.dyndns.org", "http://ifconfig.me")
  for ip_site in ip_check_sites:
    try:
      if urllib.request.urlopen(ip_site).getcode() == 200:
        ip_text = re.findall(r'[0-9]+(?:\.[0-9]+){3}', get(ip_site).text)
        return ip_text[0]
    except:
      return 'error'
  return 'error'


def send_email(email_config, text_body, html_body):
    '''
    Send an email with the text and html body, using the parameters
    configured in email_config
    '''
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Home IP update'
    msg['From'] = email_config.from_
    msg['To'] = email_config.to

    part_plain = MIMEText(text_body, 'plain')
    part_html = MIMEText(html_body, 'html')

    msg.attach(part_plain)
    msg.attach(part_html)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_config.user, email_config.password)
        server.sendmail(email_config.from_, [email_config.to], msg.as_string())


def init():
  parser = argparse.ArgumentParser()
  parser.add_argument(type=argparse.FileType(
      'r'), dest='config', help='config file')
  parser.add_argument('-o', dest='output', type=argparse.FileType('w'),
                      help='output file', default=sys.stdout)

  args = parser.parse_args()
  config = configparser.ConfigParser()
  config.read_file(args.config)

  email_user = config['EMAIL']['user']
  # Here is a tricky part with Google. Go to https://support.google.com/accounts/answer/185833?hl=en-GB and follow "How to generate an App password"
  # Into App passwords -> Select app: Mail, Select device: Other (or whatever you need)
  email_password = config['EMAIL']['password']
  email_from = config['EMAIL']['from']
  email_to = config['EMAIL']['to']
  email_config = EmailConfig(email_user, email_password, email_from, email_to)
  return email_config


def check_ip_change(ip_):
  if ip_ != 'error':
    try:
      with open(last_ip_txt_file, 'r+') as file:
        line = file.read(1)
        if line == [] or line == '':
          return True
        else:
          if ip_ != line:
            return True
          else:
            return False
    except FileNotFoundError:
      return True
  else:
    return False


if __name__ == '__main__':
  #Check the new IP against the oldest one
  isp_ip = get_ISP_IP()
  if check_ip_change(isp_ip):
    email_config = init()
    text_body, html_body = compose_email_body(isp_ip)
    send_email(email_config, text_body, html_body)
    # The last_ip file is updated here in order to be sure that the email is sent
    with open(last_ip_txt_file, 'w') as file:
      file.write(isp_ip)
