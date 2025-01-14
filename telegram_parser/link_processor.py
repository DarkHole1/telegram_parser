# -*- coding: utf-8 -*-
import requests, bs4, re, csv, time, os, cchardet, lxml
from threading import Thread
import concurrent.futures
from print_handler import print_func


def telegram_parser_open():
    try:
        channel_db = open('output/channels.csv', 'a', newline='',  encoding="utf-8")
        group_db = open('output/groups.csv', 'a', newline='',  encoding="utf-8")
        user_db = open('output/users.csv', 'a', newline='',  encoding="utf-8")
        sticker_db = open('output/stickers.csv', 'a', newline='',  encoding="utf-8")
        bot0_db = open('output/bots.csv', 'a', newline='',  encoding="utf-8")
        bot1_db = open('output/bots.csv', 'a', newline='',  encoding="utf-8")
    except FileNotFoundError:
        os.mkdir('output')
        telegram_parser_open()
    return channel_db, group_db, user_db, sticker_db, bot0_db, bot1_db


def telegram_parser(db,

                    link,
                    found,
                    title,
                    description,
                    members,
                    title_stickers,
                    bot_dict,
                    _bot_dict
                    ):
    if 'c' in found:
        db.add_channel(link,title,description,members)
    elif 'g' in found:
        db.add_group(link, title, description, members)
    elif 'u' in found:
        db.add_user(link, title, description)
    if 's' in found:
        db.add_stickers(link, title_stickers)
    if 'b0' in found:
        db.add_bot(link + '_bot', _bot_dict['title_bot'], _bot_dict['description_bot'])
    if 'b1' in found:
        db.add_bot(link + 'bot', bot_dict['title_bot'], bot_dict['description_bot'])


def fast_telegram_parser_open():
    try:
        channel_fast_db = open('output/channels_fast.csv', 'a', newline='',  encoding="utf-8")
        group_fast_db = open('output/groups_fast.csv', 'a', newline='',  encoding="utf-8")
        user_fast_db = open('output/users_fast.csv', 'a', newline='',  encoding="utf-8")
        sticker_fast_db = open('output/stickers_fast.csv', 'a', newline='',  encoding="utf-8")
        bot0_fast_db = open('output/bots_fast.csv', 'a', newline='',  encoding="utf-8")
        bot1_fast_db = open('output/bots_fast.csv', 'a', newline='',  encoding="utf-8")
    except FileNotFoundError:
        os.mkdir('output')
        fast_telegram_parser_open()
    return channel_fast_db, group_fast_db, user_fast_db, sticker_fast_db, bot0_fast_db, bot1_fast_db


def fast_telegram_parser(
        db,

        link,
        found,
):
    if 'c' in found:
        db.add_channel_fast(link)
    elif 'g' in found:
        db.add_group_fast(link)
    elif 'u' in found:
        db.add_user_fast(link)
    if 's' in found:
        db.add_stickers_fast(link)
    if 'b0' in found:
        db.add_bot_fast(link+'_bot')
    if 'b1' in found:
        db.add_bot_fast(link + 'bot')


def channel_group_user_get(link, found, parser_config):
    title = None
    description = None
    members = None
    url = 'https://t.me/' + link  # getting data from link
    s = requests.Session()
    r = s.get(url, stream=True)
    soup = bs4.BeautifulSoup(r.text, "lxml", )
    type_link = str(soup.find_all('a', class_="tgme_action_button_new"))
    members_str = str(soup.find_all('div', class_="tgme_page_extra"))

    try:
        title = str(soup.find('div', class_="tgme_page_title").text)[1:-1].replace(';', ':')
        try:
            description = str(soup.find('div', class_="tgme_page_description").text).replace(';', ':')
        except:
            pass
    except AttributeError:
        return title, description, members, found

    if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '2']):
        if re.search('Preview channel', type_link):  # check for channel
            members_int = re.findall(r'\d+', members_str)
            members = ''
            members = members.join(members_int)
            if members == '':
                members = '0'
            found += 'c,'
            return title, description, members, found
    if found == '':
        if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '3']):
            if 'Preview channel' not in type_link and 'members' in members_str:  # check for group
                members_str = members_str.split(',')[0]
                members_int = re.findall(r'\d+', members_str)
                members = ''
                members = members.join(members_int)
                if members == '':
                    members = '0'
                found += 'g,'
                return title, description, members, found

    if found == '':
        if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '4']):
            if 'tgme_action_button_new' in type_link and 'member' not in members_str and 'Send Message' in type_link:
                members = None
                found += 'u,'
                return title, description, members, found
    return title, description, members, found


