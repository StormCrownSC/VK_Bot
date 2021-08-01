import re
import requests
import urllib
import urllib.parse
from urllib.parse import quote
import xlrd
from xlrd import sheet
import json

import datetime
from datetime import timedelta, date, datetime

import PIL.Image as Image
from vk_api import VkUpload
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import os, os.path, glob, shutil, re, subprocess, time, sys
import requests
from bs4 import BeautifulSoup

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

info_professor_or_group = True
name_of_professor = ''
list_of_users = {}
if os.path.exists('list_of_users.json'):
    with open("list_of_users.json", "r") as read_file:
        list_of_users = json.load(read_file)

mounth_of_year = {'1': 'января', '2': 'февраля', '3': 'марта', '4': 'апреля', '5': 'мая', '6': 'июня', '7': 'июля', '8': 'августа', '9': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}
day_of_the_week = {'0': 'понедельник', '1': 'вторник', '2': 'среда', '3': 'четверг', '4': 'пятница', '5': 'суббота'}
day_of_the_week_name = {'понедельник': '0', 'вторник': '1', 'среда': '2', 'четверг': '3', 'пятница': '4', 'суббота': '5'}

def parth_coronavirus():
    try:
        page = requests.get("https://coronavirusstat.ru/country/russia/")
        soup = BeautifulSoup(page.text, "html.parser")
        result = soup.findAll("table")[0].find("tbody").findAll("tr")
        result_for_day = soup.findAll("div")[1]
        if result_for_day != '':
            data____ = {}
            for i in range(0, 10, 1):
                data____[str(i)] = str(result[i])
            f1 = open('result_for_day.txt', 'w')
            f1.write(str(result_for_day))
            f1.close()
            with open("result.json", "w") as write_file:
                json.dump(data____, write_file)
    except:
        print('К сожалению, лучший сайт опять завис...')

def parth_coronavirus_for_city(region, event, vk, vk_session):
    #try:
    region = str(region)
    parth_coronavirus()
    f = open('result_for_day.txt')
    result_for_day = str(f.read())
    f.close()
    stroka_ = re.findall(region.title() + ' область([\w \S]+)</div>-->', str(result_for_day))
    data_for_oblast_temp = re.findall('"dline">([\d]+)</span>', str(stroka_))
    sluchaev_for__ = re.findall('<div class="h6 m-0"> ([\d]+) <small>', str(stroka_))
    data_for_day_temp = re.findall('За 1 день">([+\-\d]+)</span>', str(stroka_))
    date_for_day_temp = re.findall('По состоянию на <[\w]+>([\d]+ [\w]+ [\d:]+)', str(result_for_day))
    temple = 'По состоянию на ' + str(date_for_day_temp[0]) + '\nрегион: ' + region.title() + ' обл.'
    if len(data_for_day_temp) != 0:
        temple += '\nСлучаев: ' + sluchaev_for__[0] + ' (' + str(data_for_day_temp[3]) + ' за сегодня)'
        for i in range(0, 3, 1):
            tmp = ''
            if i == 0:
                tmp = '\nАктивных: '
            if i == 1:
                tmp = '\nВылечено: '
            if i == 2:
                tmp = '\nУмерло: '
            temple += tmp + ' ' + str(data_for_oblast_temp[i]) + ' (' + str(data_for_day_temp[i]) + ' за сегодня)'
    else:

        temple += '\nСлучаев: ' + sluchaev_for__[0]
        for i in range(0, 3, 1):
            tmp = ''
            if i == 0:
                tmp = '\nАктивных: '
            if i == 1:
                tmp = '\nВылечено: '
            if i == 2:
                tmp = '\nУмерло: '
            temple += tmp + ' ' + str(data_for_oblast_temp[i])
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message=temple
    )

    """except:
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            message='Выбранный вами регион не найден'
        )"""

def print_graph(array):
    year = []
    for key in array.keys():
        year.append(key)
    population = {
        'Активные': [int(i[0]) / 1000000 for i in array.values()],
        'Вылечено': [int(i[1]) / 1000000 for i in array.values()],
        'Умерло': [int(i[2]) / 1000000 for i in array.values()],
    }

    fig, ax = plt.subplots()
    ax.stackplot(year, population.values(), labels=population.keys())
    ax.legend(loc='upper left')
    ax.set_title('Россия - детальная статистика - коронавирус')
    ax.set_ylabel('Число людей (в миллионах)')
    for ax in fig.axes:
        matplotlib.pyplot.sca(ax)
        plt.xticks(rotation=23)
    fig.savefig('covid.png')

def parth_coronavirus_for_all(event, vk, vk_session):
    try:
        parth_coronavirus()
        f1 = open('result_for_day.txt')
        result_for_day = str(f1.read())
        f1.close()
        with open("result.json", "r") as read_file:
            result = json.load(read_file)
        date_for_day_temp = re.findall('По состоянию на <[\w]+>([\d]+ [\w]+ [\d:]+)', str(result_for_day))
        date_for_day = 'По состоянию на ' + str(date_for_day_temp[0])

        stat_for_day = re.findall('<b>([\d.,]+ [\w]+.)</b>', str(result_for_day))
        cases_for_day_now = re.findall('([\d]+)</span> <span class="small text-muted">\(сегодня\)', str(result_for_day))
        temple = date_for_day
        for i in range(0, 4, 1):
            tmp = ''
            if i == 0:
                tmp = '\nСлучаев: '
            if i == 1:
                tmp = '\nАктивных: '
            if i == 2:
                tmp = '\nВылечено: '
            if i == 3:
                tmp = '\nУмерло: '
            temple += tmp + str(stat_for_day[i]) + ' (' + str(cases_for_day_now[i]) + ' за сегодня)'

        ten_days = {}
        for i in range(0, 10, 1):
            data__ = re.findall('<th>([\w.]+)</th>', str(result[str(i)]))
            active__ = re.findall('> ([\d]+)', str(result[str(i)]))
            ten_days[str(data__[0])] = active__

        print_graph(ten_days)
        upload = VkUpload(vk_session)
        photo = upload.photo_messages("covid.png")[0]
        owner_id = photo['owner_id']
        photo_id = photo['id']
        access_key = photo['access_key']
        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        vk.messages.send(
            user_id=event.user_id,
            attachment=attachment,
            random_id=get_random_id(),
            message=temple
        )


    except:
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            message='Произошёл сбой'
        )

