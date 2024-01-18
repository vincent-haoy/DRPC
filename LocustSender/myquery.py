import logging
from queries import Query
import scenarios
import random
import string
import requests
import time
url = "?"

# login train-ticket and store the cookies

q = Query(url)
if not q.login():
    print("failed")
    logging.fatal('login failed')
else:
    print("succ login")
# execute scenario on current user
#query_and_preserve(q)
q.query_admin_basic_config()
q.query_admin_basic_price()
q.query_route()
datestr = time.strftime("%Y-%m-%d", time.localtime())
q.query_high_speed_ticket(place_pair=("Shang Hai", "Su Zhou"), time =datestr)
scenarios.query_and_consign(q)


#python -m torch.distributed.launch --nproc_per_node 1 --master_port 12349 main.py --cfg configs/swinv2/swinv2_large_patch4_window12to24_192to384_22kto1k_ft.yaml --data-path ../mmclassification/data/mono [--batch-size 64 --output test --tag test]