import os
import time

import pandas as pd

#csv = pd.read_csv("res.csv")

def send_request(user,i):

    req = user/10

    # locust -f locusttest.py -H ? -u 2000 -r 20 --csv loadtest1 --csv-full-history
    os.system("locust -f /root/?/train-ticket-auto-query-master/login.py -H ? -u %s "
              "-r %s --csv loadtest_%s --csv-full-history -t 50s --headless"
              % (user, req,i))
#send_request(800,"test")