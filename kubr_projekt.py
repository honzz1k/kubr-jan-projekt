"""
projekt.py: třetí projekt do Engeto Python Akademie

author: Jan Kubr
"""

import sys
import csv
import requests
from bs4 import BeautifulSoup

def parse_arguments():
    if len(sys.argv) != 3:
        print("Chyba: Zadej 2 argumenty – URL a název výstupního souboru.")
        sys.exit(1)
    return sys.argv[1], sys.argv[2]

def get_soup(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
    if r.status_code != 200:
        print(f"Chyba při načítání stránky: {url}")
        sys.exit(1)
    return BeautifulSoup(r.text, 'html.parser')

def get_links(soup, base_url):
    links = []
    table = soup.find('table')
    rows = table.find_all('tr')[2:]

    for row in rows:
        tds = row.find_all('td')
        code = tds[0].text.strip()
        name = tds[1].text.strip()
        link = base_url + tds[0].find('a')['href']
        links.append((code, name, link))
    return links

def get_votes(soup):
    reg = soup.find('td', headers='sa2').text.replace('\xa0', '').replace(' ', '')
    env = soup.find('td', headers='sa3').text.replace('\xa0', '').replace(' ', '')
    val = soup.find('td', headers='sa6').text.replace('\xa0', '').replace(' ', '')

    votes = {}
    party_names = soup.find_all('td', class_='overflow_name')
    party_votes = soup.find_all('td', headers=['t1sb3', 't2sb3'])

    for name, vote in zip(party_names, party_votes):
        votes[name.text.strip()] = vote.text.replace('\xa0', '').replace(' ', '')
    return reg, env, val, votes

def main():
    base_url = "https://volby.cz/pls/ps2017nss/"
    url, output = parse_arguments()
    soup = get_soup(url)
    links = get_links(soup, base_url)

    _, _, first_link = links[0]
    first_soup = get_soup(first_link)
    _, _, _, example_votes = get_votes(first_soup)
    party_names = list(example_votes.keys())

    with open(output, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['code', 'location', 'registered', 'envelopes', 'valid'] + party_names
        writer.writerow(header)

        for code, name, link in links:
            soup = get_soup(link)
            registered, envelopes, valid, votes = get_votes(soup)
            row = [code, name, registered, envelopes, valid] + [votes.get(party, '0') for party in party_names]
            writer.writerow(row)

    print(f"Hotovo! Výsledky jsou v souboru: {output}")

if __name__ == "__main__":
    main()
