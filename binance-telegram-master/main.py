import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import json
import requests
import schedule
import argparse

parser = argparse.ArgumentParser(description='GatsbyNance')
parser.add_argument('--once', action='store_true', help='Run the script once')

encryptedUid = []
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

class HeadData:
    #more TODO here: add more data normalization in future.
    def __init__(self, name, daily_roi, weekly_roi, monthly_roi, all_roi, last_trade):
        self.name = name
        self.daily_roi = daily_roi
        self.weekly_roi = weekly_roi
        self.monthly_roi = monthly_roi
        self.all_roi = all_roi
        self.last_trade = last_trade
    
    def __str__(self):
        return f"{self.name} {self.daily_roi} {self.weekly_roi} {self.monthly_roi} {self.all_roi} {self.last_trade}"

def get_head_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', text='Daily ROI')
    dailyROI = div.find_next('div')
    div = soup.find('div', text='Weekly ROI')
    weeklyROI = div.find_next('div')
    div = soup.find('div', text='Monthly ROI')
    monthlyROI = div.find_next('div')
    div = soup.find('div', text='All ROI')
    allROI = div.find_next('div')
    div = soup.find('div', text=re.compile('Last Trade: '))
    lastTrade = div.text
    div = soup.find('div', class_='name-wrap')
    div = div.find_next('div')
    name = div.text
    return HeadData(name, dailyROI.text, weeklyROI.text, monthlyROI.text, allROI.text, lastTrade)


def telegram_send_message(message, telegram_token, telegram_chat_id):
    url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(telegram_token, telegram_chat_id, message)
    requests.post(url)

def get_board(id):
    _url = "https://www.binance.com/en/futures-activity/leaderboard/user?encryptedUid={}".format(id)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(_url)
    time.sleep(35)
    html = driver.page_source
    driver.quit()
    return html

class UserTableData:
    #more TODO here: add more data normalization in future.
    def __init__(self, symbol, size, entry_price, mark_price, pnl, time, action):
        self.symbol = symbol
        self.size = size
        self.entry_price = entry_price
        self.mark_price = mark_price
        self.pnl = pnl
        self.time = time
        self.action = action

    def __str__(self):
        return f"{self.symbol} {self.size} {self.entry_price} {self.mark_price} {self.pnl} {self.time} {self.action}"

def build_data(html):
    
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if len(cols) == 7:
            data.append(UserTableData(cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]))
    return data

def message_builder_open(data, head):
    data_symbol_split = data.symbol.split(' ')
    data_symbol = data_symbol_split[0]
    trade_type = data_symbol_split[-1]
    messages = []
    messages.append({"ENTRY": f"✅ GATSBYNANCE sort position of « {head.name} » \n CRYPTO: {data_symbol} \n TRADE: {trade_type} \n ENTRY PRICE: {data.entry_price} \n  t. me/GatsbyllionaireOfficial"})
    messages.append({"CLOSING": f"❌ GATSBYNANCE sort closing position of « {head.name} » \n CRYPTO: {data_symbol} \n CLOSING PRICE: {data.mark_price} \n  t. me/GatsbyllionaireOfficial"})
    return messages

def write_to_logs(data):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open('logs/log.gary', 'a') as f:
        f.write(current_time + " | " + data + "\n")
        f.close()

def load_config():
    with open('config.json') as f:
        data = json.load(f)
        telegram = data['telegram']
        user = data['user']
        telegram_token = telegram['token']
        telegram_chat_id = telegram['chat_id']
        for i in user:
            encryptedUid.append(i['encryptedUid'])
        return telegram_token, telegram_chat_id

telegram_token, telegram_chat_id = load_config()

cache = []

def collector():
    for id in encryptedUid:             
        board = get_board(id)
        data = build_data(board) # this is a list of UserTableData objects
        head_case = get_head_data(board) # this is a HeadData object
        for i in data:
            messages = message_builder_open(i, head_case)
            for message in messages:
                if message not in cache:
                    cache.append(message)
                    write_to_logs(str(message))
                    for key, value in message.items():
                        telegram_send_message(value, telegram_token, telegram_chat_id)
                        time.sleep(1)
                else:
                    print("---------------------------------------") 
                    print("[INFO] We have already collected this data.")
                    print("[INFO] Data: " + str(message))
                    print("[INFO] Cache: " + str(cache))
                    print("[INFO] Cache length: " + str(len(cache)))
                    print("---------------------------------------")

import progressbar

if parser.parse_args().once:
    print('[&] Running once')
    collector()
else:
    print('[&] Running on schedule')
    schedule.every(5).minutes.do(collector)
    widgets = ['SCANNING: ', progressbar.AnimatedMarker()]
    bar = progressbar.ProgressBar(widgets=widgets).start()
    counter = 0
    while True:
        schedule.run_pending()
        time.sleep(1)
        bar.update(counter)
        counter += 1
        if counter == 100:
            counter = 0


    