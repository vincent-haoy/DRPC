import os
import time

import pandas as pd

#csv = pd.read_csv("res.csv")

def send_request(user,i):

    req = user/10

    # locust -f locusttest.py -H http://172.20.110.29:30010 -u 2000 -r 20 --csv loadtest1 --csv-full-history
    os.system("locust -f /root/haoyu/train-ticket-auto-query-master/login.py -H http://172.16.101.163:32677 -u %s "
              "-r %s --csv loadtest_%s --csv-full-history -t 50s --headless"
              % (user, req,i))
#send_request(800,"test")