def find_professors(name, event, vk, vk_session):
    with open("professor.json", "r") as read_file:
        data = json.load(read_file)
    global name_of_professor
    name_of_professor = name
    name = str(name)
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('на сегодня', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('на завтра', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()  # переход на вторую строку
    keyboard.add_button('на эту неделю', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('на следующую неделю', color=VkKeyboardColor.PRIMARY)
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Показать расписание преподавателя ' + name.title()
    )

def professors_(name, event, vk, vk_session):
    data1 = ''
    with open("professor.json", "r") as read_file:
        data1 = json.load(read_file)
    global info_professor_or_group
    info_professor_or_group = False
    keys = data1.keys()
    data_name = re.findall(name, str(keys))

    if len(data_name) > 1:
        data_name = re.findall('{} \w.\w'.format(name), str(keys))
        temple = ''
        keyboard = VkKeyboard(one_time=True)
        for i in data_name:
            keyboard.add_button(i.title(), color=VkKeyboardColor.NEGATIVE)

        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Выберите преподавателя'
        )

    elif len(data_name) == 1:
        data_name = re.findall('{} \w.\w'.format(name), str(keys))
        data_name = str(data_name)
        data_name = data_name[2:-2]
        find_professors(data_name, event, vk, vk_session)
    
    else:
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            message='Преподаватель отсутствует'
        )

def photos(event, vk, vk_session, temple):
    upload = VkUpload(vk_session)
    img = Image.new('RGB', (len(os.listdir('photos')) * 50, 50))
    kk = 0
    for elem in os.listdir('photos'):
        img1 = Image.open('photos/' + str(elem))
        img.paste(img1, (kk, 0))
        kk += 50
    img.save("photos/image.png")

    photo = upload.photo_messages("photos/image.png")[0]
    owner_id = photo['owner_id']
    photo_id = photo['id']
    access_key = photo['access_key']
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk.messages.send(
        user_id=event.user_id,
        attachment=attachment,
        random_id=get_random_id(),
        message=temple
    )
    for elem in os.listdir('photos'):
        os.remove('photos/' + str(elem))

def parth_weather():
    s_city = "Moscow,RU"
    city_id = 0
    appid = "bd91290c88473bdddefa71c5e7946d3e"
    res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                       params={'q': s_city, 'type': 'like', 'units': 'metric', 'lang': 'ru', 'APPID': appid})
    data = res.json()
    with open("weather.json", "w") as write_file:
        json.dump(data, write_file)
    res_1 = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'q': s_city, 'type': 'like', 'units': 'metric', 'lang': 'ru', 'APPID': appid})
    data_ = res_1.json()
    with open("weather_day.json", "w") as write_file:
        json.dump(data_, write_file)

def pressure(bar):
    return round(bar * 7.50062)

def bofort_scale(wind):
    if wind <= 0.2:
        return 'штиль'
    elif wind <= 1.5:
        return 'тихий'
    elif wind <= 3.3:
        return 'лёгкий'
    elif wind <= 5.4:
        return 'слабый'
    elif wind <= 7.9:
        return 'умеренный'
    elif wind <= 10.7:
        return 'свежий'
    elif wind <= 13.8:
        return 'сильный'
    elif wind <= 17.1:
        return 'крепкий'
    elif wind <= 20.7:
        return 'очень крепкий'
    elif wind <= 24.4:
        return 'шторм'
    elif wind <= 28.4:
        return 'сильный шторм'
    elif wind <= 32.6:
        return 'жестокий шторм'
    else:
        return 'ураган'

def wind_rumb(deg):
    if deg <= 10:
        return 'северный'
    elif deg < 80:
        return 'северо-восточный'
    elif deg <= 100:
        return 'восточный'
    elif deg < 170:
        return 'юго-восточный'
    elif deg <= 190:
        return 'южный'
    elif deg < 260:
        return 'юго-западный'
    elif deg <= 280:
        return 'западный'
    elif deg < 350:
        return 'северо-западный'
    elif deg <= 360:
        return 'северный'

def weather_day(event, vk, vk_session, photo_con):
    #try:
    upload = VkUpload(vk_session)
    attachments = []
    answer = ''
    with open("weather_day.json", "r") as read_file:
        data = json.load(read_file)
    if photo_con == 1:
        image = requests.get("http://openweathermap.org/img/w/" + str(data['weather'][0]['icon']) + ".png", stream=True)
        photo = upload.photo_messages(photos=image.raw)[0]
        attachments.append("photo{}_{}".format(photo["owner_id"], photo["id"]))
        vk.messages.send(
            user_id=event.user_id,
            attachment=','.join(attachments),
            random_id=get_random_id(),
            message='Погода в Москве'
        )
    if photo_con == 0:
        answer += 'Погода в Москве:\n'
    answer += str(data['weather'][0]['description']) + ', температура: ' + str(round(data['main']['temp_min'])) \
             + ' - ' + str(round(data['main']['temp_max'])) + 'ºC\nДавление: ' + str(pressure(int(data['main']['pressure']))) \
             + ' мм рт. ст., влажность: ' + str(data['main']['humidity']) + '%\nВетер: ' + str(bofort_scale(int(data['wind']['speed']))) + ', ' \
             + str(round(data['wind']['speed'])) + ' м/с, ' +  str(wind_rumb(int(data['wind']['deg'])))

    return answer

    #except Exception as e:
        #return 0
        #pass