def stickers_get(link, found):
    url_stickers = 'https://t.me/addstickers/' + link  # getting data from link
    r_stickers = requests.get(url_stickers, stream=True)
    soup_stickers = bs4.BeautifulSoup(r_stickers.text, "lxml", )
    type_link = str(soup_stickers.find_all('div', class_="tgme_page_description")).replace(u'\xa0', ' ').replace(';',
                                                                                                                 ':')
    if re.search('Sticker Set', type_link):
        return None, found
    else:
        start_name = [(m.start(0), m.end(0)) for m in re.finditer("<strong>", type_link)][1][1]
        end_name = [(m.start(0), m.end(0)) for m in re.finditer("</strong>", type_link)][1][0]
        title_stickers = type_link[start_name:end_name]
        found += 's,'
        return title_stickers, found


def bot_get(link, found, i):
    bot_dict = dict()
    url_bot = 'https://t.me/' + link
    r_bot = requests.get(url_bot, stream=True)
    soup_bot = bs4.BeautifulSoup(r_bot.text, "lxml", )
    type_link = soup_bot.find_all('div', class_="tgme_page_extra")
    if type_link != []:
        title_bot = soup_bot.find('div', class_='tgme_page_title').text
        try:
            description_bot = soup_bot.find('div', class_='tgme_page_description').text
        except:
            description_bot = None
        bot_dict['title_bot'] = title_bot
        bot_dict['description_bot'] = description_bot
        found += 'b' + str(i) + ','
    return bot_dict, found


def output_func(found, link, parser_config):
    output_dict = {
        'c': 'Channel, ',
        'g': 'Group, ',
        'u': 'User, ',
        's': 'Sticker Pack, ',
        'b0': 'Bot, ',
        'b1': 'Bot, ',
    }
    if '1' in parser_config['output'] or '2' in parser_config['output']:
        if found != '':
            mess = ''
            for found_item in found.split(','):
                if found_item != '':
                    mess += output_dict[found_item]
        else:
            mess = 'False'
        if '2' in parser_config['output']:
            if mess == 'False':
                return
        print_func(parser_config,
                   'Try: ' + link + ', result: ' + mess)


def get_link(link,
             parser_config,
             db):
    i = 0
    while i < 5:
        try:
            title = None
            description = None
            members = None
            title_stickers = None
            bot_dict = None
            _bot_dict = None
            found = ''
            found_cgu = ''
            found_b = ''
            found_s = ''
            _found_b = ''
            if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '2', '3', '4', '5', '6']):
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                    if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '2', '3', '4']):
                        channel_group_user_future = executor.submit(channel_group_user_get, link, found, parser_config)
                    if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '5']):
                        sticker_future = executor.submit(stickers_get, link, found)
                    if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '6']):
                        if '1' in parser_config['bot_mode']:
                            _bot_future = executor.submit(bot_get, link + '_bot', found, 0)
                        if '2' in parser_config['bot_mode']:
                            bot_future = executor.submit(bot_get, link + 'bot', found, 1)

                if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '2', '3', '4']):
                    title, description, members, found_cgu = channel_group_user_future.result()
                if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '5']):
                    title_stickers, found_s = sticker_future.result()
                if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '6']):
                    if '1' in parser_config['bot_mode']:
                        _bot_dict, _found_b = _bot_future.result()
                    if '2' in parser_config['bot_mode']:
                        bot_dict, found_b = bot_future.result()
            found = found_b + _found_b + found_cgu + found_s
            Thread(target=telegram_parser, args=(db,
                                                 link,
                                                 found,
                                                 title,
                                                 description,
                                                 members,
                                                 title_stickers,
                                                 bot_dict,
                                                 _bot_dict
                                                 )).start()

            output_func(found, link, parser_config)

            return
        except OSError:  # exceptions
            if i != 4:
                print_func(parser_config,
                           'No connection. Pause script')
            if i == 4:
                print_func(parser_config,
                           'Connection error. Stop script.')
                return 'connection_error'
            i += 1
            time.sleep(10)


