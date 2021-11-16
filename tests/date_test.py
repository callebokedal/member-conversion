from datetime import date
from datetime import datetime
'''
clear && docker run -it --rm --name my-test-script -v "$PWD":/usr/src/app -w /usr/src/app python-slim-buster python \
    tests/date_test.py
'''

date_format = "%Y-%m-%d"
d0 = datetime.strptime("2021-05-04", date_format)
acc_days = 0

dates = ['2014-03-26','2011-04-15','2014-06-03','2017-04-17','2017-04-29','2002-04-16','2013-10-07']
for d in dates:
    d1 = datetime.strptime(d, date_format)
    days = (d0 - d1).days
    acc_days += days
    print("{} dagar, {} år".format(days, round((days/365),1)))

print("Totalt: {} dagar, {} år".format(acc_days, round((acc_days/365), 1)))