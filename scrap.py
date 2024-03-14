import csv
import locale
import requests
import dateparser
from bs4 import BeautifulSoup as BSoup
from deep_translator import GoogleTranslator


def convert_money(table_data):
    return int(''.join(table_data.text.strip().replace(u'\xa0', u' ').split(' ')[:-1]))


def clean_name(name: str) -> str:
    """

    :param name:
    :return:
    """
    if '(' in name:
        return name.split('(')[1].split(')')[0]
    elif '«' in name:
        return ' '.join(name.split(' ')[::2])
    else:
        return name


URL = "http://gameshows.ru/wiki/Хто_зверху%3F_(Список_выпусков)"
page = requests.get(URL)

soup = BSoup(page.content, "html.parser")
h2_tags = soup.find_all('h2')
season = 1
all_tables = soup.find_all("table", class_="wikitable")
tables = all_tables[:-1]  # without specials and the last season
episodes = []

for id, table in enumerate(tables):
    if ("wikicenter" in table.get('class', []) or id == 22) and id != 23:
        continue
    i = 0
    ep_count = 1
    double_check = 0
    for row in table.find_all('tr'):
        if row.find("th") is not None:
            continue
        for td in row.find_all('td'):
            if ep_count > 12 and season == 4:
                continue
            if i % 8 == 0:
                if td.text.strip() == '…':
                    break
                episode = int(td.text.strip().split('(')[0])
            elif i % 8 == 1:
                try:
                    locale.setlocale(locale.LC_ALL, 'ru_RU')
                    str_date = td.text.strip().title()
                    date = dateparser.parse(str_date).date()
                except AttributeError:
                    if id != 23:
                        str_date = td.next.text.strip().title()
                        date = dateparser.parse(str_date).date()
                    else:
                        str_date = td.next.next.next.next.text.strip().title()
                        date = dateparser.parse(str_date).date()
            elif i % 8 == 2:
                male_participants = GoogleTranslator(source='ru', target='uk').translate(td.text.strip())
                male_participants = male_participants.split(', ')
                male_participants = [clean_name(man) for man in male_participants]
            elif i % 8 == 3:
                male_money = convert_money(td)
            elif i % 8 == 4:
                male_final_money = convert_money(td)
            elif i % 6 == 5:
                female_participants = GoogleTranslator(source='ru', target='uk').translate(td.text.strip())
                female_participants = female_participants.split(', ')
                female_participants = [clean_name(woman) for woman in female_participants]
            elif i % 8 == 6:
                female_money = convert_money(td)
            elif i % 8 == 7:
                female_final_money = convert_money(td)
            i += 1
        double_check += 1
        if double_check == 2:
            ep_data = dict()
            ep_data['season'] = season
            ep_data['episode'] = episode
            ep_data['date'] = date
            ep_data['males'] = ';'.join(male_participants)
            ep_data['male_money'] = male_money
            ep_data['final_male_money'] = male_final_money
            ep_data['females'] = ';'.join(female_participants)
            ep_data['female_money'] = female_money
            ep_data['final_female_money'] = female_final_money
            episodes.append(ep_data)
            print(f'Episode {episode} of season {season} saved successfully!')
            ep_count += 1
            double_check = 0
            i = 0
    season += 1

field_names = ['season', 'episode', 'date', 'males', 'male_money', 'final_male_money', 'females', 'female_money',
               'final_female_money']

with open('scrapped_data.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(episodes)
