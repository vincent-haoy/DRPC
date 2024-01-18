import warnings
#warnings.filterwarnings("ignore")
import logging
from queries import Query
import scenarios
import random
from utils import *
import time
from locust import HttpUser, between, task, SequentialTaskSet, TaskSet,constant
highspeed_weights = {True: 60, False: 40}
datestr = time.strftime("%Y-%m-%d", time.localtime())
TRIP_DATA: list[dict[str, str]] = [
    {"from": "Shang Hai", "to": "Su Zhou", "trip_id": "D1345", "seat_type": "2", "seat_price": "50.0"},
    {"from": "Shang Hai", "to": "Su Zhou", "trip_id": "D1345", "seat_type": "3", "seat_price": "22.5"},
    {"from": "Su Zhou", "to": "Shang Hai", "trip_id": "G1237", "seat_type": "2", "seat_price": "50.0"},
    {"from": "Shang Hai", "to": "Su Zhou", "trip_id": "G1237", "seat_type": "3", "seat_price": "30.0"},
    {"from": "Nan Jing", "to": "Shang Hai", "trip_id": "G1234", "seat_type": "2", "seat_price": "250.0"},
    {"from": "Nan Jing", "to": "Shang Hai", "trip_id": "G1234", "seat_type": "3", "seat_price": "95.0"},
    {"from": "Wu Xi", "to": "Shang Hai", "trip_id": "G1234", "seat_type": "2", "seat_price": "100.0"},
    {"from": "Wu Xi", "to": "Shang Hai", "trip_id": "G1234", "seat_type": "3", "seat_price": "38.0"},
    {"from": "Nan Jing", "to": "Shang Hai", "trip_id": "G1235", "seat_type": "2", "seat_price": "250.0"},
    {"from": "Nan Jing", "to": "Shang Hai", "trip_id": "G1235", "seat_type": "3", "seat_price": "125.0"},
    {"from": "Nan Jing", "to": "Shang Hai", "trip_id": "G1236", "seat_type": "2", "seat_price": "250.0"},
    {"from": "Nan Jing", "to": "Shang Hai", "trip_id": "G1236", "seat_type": "3", "seat_price": "175.0"},
]
COOKIES = {
        'JSESSIONID':'D6E3BB27E290C35C9DDFE950ECF9DB43',
        'YsbCaptcha':'6F51E1FB5A544E1885DBF18E41AF154A'
    }
USERNAME="?"
PASSWORD="?"
URL = "?"

UUID = "?"
BEARER = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmZHNlX21pY3Jvc2VydmljZSIsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJpZCI6IjRkMmE0NmM3LTcxY2ItNGNmMS1iNWJiLWI2ODQwNmQ5ZGE2ZiIsImlhdCI6MTY4MjU5MzEzNSwiZXhwIjoxNjgyNTk2NzM1fQ.HH683Sgs7g-_jPlwdJHdR6nnDhx7hMAoRfr6MKpKoXE"
HEADER = {
            'Proxy-Connection': 'keep-alive',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
    }
DATE = time.strftime("%Y-%m-%d", time.localtime())

class WebsiteUser(HttpUser):
    wait_time = between(0, 2)
    def on_start(self):
        self.client.headers ["Authorization"] =  f"Bearer {BEARER}"
    @task(1)
    def verification(self):
        verify_url = '/api/v1/verifycode/generate'
        self.client.get(url='/api/v1/verifycode/generate')
    @task(3)
    def query_assurance(self):
        assurance_url = "/api/v1/assuranceservice/assurances/types"
        ass_response = self.client.get(url=assurance_url, headers={})
    @task(1)
    def query_food(self):
        url = f"/api/v1/foodservice/foods/{DATE}/Shang Hai/Su Zhou/D1345"
        response = self.client.get(url=url)
    @task(1)
    def seatservice(self):
        url="/api/v1/seatservice"
        self.client.get(url=url)

    @task(1)
    def query_contacts(self):
        url = f"/api/v1/contactservice/contacts/account/{UUID}"
        response = self.client.get(url=url)
    @task(3)
    def cancle(self):
        url = "/api/v1/cancelservice/cancel"
        response = self.client.get(url=url)
"""
    @task(1)
    def book(self):
        url = "/client_ticket_book.html?tripId=D1345&from=shanghai&to=suzhou&seatType=2&seat_price=50.0&date={DATE}"
        response = self.client.get(url=url)
    @task(1)
    def search_ticket(self):
        url = "/api/v1/travelservice/trips/left"
        response = self.client.get(url=url)
    


    @task(3)
    def query_order(self):
        url = "/api/v1/orderservice/order/refresh"
        response = self.client.get(url=url)
    
    @task(3)
    def query_order2(self):
        url = "/api/v1/orderOtherService/orderOther/refresh"
        response = self.client.get(url=url)
    
    @task(3)
    def query_route(self):
        url = "/api/v1/routeservice/routes"
        response = self.client.get(url=url)


    
    @task(3)
    def dummy_enter_station(self):
        url = "/api/v1/executeservice/execute/execute/"
        response = self.client.get(url=url)
    @task(1)
    def dummy_cheapes(self):
        url = "/api/v1/travelplanservice/travelPlan/cheapest"
        response = self.client.get(url=url)
    @task(1)
    def dummy_rebook(self):
        url = "/api/v1/rebookservice/rebook"
        response = self.client.get(url=url)
    @task(3)
    def dummy_query_admin_travel(self):
        url = "/api/v1/admintravelservice/admintravel"
        response = self.client.get(url=url)
    @task(3)
    def dummy_admin_basic_config(self):
        url = "/api/v1/adminbasicservice/adminbasic/configs"
        response = self.client.get(url=url)

    @task(1)
    def dummy_pay(self):
        url = "/api/v1/inside_pay_service/inside_payment"
        response = self.client.get(url=url)

    @task(1)
    def dummy_pay2(self):
        url="/api/v1/paymentservice"
        self.client.get(url=url)
    
    @task(3)
    def adminuserservice(self):
        url="/api/v1/adminuserservice/users"
        self.client.get(url=url)

    @task(3)
    def basicservice(self):
        url="/api/v1/basicservice"
        self.client.get(url=url)
    
    @task(3)
    def preserveotherservice(self):
        url="/api/v1/preserveotherservice"
        self.client.get(url=url)

    @task(3)
    def trainservice(self):
        url="/api/v1/trainservice"
        self.client.get(url=url)


    @task(3)
    def stationservice(self):
        url="/api/v1/stationservice"
        self.client.get(url=url)

    @task(3)
    def securityservice(self):
        url="/api/v1/securityservice"
        self.client.get(url=url)

    @task(3)
    def routeplanservice(self):
        url="/api/v1/routeplanservice"
        self.client.get(url=url)

    @task(3)
    def userservice(self):
        url="/api/v1/userservice/users"
        self.client.get(url=url)

    @task(3)
    def adminrouteservice(self):
        url="/api/v1/adminrouteservice"
        self.client.get(url=url)

    @task(3)
    def getVouchere(self):
        url="/voucher.html"
        self.client.get(url=url)

    @task(1)
    def priceservice(self):
        url="/api/v1/priceservice"
        self.client.get(url=url)

    @task(3)
    def travel2service(self):
        url="/api/v1/travel2service"
        self.client.get(url=url)

    @task(3)
    def configservice(self):
        url="/api/v1/configservice"
        self.client.get(url=url)

    @task(1)
    def preserveservice(self):
        url="/api/v1/preserveservice"
        self.client.get(url=url)
    """