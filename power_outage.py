from datetime import datetime
import re
#from dateutil.parser import parse

# check the last date of the poweroutage and update


def check_last_poweroutage():
    date = ""
    try:
        with open(poweroutage, 'r+') as file:
            date = file.read()
            # try:
            #     date = datetime.strptime(date, '%b %d %Y %I:%M%p')
            #     ddate = date - datetime.now()
            # except ValueError:
            #     file.write(str(datetime.now())
        print(date)
    except FileNotFoundError:
    except EOFError:
        #file.write(str(datetime.now())
        print(date)

check_last_poweroutage()
