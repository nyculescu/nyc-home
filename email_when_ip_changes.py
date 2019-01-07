import argparse
import configparser
import requests
import smtplib

from collections import namedtuple
from requests import get

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Group the email configuration parameters
# Note the 'from_' to avoid using a reserved Python keyword (from)
EmailConfig = namedtuple('EmailConfig', ['user', 'password', 'from_', 'to'])

# Get the ISP's IPv4 from the current network
def get_ISP_IP():
  ip = get('https://api.ipify.org').text
  return ip

# Sends the email
def send_email(email_config):
    '''
    Send an email with the text and html body, using the parameters
    configured in email_config
    '''

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Home IP update'
    msg['From'] = email_config.from_
    msg['To'] = email_config.to

    text_body = 'The new IP is: %s', get_ISP_IP()
    part_plain = MIMEText(text_body, 'plain')
    #part_html = MIMEText(html_body, 'html')

    msg.attach(part_plain)
    #msg.attach(part_html)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_config.user, email_config.password)
        server.sendmail(email_config.from_, [email_config.to], msg.as_string())


def main():
  print("first things first")


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(type=argparse.FileType('r'), dest='config', help='config file')

  args = parser.parse_args()
  config = configparser.ConfigParser()
  config.read_file(args.config)

  email_user = config['EMAIL']['user']
  email_password = config['EMAIL']['password']
  email_from = config['EMAIL']['from']
  email_to = config['EMAIL']['to']
  email_config = EmailConfig(email_user, email_password, email_from, email_to)

  send_email(email_config)
