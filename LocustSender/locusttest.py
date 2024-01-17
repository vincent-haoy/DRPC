from locust import HttpUser, between, task, SequentialTaskSet, TaskSet,constant
import warnings
#warnings.filterwarnings("ignore")
import logging
from queries import Query
import scenarios
import random
from utils import *
import time
highspeed_weights = {True: 60, False: 40}
datestr = time.strftime("%Y-%m-%d", time.localtime())
place_pairs = [("Shang Hai", "Su Zhou"),
                       ("Su Zhou", "Shang Hai"),
                       ("Nan Jing", "Shang Hai")]



class WebsiteUser(HttpUser):
    wait_time = between(0, 2)
    def on_start(self):
        url = "http://172.16.101.163:32677"
        self.client.headers ={
            'Proxy-Connection': 'keep-alive',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        self.username = "fdse_microservice"
        self.password = "111111"
        self.bearer = ""
        headers = {
            'Origin': url,
            'Referer': "/client_login.html",
        }
        data = '{"username":"' + self.username + '","password":"' + \
            self.password + '","verificationCode":"1234"}'
        verify_ur = '/api/v1/verifycode/generate'
        r = self.client.get(url=verify_ur)
        time.sleep(0.1)
        with self.client.post(url = "/api/v1/users/login",
                                headers=headers,
                                json={
                                     "username": self.username,
                                     "password": self.password},
                                verify=False,
                                catch_response=True     
                                     ) as response:
        
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == 0:
                    response.failure("log in fail")
                    return
                
                data = data.get("data")
                self.uid = data.get("userId")
                self.token = data.get("token")
                self.client.headers = {"Authorization": f"Bearer {self.token}"}
                response.success()
            else:
                response.failure("Got wrong response")
                return
    @task(1)
    class SequenceOfTasks(SequentialTaskSet):
        wait_time = between(0, 2)
        def on_start(self):
            query_other =  random_from_weighted(highspeed_weights)
            if query_other:
                url = "/api/v1/orderOtherService/orderOther/refresh"
            else:
                url = "/api/v1/orderservice/order/refresh"
            payload = {
                "loginId": self.user.uid,
            }
            response = self.client.post(url=url, headers=dict(), json=payload, catch_response=True)
            data = response.json().get("data")
            pairs = []
            types = tuple([0, 1])
            for d in data:
            # status = 0: not paid
            # status=1 paid not collect
            # status=2 collected
                if d.get("status") in types:
                    order_id = d.get("id")
                    trip_id = d.get("trainNumber")
                    pairs.append((order_id, trip_id))
            self.pairs = pairs

        @task(1)
        class action_after_querry(TaskSet):
            wait_time = constant(1)

            @task(1)
            def preseve_high_speedticket(self):
                time = datestr
                place_pair = ("Shang Hai", "Su Zhou")
                #validating there is sufficient ticket left
                validate_url = "/api/v1/travelservice/trips/left"
                assurance_url = "/api/v1/assuranceservice/assurances/types"
                ass_response = self.client.get(url=assurance_url, headers={})
                payload = {
                    "departureTime": time,
                    "startPlace": place_pair[0],
                    "endPlace": place_pair[1],
                }
                response = self.client.get(url=validate_url, headers={}, json=payload)
            
            @task(1)
            def preseve_normal_speedticket(self):
                time = datestr
                ##validating there is sufficient ticket left
                validate_url = "/api/v1/travel2service/trips/left"
                place_pair = ("Shang Hai", "Tai Yuan")
                payload = {
                "departureTime": time,
                "startPlace": place_pair[0],
                "endPlace": place_pair[1],
                }
                assurance_url = "/api/v1/assuranceservice/assurances/types"
                self.client.get(url=assurance_url, headers={})
                response = self.client.post(url=validate_url, headers={}, json=payload,catch_response=True)
                data = response.json().get("data")  # type: dict

                """trip_ids = []
                for d in data:
                    trip_id = d.get("tripId").get("type") + \
                    d.get("tripId").get("number")
                    trip_ids.append(trip_id)
                trip_id = random_from_list(trip_ids)
                base_preserve_payload = {
                "accountId": self.user.uid,
                "assurance": "0",
                "contactsId": "",
                "date": time,
                "from": place_pair[0],
                "to": place_pair[1],
                "tripId": random_from_list(trip_ids)
                 }"""


            
            """@task(1)
            def put_consign(self):
                url = "/api/v1/orderservice/order/refresh"
                payload = {
                    "loginId": self.user.uid,
                }
                
                response = self.client.post(url=url, headers={}, json=payload,catch_response=True)
                if response.status_code != 200 or response.json().get("data") is None:
                    print("login failed")
                    response.failure("log in fail ")
                    pass
                data = response.json().get("data")
                datum = random.choice(data)
                consignload = {
                "accountId": datum.get("accountId"),
                "handleDate": time.strftime('%Y-%m-%d', time.localtime(time.time())),
                "targetDate": time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                "from": datum.get("from"),
                "to": datum.get("to"),
                "orderId": datum.get("id"),
                "consignee": "32",
                "phone": "12345677654",
                "weight": "32",
                "id": "",
                "isWithin": False
                }
                url = "/api/v1/consignservice/consigns"
                res = self.client.put(url="/api/v1/consignservice/consigns",
                                json=consignload)"""
            
            @task(1)    
            def cancle_order(self):
                if not self.parent.pairs:
                    return
                pair = random_from_list(self.parent.pairs)
                url = f"/api/v1/cancelservice/cancel/{pair[0]}/{self.user.uid}"
                res = self.client.get(url=url, headers={})

            @task(1)
            def collect_order(self):
                if not self.parent.pairs:
                    return
                pair = random_from_list(self.parent.pairs)
                order_id=pair[0]
                url = f"/api/v1/executeservice/execute/collected/{order_id}"
                res = self.client.get(url=url, headers={})

    """@task(1)
    def get_foods(self):
        departure_date = datestr
        head = {"Accept": "application/json",
                "Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        response = self.client.get("/api/v1/foodservice/foods/" + departure_date + "/shanghai/suzhou/D1345",
            headers=head)"""
        
    @task(1)
    def query_assurances(self):
        url = "/api/v1/assuranceservice/assurances/types"

        response = self.client.get(url=url)


    """@task(3)
    def query_advanced_ticket(self):
        wait_time = between(0, 2)
        query_type = random.choice(["cheapest", "quickest", "minStation"])
        url = f"/api/v1/travelplanservice/travelPlan/{query_type}"
        place_pairs = [("Shang Hai", "Su Zhou"),
                       ("Su Zhou", "Shang Hai"),
                       ("Nan Jing", "Shang Hai")]
        place_pair =("Shang Hai", "Su Zhou")
        date = datestr

        payload = {
            "departureTime": date,
            "startPlace": place_pair[0],
            "endPlace": place_pair[1],
        }

        response = self.client.post(url=url, json=payload,headers = {},catch_response=True)"""
    
    @task(1)
    def query_admin_basic_price(self):
        url = "/api/v1/adminbasicservice/adminbasic/prices"
        response = self.client.get(url=url, headers={})

    @task(1)
    def query_admin_basic_config(self):
        url = "/api/v1/adminbasicservice/adminbasic/configs"
        response = self.client.get(url=url, headers={})
    
    @task(1)
    def query_routes(self):
        url = "/api/v1/routeservice/routes"
        response = self.client.get(url=url, headers={})

    @task(1)
    def query_contacts(self):
        url = f"/api/v1/contactservice/contacts/account/{self.uid}"

        response = self.client.get(url=url, headers={})
   