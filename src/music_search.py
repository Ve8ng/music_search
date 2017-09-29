#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import os
import subprocess
import sys
import json
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable


def text(strings):
    while(1):
        ques = input(strings)
        if "number" in strings and (not ques.isdigit()):
            print("Please,", strings.lower())
            continue
        else:
            break
    return ques


def parse(artist,page):
    artist=artist
    site = 'http://go.mail.ru/zaycev?q=%s&page=%s' % (artist, page)
    r = requests.get(site)

    soup = BeautifulSoup(r.text, 'html.parser')

    D = r'длительность.(\d+\:\d+\:\d+)'
    R = r'размер.((\d+|\d+.\d+) \w+)'
    B = r'битрейт.(\d+ \w+)'

    global dh
    dh = [[x.get_text(), x.get('href')]
          for x in soup.find_all('a', {'class': "light-link"}) if x.get_text() != "Читать далее"]

    global hd
    hd = [{'длительность': re.search(D, str(x)).group()[13:],
           'размер': re.search(R, str(x)).group()[7:],
           'битрейт': re.search(B, str(x)).group()[8:]}
          for x in soup.find_all('div', {'class': "result__snp"})]
    return dh, hd


def tb(x, y):
    if len(dh) == 20 and x == 20:
        global i
        i+=1
        parse(artist,i)
        x=0
        y=10
    if len(dh) == 0:
        print('Sorry, nothing found')
        sys.exit()
    elif len(dh) <= y:
        y = len(dh)
    table = PrettyTable()
    table.add_column("  ", [i for i in range(x, y)])
    table.align["  "] = "r"
    table.add_column("Name", [dh[i][0] for i in range(x, y)])
    table.align["Name"] = "l"
    table.add_column("Durability", [hd[i]['длительность'] for i in range(x, y)])
    table.add_column("Size", [hd[i]['размер'] for i in range(x, y)])
    table.align["Size"] = "r"
    table.add_column("Bitrate", [hd[i]['битрейт'] for i in range(x, y)])
    print(table)


def main(x, y):
    global artist
    global i
    i = 1
    artist = input('Enter artist or song name: ')
    parse(artist,i)

    while 1:
        tb(x, y)

        try:
            number = text('Choose number: ')
            print('\n{:-^20}'.format(''))
            print('|{:^18}|'.format('Usage'))
            print('{:-^20}'.format(''))
            print('|{}      |'.format(' play - Play song |\n| save - Save song |\n| next - Next page |\n| exit - Exit'))
            print('{:-^20}'.format(''))

            query = input('What\'s next? ')

            soups = BeautifulSoup(requests.get(dh[int(number)][1]).text, 'html.parser')
            data = json.loads(requests.get('http://zaycev.net' + soups.find('div', {'class':"musicset-track"}).get('data-url')).text)

            if query == 'play' or query == 'p':
                print('Playing: ', dh[int(number)][0])
                subprocess.call(['mplayer', '-msglevel', 'all=-1:statusline=5', '-novideo', '%s' % data['url']])

            elif query == 'save' or query == 's':
                print('Downloading: ', dh[int(number)][0])
                subprocess.call(['cd', '~/Music', '&&', 'curl', '-#', '-o', '"%s.mp3"', '%s' % (dh[int(number)][0],data['url'])])

            elif query == 'next' or query == 'n':
                print('Next')
                if x >= 20 and y>=20:
                    x=0
                    y=10
                x+=10
                y+=10

            elif query == 'exit' or query == 'e':
                print('Thank you for beeing with us')
                sys.exit()

        except KeyboardInterrupt:
            subprocess.call('clear')
            print('Thank you for beeing with us')
            sys.exit()
        
        subprocess.call('clear')

if __name__ == "__main__":
    main(0, 10)
