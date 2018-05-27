from pymongo import MongoClient
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import json
import time

reader = open('credentials.txt', 'rb')
username, password = reader.read().split('\n')
client = MongoClient('mongodb://{}:{}@ds235840.mlab.com:35840/odds'.format(username, password))
db = client.odds
odds = db.odds


def get_live(sport='basketball'):
    url = 'https://sports.bovada.lv/{}'.format(sport)
    driver = webdriver.Chrome('../chromedriver')
    driver.get(url)
    scrape_time = float(time.time())
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, 'lxml')
    js = soup.find_all('script', {'class': 'content-data'})[0]
    live_data = re.findall('\[(.+)\]', str(js))[0]
    live_data = json.loads(live_data)
    return live_data, scrape_time
    

def publish_data(live_data, scrape_time):
	data_list = live_data['card_data']['items'][0]['itemList']['items']
	for datum in data_list:
		document = {'time': scrape_time, 'observation': datum}
		odds.insert_one(document)
	print 'Published {} games'.format(len(data_list))


def continuously_publish():
	while True:
		live_data, scrape_time = get_live('baseball')
		publish_data(live_data, scrape_time)
		time.sleep(10)


if __name__ == '__main__':
	continuously_publish()