def weather_week(event, vk, vk_session):
    try:
        with open("weather.json", "r") as read_file:
            data = json.load(read_file)
        today = date.today()
        last_day = today + timedelta(5)
        l_day = str(last_day.day)
        if int(last_day.day) < 10:
            l_day = '0' + str(last_day.day)
        temple__ = 'Погода в Москве с ' + str(today.day) + '.' + str(today.month) + ' по ' + l_day + '.' + str(last_day.month)
        kk = 0
        temple = ''
        for i in data['list']:
            date_temp = str(re.findall('^\d\d\d\d[-]\d\d[-]\d\d', str(i['dt_txt'])))
            date_temp = date_temp[2:-2]
            cure_date =str(re.findall('\d\d[:]\d\d[:]\d\d', str(i['dt_txt'])))
            cure_date = cure_date[2:-2]
            if str(date_temp) < str(last_day) and cure_date == '12:00:00':
                if round(i['main']['temp']) < 10 and round(i['main']['temp']) >= 0:
                    temple += '+' + str(round(i['main']['temp'])) + '°С // '
                else:
                    temple += str(round(i['main']['temp'])) + '°С // '
                image = requests.get("http://openweathermap.org/img/w/" + str(i['weather'][0]['icon']) + ".png",
                                     stream=True)
                kk += 1
                with open("photos/file" + str(kk) + ".png", "wb") as f:
                    f.write(image.content)

        temple = temple[:-2]
        temple += ' ДЕНЬ\n/ '
        for i in data['list']:
            date_temp = str(re.findall('^\d\d\d\d[-]\d\d[-]\d\d', str(i['dt_txt'])))
            date_temp = date_temp[2:-2]
            cure_date =str(re.findall('\d\d[:]\d\d[:]\d\d', str(i['dt_txt'])))
            cure_date = cure_date[2:-2]
            if str(date_temp) < str(last_day) and cure_date == '21:00:00':
                if round(i['main']['temp']) < 10 and round(i['main']['temp']) >= 0:
                    temple += '+' + str(round(i['main']['temp'])) + '°С // '
                else:
                    temple += str(round(i['main']['temp'])) + '°С // '

        temple = temple[:-2]
        temple += ' НОЧЬ\n'
        photos(event, vk, vk_session, temple__)
        return temple


    except Exception as e:
        print("Exception (find):", e)
        pass

def weather_today(event, vk, vk_session):
    try:
        upload = VkUpload(vk_session)
        with open("weather.json", "r") as read_file:
            data = json.load(read_file)
        today = date.today()
        temple = '/ '
        for i in data['list']:
            date_temp = str(re.findall('^\d\d\d\d[-]\d\d[-]\d\d', str(i['dt_txt'])))
            date_temp = date_temp[2:-2]
            cure_date = str(re.findall('\d\d[:]\d\d[:]\d\d', str(i['dt_txt'])))
            cure_date = cure_date[2:-2]
            if str(date_temp) == str(today) and (cure_date == '09:00:00' or cure_date == '15:00:00' or cure_date == '18:00:00' or cure_date == '21:00:00'):
                if round(i['main']['temp']) < 10 and round(i['main']['temp']) >= 0:
                    temple += '+' + str(round(i['main']['temp'])) + '°С // '
                else:
                    temple += str(round(i['main']['temp'])) + '°С // '

        temple = temple[:-2]
        temple += '\n\n'
        kk = 0
        for i in data['list']:
            date_temp = str(re.findall('^\d\d\d\d[-]\d\d[-]\d\d', str(i['dt_txt'])))
            date_temp = date_temp[2:-2]
            cure_date = str(re.findall('\d\d[:]\d\d[:]\d\d', str(i['dt_txt'])))
            cure_date = cure_date[2:-2]

            if str(date_temp) == str(today):
                if cure_date == '09:00:00':
                    temple += '\nУТРО\n// '
                    temple += str(i['weather'][0]['description']) + ', температура: ' + str(
                        round(i['main']['temp_min'])) \
                              + ' - ' + str(round(i['main']['temp_max'])) + 'ºC\n// Давление: ' + str(
                        pressure(int(i['main']['pressure']))) \
                              + ' мм рт. ст., влажность: ' + str(i['main']['humidity']) + '%\n// Ветер: ' + str(
                        bofort_scale(int(i['wind']['speed']))) + ', ' \
                              + str(round(i['wind']['speed'])) + ' м/с, ' + str(wind_rumb(int(i['wind']['deg'])))
                    image = requests.get("http://openweathermap.org/img/w/" + str(i['weather'][0]['icon']) + ".png",
                                         stream=True)
                    kk += 1
                    with open("photos/file" + str(kk) + ".png", "wb") as l:
                        l.write(image.content)
                if cure_date == '15:00:00':
                    temple += '\nДЕНЬ\n// '
                    temple += str(i['weather'][0]['description']) + ', температура: ' + str(
                        round(i['main']['temp_min'])) \
                              + ' - ' + str(round(i['main']['temp_max'])) + 'ºC\n// Давление: ' + str(
                        pressure(int(i['main']['pressure']))) \
                              + ' мм рт. ст., влажность: ' + str(i['main']['humidity']) + '%\n// Ветер: ' + str(
                        bofort_scale(int(i['wind']['speed']))) + ', ' \
                              + str(round(i['wind']['speed'])) + ' м/с, ' + str(wind_rumb(int(i['wind']['deg'])))
                    image = requests.get("http://openweathermap.org/img/w/" + str(i['weather'][0]['icon']) + ".png",
                                         stream=True)
                    kk += 1
                    with open("photos/file" + str(kk) + ".png", "wb") as l:
                        l.write(image.content)
                if cure_date == '18:00:00':
                    temple += '\nВЕЧЕР\n// '
                    temple += str(i['weather'][0]['description']) + ', температура: ' + str(
                        round(i['main']['temp_min'])) \
                              + ' - ' + str(round(i['main']['temp_max'])) + 'ºC\n// Давление: ' + str(
                        pressure(int(i['main']['pressure']))) \
                              + ' мм рт. ст., влажность: ' + str(i['main']['humidity']) + '%\n// Ветер: ' + str(
                        bofort_scale(int(i['wind']['speed']))) + ', ' \
                              + str(round(i['wind']['speed'])) + ' м/с, ' + str(wind_rumb(int(i['wind']['deg'])))
                    image = requests.get("http://openweathermap.org/img/w/" + str(i['weather'][0]['icon']) + ".png",
                                         stream=True)
                    kk += 1
                    with open("photos/file" + str(kk) + ".png", "wb") as l:
                        l.write(image.content)
                if cure_date == '21:00:00':
                    temple += '\nНОЧЬ\n// '
                    temple += str(i['weather'][0]['description']) + ', температура: ' + str(
                        round(i['main']['temp_min'])) \
                              + ' - ' + str(round(i['main']['temp_max'])) + 'ºC\n// Давление: ' + str(
                        pressure(int(i['main']['pressure']))) \
                              + ' мм рт. ст., влажность: ' + str(i['main']['humidity']) + '%\n// Ветер: ' + str(
                        bofort_scale(int(i['wind']['speed']))) + ', ' \
                              + str(round(i['wind']['speed'])) + ' м/с, ' + str(wind_rumb(int(i['wind']['deg'])))
                    image = requests.get("http://openweathermap.org/img/w/" + str(i['weather'][0]['icon']) + ".png", stream=True)
                    kk += 1
                    with open("photos/file" + str(kk) + ".png", "wb") as l:
                        l.write(image.content)

        photos(event, vk, vk_session, 'Погода в Москве сегодня')
        return temple


    except Exception as e:
        print("Exception (find):", e)
        pass
        return 0

