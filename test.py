import datetime
from models import *
sample = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
loaded = datetime.datetime.strptime(sample, Universal.systemWideStringDatetimeFormat)
toShowUser = datetime.datetime.strftime(loaded, "%d %b %Y %I:%M %p")

print(toShowUser)