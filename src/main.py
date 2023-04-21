import logging
import os
import time

from nc_dnsapi import Client, DNSRecord
from requests import get

customer = os.getenv('CUSTOMER_ID')
api_key = os.getenv('API_KEY')
api_password = os.getenv('API_PASSWORD')
domain_names = os.getenv('DOMAINS', ",").split(",")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
if customer is None or api_key is None or api_password is None:
    logging.info(f"You are missing some credentials.")
    exit()

API = Client(customer, api_key, api_password)
DOMAINS = list()


class Domain:
    def __init__(self, name):
        global DOMAINS
        self.name = name.strip()
        self.records = list()
        DOMAINS.append(self)
        self.fetch_records()

    def fetch_records(self):
        global API
        records = API.dns_records(self.name)
        if len(records) == 0:
            self.add_destinations()
        else:
            logging.info(f"Fetched {len(records)} records(s) for {self.name}.")
        for record in records:
            self.records.append(record)

    def update_records(self):
        global IP_ADDRESS
        for rec in self.records:
            rec.destination = IP_ADDRESS

    def add_destinations(self):
        global IP_ADDRESS, API
        API.add_dns_record(self.name, DNSRecord("*", "A", IP_ADDRESS))
        API.add_dns_record(self.name, DNSRecord("@", "A", IP_ADDRESS))
        logging.info(f"Added new records for {self.name}.")
        time.sleep(5)  # Let's wait a bit before we fetch again
        self.fetch_records()

    def update_destinations(self):
        global IP_ADDRESS, API
        for rec in self.records:
            if rec.destination != IP_ADDRESS:
                rec.destination = IP_ADDRESS
                API.update_dns_record(self.name, rec)
                logging.info(f"Updated record {rec.hostname} for {self.name}.")
            else:
                logging.info(f"Nothing to do for {self.name} records: {rec}")

    def __str__(self):
        return f"{self.name} with records {self.records}"


def get_public_ip():
    return get('https://api.ipify.org').content.decode('utf8')


for domain_name in domain_names:
    domain_object = Domain(domain_name)
IP_ADDRESS = get_public_ip()

logging.info(f"Initialization started with IP: {IP_ADDRESS}")
logging.info("Found following domains with records:")
for dom in DOMAINS:
    logging.info(dom)

counter = 0
while 1:
    IP_ADDRESS = get_public_ip()
    for domain in DOMAINS:
        if counter >= 12:
            logging.info("Forcing new fetches for domains.")
            domain.fetch_records()
            counter = 0
        domain.update_destinations()
    logging.info(f'Check done at {time.strftime("%d.%m.%y, %H:%M:%S", time.localtime())}.')
    time.sleep(60 * 5)
    counter += 1