def weather_next_day(event, vk, vk_session):
    try:
        upload = VkUpload(vk_session)
        with open("weather.json", "r") as read_file:
            data = json.load(read_file)
        today = date.today()
        today = today + timedelta(1)
        temple = '/ '
        for i in data['list']:
            date_temp = str(re.findall('^\d\d\d\d[-]\d\d[-]\d\d', str(i['dt_txt'])))
            date_temp = date_temp[2:-2]
            cure_date = str(re.findall('\d\d[:]\d\d[:]\d\d', str(i['dt_txt'])))
            cure_date = cure_date[2:-2]
            if str(date_temp) == str(today) and (cure_date == '09:00:00' or cure_date == '15:00:00' or cure_date == '18:00:00' or cure_date == '21:00:00'):
                if round(i['main']['temp']) < 10 and round(i['main']['temp']) >= 0:
                    temple += '+' + str(round(i['main']['temp'])) + '°С // '
                else:
                    temple += str(round(i['main']['temp'])) + '°С // '
        temple = temple[:-2]
        temple += '\n\n'
        kk = 0
        for i in data['list']:
            date_temp = str(re.findall('^\d\d\d\d[-]\d\d[-]\d\d', str(i['dt_txt'])))
            date_temp = date_temp[2:-2]
            cure_date = str(re.findall('\d\d[:]\d\d[:]\d\d', str(i['dt_txt'])))
            cure_date = cure_date[2:-2]

            if str(date_temp) == str(today):
                if cure_date == '09:00:00':
                    temple += '\nУТРО\n// '
                    temple += str(i['weather'][0]['description']) + ', температура: ' + str(
                        round(i['main']['temp_min'])) \
                              + ' - ' + str(round(i['main']['temp_max'])) + 'ºC\n// Давление: ' + str(
                        pressure(int(i['main']['pressure']))) \
                              + ' мм рт. ст., влажность: ' + str(i['main']['humidity']) + '%\n// Ветер: ' + str(
                        bofort_scale(int(i['wind']['speed']))) + ', ' \
                              + str(round(i['wind']['speed'])) + ' м/с, ' + str(wind_rumb(int(i['wind']['deg'])))
                    image = requests.get("http://openweathermap.org/img/w/" + str(i['weather'][0]['icon']) + ".png",
                                         stream=True)
                    kk += 1
                    with open("photos/file" + str(kk) + ".png", "wb") as f:
                        f.write(image.content)
                if cure_date == '15:00:00':
                    temple += '\nДЕНЬ\n// '
                    temple += str(i['weather'][0]['description']) + ', температура: ' + str(
                        round(i['main']['temp_min'])) \
                              + ' - ' + str(round(i['main']['temp_max'])) + 'ºC\n// Давление: ' + str(
                        pressure(int(i['main']['pressure']))) \
                              + ' мм рт. ст., влажность: ' + str(i['main']['humidity']) + '%\n// Ветер: ' + str(
                        bofort_scale(int(i['wind']['speed']))) + ', ' \
                              + str(round(i['wind']['speed'])) + ' м/с, ' + str(wind_rumb(int(i['wind']['deg'])))
                    image = requests.get("http://openweathermap.org/img/w/" + str(i['weather'][0]['icon']) + ".png",
                                         stream=True)
                    kk += 1
                    with open("photos/file" + str(kk) + ".png", "wb") as f:
                        f.write(image.content)
                if cure_date == '18:00:00':
                    temple += '\nВЕЧЕР\n// '
                    temple += str(i['weather'][0]['description']) + ', температура: ' + str(
                        round(i['main']['temp_min'])) \
                              + ' - ' + str(round(i['main']['temp_max'])) + 'ºC\n// Давление: ' + str(
                        pressure(int(i['main']['pressure']))) \
                              + ' мм рт. ст., влажность: ' + str(i['main']['humidity']) + '%\n// Ветер: ' + str(
                        bofort_scale(int(i['wind']['speed']))) + ', ' \
                              + str(round(i['wind']['speed'])) + ' м/с, ' + str(wind_rumb(int(i['wind']['deg'])))
                    image = requests.get("http://openweathermap.org/img/w/" + str(i['weather'][0]['icon']) + ".png",
                                         stream=True)
                    kk += 1
                    with open("photos/file" + str(kk) + ".png", "wb") as f:
                        f.write(image.content)
                if cure_date == '21:00:00':
                    temple += '\nНОЧЬ\n// '
                    temple += str(i['weather'][0]['description']) + ', температура: ' + str(
                        round(i['main']['temp_min'])) \
                              + ' - ' + str(round(i['main']['temp_max'])) + 'ºC\n// Давление: ' + str(
                        pressure(int(i['main']['pressure']))) \
                              + ' мм рт. ст., влажность: ' + str(i['main']['humidity']) + '%\n// Ветер: ' + str(
                        bofort_scale(int(i['wind']['speed']))) + ', ' \
                              + str(round(i['wind']['speed'])) + ' м/с, ' + str(wind_rumb(int(i['wind']['deg'])))
                    image = requests.get("http://openweathermap.org/img/w/" + str(i['weather'][0]['icon']) + ".png",
                                         stream=True)
                    kk += 1
                    with open("photos/file" + str(kk) + ".png", "wb") as f:
                        f.write(image.content)

        photos(event, vk, vk_session, 'Погода в Москве завтра')
        return temple


    except Exception as e:
        print("Exception (find):", e)
        pass