def fast_channel_group_user_get(link, found, parser_config):
    url = 'https://t.me/' + link  # getting data from link
    r = requests.get(url, stream=True)
    soup = bs4.BeautifulSoup(r.text, "lxml", )
    type_link = str(soup.find_all('a', class_="tgme_action_button_new"))
    members_str = str(soup.find_all('div', class_="tgme_page_extra"))
    if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '2']):
        if 'Preview channel' in type_link:  # check for channel
            found += 'c,'
            return found
    if found == '':
        if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '3']):
            if 'Preview channel' not in type_link and 'members' in members_str:  # check for group
                found += 'g,'
                return found
    if found == '':
        if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '4']):
            if 'tgme_action_button_new' in type_link and 'member' not in members_str and 'Send Message' in type_link:
                found += 'u,'
                return found
    return found


def fast_stickers_get(link, found):
    url_stickers = 'https://t.me/addstickers/' + link  # getting data from link
    r_stickers = requests.get(url_stickers, stream=True)
    soup_stickers = bs4.BeautifulSoup(r_stickers.text, "lxml", )
    type_link = str(soup_stickers.find_all('div', class_="tgme_page_description")).replace(u'\xa0', ' ').replace(';',
                                                                                                                 ':')
    if re.search('Sticker Set', type_link):  # check for channel
        return found
    else:
        found += 's,'
        return found


def fast_bot_get(link, found, i):
    url_bot = 'https://t.me/' + link
    r_bot = requests.get(url_bot, stream=True)
    soup_bot = bs4.BeautifulSoup(r_bot.text, "lxml", )
    type_link = soup_bot.find_all('div', class_="tgme_page_extra")
    if type_link != []:
        found += 'b' + str(i) + ','
    return found


def get_fast_link(link, parser_config, db):
    i = 0
    while i < 5:
        try:
            found = ''
            found_b = ''
            found_sgu = ''
            found_s = ''
            _found_b = ''
            if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '2', '3', '4', '5', '6']):
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                    if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '2', '3', '4']):
                        channel_group_user_future = executor.submit(fast_channel_group_user_get, link, found,
                                                                    parser_config)
                    if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '5']):
                        sticker_future = executor.submit(fast_stickers_get, link, found)
                    if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '6']):
                        if '1' in parser_config['bot_mode']:
                            _bot_future = executor.submit(fast_bot_get, link + '_bot', found, 0)
                        if '2' in parser_config['bot_mode']:
                            bot_future = executor.submit(fast_bot_get, link + 'bot', found, 1)

            if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '2', '3', '4']):
                found_sgu = channel_group_user_future.result()
            if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '5']):
                found_s = sticker_future.result()
            if any(parser_mode in parser_config['parser_type'] for parser_mode in ['1', '6']):
                if '1' in parser_config['bot_mode']:
                    _found_b = _bot_future.result()
                if '2' in parser_config['bot_mode']:
                    found_b = bot_future.result()

            found = found_s + found_sgu + found_b + _found_b
            Thread(target=fast_telegram_parser, args=(
                db,
                link,
                found,
            )).start()

            output_func(found, link, parser_config)

            return
        except OSError:  # exceptions
            if i != 4:
                print_func(parser_config,
                           'No connection. Pause script')
            if i == 4:
                print_func(parser_config,
                           'Connection error. Stop script.')
                return 'connection_error'
            i += 1
            time.sleep(10)