def keyboard_vk_raspisanie(vk, event):
    global info_professor_or_group
    info_professor_or_group = True
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('на сегодня', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('на завтра', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()  # переход на вторую строку
    keyboard.add_button('на эту неделю', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('на следующую неделю', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()  # переход на третью строку
    keyboard.add_button('какая неделя?', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('какая группа?', color=VkKeyboardColor.SECONDARY)
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Показываю расписание'
    )

def keyboard_vk_main(vk, event):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Показать расписание', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Прогноз погоды', color=VkKeyboardColor.POSITIVE)
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Главная клавиатура'
    )

def keyboard_vk_weather(vk, event):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('сейчас', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('сегодня', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('завтра', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()  # переход на вторую строку
    keyboard.add_button('на 5 дней', color=VkKeyboardColor.POSITIVE)
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Прогноз погоды'
    )

def raspisanie(week, group, data):
    day_of_week = int(datetime.weekday(data))
    if day_of_week < 6:
        data1 = {}
        global info_professor_or_group
        if info_professor_or_group:
            with open("curs.json", "r") as read_file:
                data1 = json.load(read_file)
            tmp = ''
            for i in data1:
                if i == group:
                    tmp = data1[i][str(week)][str(day_of_week)]
                    break

            if tmp == '':
                return 'Расписание вашей группы не найдено.\nПроверьте корректность введенной группы!'
        else:
            with open("professor.json", "r") as read_file:
                data1 = json.load(read_file)
            global name_of_professor
            tmp = ''
            for i in data1:
                if i == name_of_professor:
                    tmp = data1[i][str(week)][str(day_of_week)]
                    break
        if tmp != '' and info_professor_or_group == False:
            temple = 'Расписание преподавателя ' + name_of_professor.title() +  ' на ' \
                     + ' ' + str(data.day) + ' ' + str(mounth_of_year[str(data.month)]) + ' ' + '\n' + '\n'
            for i in range(0, 6, 1):
                if tmp[str(i)] != '':
                    temple += str(i + 1) + ') ' + tmp[str(i)][0] + ',  ' + tmp[str(i)][1] + ', ' + tmp[str(i)][2] + ', ' + tmp[str(i)][3] + '\n'
                else:
                    temple += str(i + 1) + ') ' + '-\n'

            return temple
        if tmp == '' and info_professor_or_group == False:
            return 'Преподаватель отсутствует'
        if tmp != '' and info_professor_or_group:
            temple = 'Расписание на ' \
                     + ' ' + str(data.day) + ' ' + str(mounth_of_year[str(data.month)]) + ' ' + '\n' + '\n'
            for i in range(0, 6, 1):
                if tmp[str(i)] != '':
                    temple += str(i + 1) + ') ' + tmp[str(i)][0] + ',  ' + tmp[str(i)][1] + ', ' + tmp[str(i)][2] + ', ' + tmp[str(i)][3] + '\n'
                else:
                    temple += str(i + 1) + ') ' + '-\n'

            return temple
        return 'Выбранная вами группа отсутствует'
    else:
        return 'Сегодня воскресенье, пар нет!'

def raspisanie_from(group, day):
    group = group.lower()
    if day < 6:
        tmp1 = ''
        tmp2 = ''
        data_ = ''
        with open("curs.json", "r") as read_file:
            data_ = json.load(read_file)

        for i in data_:
            if i == group:
                tmp1 = data_[i]['0'][str(day)]
                tmp2 = data_[i]['1'][str(day)]
                break


        if tmp1 == '':
            return 'Расписание вашей группы не найдено.\nПроверьте корректность введенной группы!'

        else:
            temple = 'Расписание на ' + str(day_of_the_week[str(day)]) \
                     + ' чётной недели\n'
            for i in range(0, 6, 1):
                if tmp1[str(i)] != '':
                    temple += str(i + 1) + ') ' + tmp1[str(i)][0] + ', ' + tmp1[str(i)][1] + ', ' + tmp1[str(i)][2] + ', ' + tmp1[str(i)][3] + '\n'
                else:
                    temple += str(i + 1) + ') ' + '-\n'

            temple += '\nРасписание на ' + str(day_of_the_week[str(day)]) \
                     + ' нечётной недели\n'
            for i in range(0, 6, 1):
                if tmp2[str(i)] != '':
                    temple += str(i + 1) + ') ' + tmp2[str(i)][0] + ', ' + tmp2[str(i)][1] + ', ' + tmp2[str(i)][2] + ', ' + tmp2[str(i)][3] + '\n'
                else:
                    temple += str(i + 1) + ') ' + '-\n'

            return temple


    else:
        return 'Сегодня воскресенье, пар нет!'

def main():
    current_datetime = datetime.now()
    week = date(year=current_datetime.year, month=current_datetime.month, day=current_datetime.day).isocalendar()[1]
    vk_session = vk_api.VkApi(token='59c5cb35bb3da23560e805ad563bad774d39912c90ade0399368844eb09b78aa2981f7222ddf444a3e4c4')
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    print('I\'m ready!')
    week_bool = False
    user_id_ = 1
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            cnt = False
            for i in list_of_users:
                if str(i) == str(event.user_id):
                    cnt = True
            if re.findall('^\w\w\w\w[-]\d\d[-]\d\d', str(event.text)):
                vk.messages.send(
                    user_id = event.user_id,
                    random_id = get_random_id(),
                    message = 'Я запомнил, что ты из группы ' + str(event.text)
                )
                even_or_odd_week = 1
                if int(week - 5) % 2 == 0:
                    even_or_odd_week = 0
                list_of_users[str(event.user_id)] = []
                list_of_users[str(event.user_id)].append(str(event.text.lower()))
                list_of_users[str(event.user_id)].append(str(even_or_odd_week))
                with open("list_of_users.json", "w") as write_file:
                    json.dump(list_of_users, write_file)
            elif cnt == False:
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message='У вас не указана группа. \nВведите полное название своей группы в формате "****-**-**"'
                )
                group_bool = True
            elif event.text.lower() == 'бот':
                keyboard_vk_raspisanie(vk, event)
                #
            elif event.text.lower() == 'показать расписание':
                keyboard_vk_raspisanie(vk, event)
            elif event.text.lower() == 'начать':
                keyboard_vk_main(vk, event)
                #
            elif event.text.lower() == 'погода':
                temple = weather_day(event, vk, vk_session, 0)
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=temple
                )
            elif event.text.lower() == 'прогноз погоды':
                keyboard_vk_weather(vk, event)
                #
            elif event.text.lower() == 'сейчас':
                temple = weather_day(event, vk, vk_session, 1)
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=temple
                )
            elif event.text.lower() == 'сегодня':
                temple = weather_today(event, vk, vk_session)
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=temple
                )
            elif event.text.lower() == 'завтра':
                temple = weather_next_day(event, vk, vk_session)
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=temple
                )
            elif event.text.lower() == 'на 5 дней':
                temple = weather_week(event, vk, vk_session)
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=temple
                )
            elif event.text.lower() == 'корона':
                parth_coronavirus_for_all(event, vk, vk_session)
            elif re.findall('корона [\w]+', str(event.text.lower())):
                region = re.findall('корона ([\w]+)', str(event.text.lower()))
                parth_coronavirus_for_city(region[0], event, vk, vk_session)
            elif re.findall('бот \w\w\w\w[-]\d\d[-]\d\d', str(event.text.lower())):
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message='Показать расписание группы ' + str(event.text)
                )
                even_or_odd_week = 1
                if int(week - 5) % 2 == 0:
                    even_or_odd_week = 0
                list_of_users[str(event.user_id)] = []
                list_of_users[str(event.user_id)].append(str(event.text))
                list_of_users[str(event.user_id)].append(str(even_or_odd_week))
                with open("list_of_users.json", "w") as write_file:
                    json.dump(list_of_users, write_file)
                keyboard_vk_raspisanie(vk, event)
            elif re.findall('бот [\w]+ \w\w\w\w[-]\d\d[-]\d\d', str(event.text.lower())):
                day = str(re.findall('бот ([\w]+) \w\w\w\w[-]\d\d[-]\d\d', str(event.text.lower())))
                day = day[2:-2]
                try:
                    day = int(day_of_the_week_name[day])
                    even_or_odd_week = 1
                    group_ = str(re.findall('бот [\w]+ (\w\w\w\w[-]\d\d[-]\d\d)', str(event.text.lower())))
                    group = str(group_[2:-2])
                    temple = raspisanie_from(group, day)
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=temple
                    )
                except:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message='Возникла ошибка'
                    )
            elif re.findall('найти \w+', str(event.text.lower())):
                name__ = str(re.findall('найти (\w+)', str(event.text.lower())))
                name__ = name__[2:-2]
                professors_(name__, event, vk, vk_session)
            elif event.text.lower() == 'на сегодня':
                today = date.today()
                temple = raspisanie(list_of_users[str(event.user_id)][1], list_of_users[str(event.user_id)][0], today)
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=temple
                )
            elif event.text.lower() == 'на завтра':
                today = date.today() + timedelta(1)
                temple = raspisanie(list_of_users[str(event.user_id)][1], list_of_users[str(event.user_id)][0], today)
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=temple
                )
            elif event.text.lower() == 'на эту неделю':
                temple = ''
                mondey = date.today() + timedelta(days=-date.today().weekday())
                for j in range(0, 6, 1):
                    today = mondey + timedelta(j)
                    temple += raspisanie(list_of_users[str(event.user_id)][1], list_of_users[str(event.user_id)][0], today) + '\n'

                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=temple
                )
            elif event.text.lower() == 'на следующую неделю':
                temple = ''
                mondey_ = date.today() + timedelta(days=-date.today().weekday())
                mondey = mondey_ + timedelta(7)
                week__ = 1
                if list_of_users[str(event.user_id)][1] == '1':
                    week__ = 0
                for j in range(0, 6, 1):
                    today = mondey + timedelta(j)
                    temple += raspisanie(week__, list_of_users[str(event.user_id)][0], today) + '\n'

                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=temple
                )
            elif event.text.lower() == 'какая неделя?':
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message='Идёт ' + str(week - 5) + ' неделя'
                )
            elif event.text.lower() == 'какая группа?':
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message='Показываю расписание группы ' + str(list_of_users[str(event.user_id)][0].upper())
                )
            elif re.findall('\w+ \w.\w', str(event.text.lower())):
                name = str(event.text.lower())
                find_professors(name, event, vk, vk_session)
            else:
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message='Неизвестная команда'
                )

def specific(strl):
    n = len(strl)
    strl = strl[n:] + strl[:n - 1]
    n -= 1
    strl = strl[n:] + strl[:n - 1]
    n -= 1
    strl = strl[n:] + strl[:n - 1]
    n -= 1
    strl = strl[n:] + strl[:n - 1]
    return strl

def write_str_correct(strl):
    strl = strl[:0] + strl[0 + 1:]
    strl = strl[:0] + strl[0 + 1:]
    n = len(strl)
    strl = strl[n:] + strl[:n - 1]
    n -= 1
    strl = strl[n:] + strl[:n - 1]
    return strl

def clean(names):
    site = r"[A-Я][а-я]+ +[А-Я]\. *[А-Я]"
    new_names = []
    try:
        re.search(site, names)
        while re.search(site, names):
            elem = (re.search(site, names)).group(0)
            new_names.append(elem.split()[0] + " " + ''.join(elem.split()[1:]))
            return new_names
    except:
        return None

def params_():
    return {"0": {"0": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "1": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "2": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "3": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "4": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "5": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""}},
            "1": {"0": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "1": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "2": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "3": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "4": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""},
                  "5": {"0": "", "1": "", "2": "", "3": "", "4": "", "5": ""}}}

def soup():
    page = requests.get("https://www.mirea.ru/schedule/")
    soup = BeautifulSoup(page.text, "html.parser")
    result = soup.find("div", {"class": "rasspisanie"}). \
        find(string="Институт информационных технологий"). \
        find_parent("div"). \
        find_parent("div"). \
        findAll('a', href=True)  # получить ссылки
    k = 1
    array_of_links = []
    link_itog = ''
    for x in result:
        strl = ''
        if re.findall('[^Зач_]ИИТ_[1, 2, 3]', str(x)):
            strl = str(re.findall(r'href="[\'"]?([^\'" >]+)', str(x)))
            strl = write_str_correct(strl)
            parse_part = str(re.findall(r'ИИТ[_\.\-\w]+', str(strl)))
            parse_part = write_str_correct(parse_part)
            main_strl_part = str(re.split(parse_part, str(strl)))
            main_strl_part = write_str_correct(main_strl_part)
            main_strl_part = specific(main_strl_part)
            link_tab = urllib.parse.quote(str(parse_part), safe='')
            link_itog = str(main_strl_part + link_tab)
            array_of_links.append(link_itog)

            f = open("file" + str(k) + ".xlsx", "wb")  # открываем файл для записи, в режиме wb
            resp = requests.get(link_itog)  # запрос по ссылке
            f.write(resp.content)
            k += 1

    group_of_curs = {}
    group_of_professor = {}
    for i in range(1, 4, 1):
        book = xlrd.open_workbook(str("file" + str(i) + ".xlsx"))  # открытие файла
        sheet = book.sheet_by_index(0)  # первый лист
        num_cols = sheet.ncols  # количество столбцов
        for x in range(7, num_cols, 5):
            week_ = params_()
            for y in range(3, 75, 2):
                if clean(sheet.cell(y, x).value):
                    temp = clean(sheet.cell(y, x).value)
                    for name__ in temp:
                        if name__.lower() not in group_of_professor.keys():
                            group_of_professor[name__.lower()] = params_()

                    for name__ in temp:
                        if name__.lower() in group_of_professor.keys():
                            day_ = 0
                            count = 0
                            if y <= 14:
                                day_ = 0
                            if y <= 26 and y > 14:
                                day_= 1
                            if y <= 38 and y > 26:
                                day_ = 2
                            if y <= 50 and y > 38:
                                day_ = 3
                            if y <= 62 and y > 50:
                                day_ = 4
                            if y <= 74 and y > 62:
                                day_ = 5
                            if y - day_ * 12 == 3:
                                count = 0
                            if y - day_ * 12 == 5:
                                count = 1
                            if y - day_ * 12 == 7:
                                count = 2
                            if y - day_ * 12 == 9:
                                count = 3
                            if y - day_ * 12 == 11:
                                count = 4
                            if y - day_ * 12 == 13:
                                count = 5

                            temples = []
                            first = str(sheet.cell(y, x - 2).value)
                            first = first.replace('\n', ' ')
                            second = str(sheet.cell(1, x - 2).value)
                            second = second.replace('\n', ' ')
                            third = str(sheet.cell(y, x - 1).value)
                            third = third.replace('\n', ' ')
                            fourth = str(sheet.cell(y, x + 1).value)
                            fourth = fourth.replace('\n', ' ')
                            temples.append(first)
                            temples.append(second)
                            temples.append(third)
                            temples.append(fourth)
                            group_of_professor[name__.lower()]['0'][str(day_)][str(count)] = temples
                if sheet.cell(y, x - 2).value != '':
                    day_ = 0
                    count = 0
                    if y <= 14:
                        day_ = 0
                    if y <= 26 and y > 14:
                        day_ = 1
                    if y <= 38 and y > 26:
                        day_ = 2
                    if y <= 50 and y > 38:
                        day_ = 3
                    if y <= 62 and y > 50:
                        day_ = 4
                    if y <= 74 and y > 62:
                        day_ = 5
                    if y - day_ * 12 == 3:
                        count = 0
                    if y - day_ * 12 == 5:
                        count = 1
                    if y - day_ * 12 == 7:
                        count = 2
                    if y - day_ * 12 == 9:
                        count = 3
                    if y - day_ * 12 == 11:
                        count = 4
                    if y - day_ * 12 == 13:
                        count = 5
                    temples = []
                    first = str(sheet.cell(y, x - 2).value)
                    first = first.replace('\n', ' ')
                    second = str(sheet.cell(y, x).value)
                    second = second.replace('\n', ' ')
                    third = str(sheet.cell(y, x - 1).value)
                    third = third.replace('\n', ' ')
                    fourth = str(sheet.cell(y, x + 1).value)
                    fourth = fourth.replace('\n', ' ')
                    temples.append(first)
                    temples.append(second)
                    temples.append(third)
                    temples.append(fourth)
                    week_['0'][str(day_)][str(count)] = temples

            for y in range(4, 76, 2):

                if clean(sheet.cell(y, x).value):
                    temp = clean(sheet.cell(y, x).value)
                    for name__ in temp:
                        if name__.lower() not in group_of_professor.keys():
                            group_of_professor[name__.lower()] = params_()

                    for name__ in temp:
                        if name__.lower() in group_of_professor.keys():
                            day_ = 0
                            count = 0
                            if y <= 14:
                                day_ = 0
                            if y <= 26 and y > 14:
                                day_ = 1
                            if y <= 38 and y > 26:
                                day_ = 2
                            if y <= 50 and y > 38:
                                day_ = 3
                            if y <= 62 and y > 50:
                                day_ = 4
                            if y <= 74 and y > 62:
                                day_ = 5
                            if y - day_ * 12 == 4:
                                count = 0
                            if y - day_ * 12 == 6:
                                count = 1
                            if y - day_ * 12 == 8:
                                count = 2
                            if y - day_ * 12 == 10:
                                count = 3
                            if y - day_ * 12 == 12:
                                count = 4
                            if y - day_ * 12 == 14:
                                count = 5

                            temples = []
                            first = str(sheet.cell(y, x - 2).value)
                            first = first.replace('\n', ' ')
                            second = str(sheet.cell(1, x - 2).value)
                            second = second.replace('\n', ' ')
                            third = str(sheet.cell(y, x - 1).value)
                            third = third.replace('\n', ' ')
                            fourth = str(sheet.cell(y, x + 1).value)
                            fourth = fourth.replace('\n', ' ')
                            temples.append(first)
                            temples.append(second)
                            temples.append(third)
                            temples.append(fourth)
                            group_of_professor[name__.lower()]['1'][str(day_)][str(count)] = temples
                if sheet.cell(y, x - 2).value != '':
                    day_ = 0
                    count = 0
                    if y <= 14:
                        day_ = 0
                    if y <= 26 and y > 14:
                        day_ = 1
                    if y <= 38 and y > 26:
                        day_ = 2
                    if y <= 50 and y > 38:
                        day_ = 3
                    if y <= 62 and y > 50:
                        day_ = 4
                    if y <= 74 and y > 62:
                        day_ = 5
                    if y - day_ * 12 == 4:
                        count = 0
                    if y - day_ * 12 == 6:
                        count = 1
                    if y - day_ * 12 == 8:
                        count = 2
                    if y - day_ * 12 == 10:
                        count = 3
                    if y - day_ * 12 == 12:
                        count = 4
                    if y - day_ * 12 == 14:
                        count = 5
                    temples = []
                    first = str(sheet.cell(y, x - 2).value)
                    first = first.replace('\n', ' ')
                    second = str(sheet.cell(y, x).value)
                    second = second.replace('\n', ' ')
                    third = str(sheet.cell(y, x - 1).value)
                    third = third.replace('\n', ' ')
                    fourth = str(sheet.cell(y, x + 1).value)
                    fourth = fourth.replace('\n', ' ')
                    temples.append(first)
                    temples.append(second)
                    temples.append(third)
                    temples.append(fourth)
                    week_['1'][str(day_)][str(count)] = temples

            if re.findall('\w\w\w\w[-]\d\d[-]\d\d', str(sheet.cell(1, x - 2).value)):
                group_of_curs[str(sheet.cell(1, x - 2).value.lower())] = week_

    with open("curs.json", "w") as write_file:
        json.dump(group_of_curs, write_file)
    with open("professor.json", "w") as write_file:
        json.dump(group_of_professor, write_file)

if __name__ == '__main__':
    parth_coronavirus()
    parth_weather()
    soup()
    main()
