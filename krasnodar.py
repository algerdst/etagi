import requests
import json
import csv
import time
from datetime import datetime
from random import randint
from bs4 import BeautifulSoup
from urllib.parse import unquote

# поля в итоговой таблице exel
fields = ['ID', 'Номер объекта', 'ID_1', 'Пользователь', 'Связь', 'Тип сделки', 'Форма', 'Назначение',
          'Месторасположение', 'Количество комнат', 'Площадь', 'Cтоймость', 'Фото1', 'Фото2', 'Фото3', 'Описание',
          'Количество номеров', 'Cрок окупаемости'
          ]
# возможные типы недвижимости
types_of_commerce = {
    'office': 'Офис',
    'torg': 'Торговое помещение',
    'other': 'Свободное назначение',
    'dev': 'Производство',
    'sklad': 'Склад',
    'dev_land': 'Земля под производство',
    'land': 'Земельный участок',
    'base': 'База',
    'busines': 'Готовый бизнес',
    'flat': 'Квартира',
    'apart': 'Апартаменты/Студия',
    'malosem': 'Малосемейка',
    'house': 'Дом',
    'garden': 'Дача',
    'townhouse': 'Таунхаус',
    'garage_type': 'Гараж',
    'room': 'Комната',
    'obshaga': 'Общежитие',
    'cottage': 'Коттедж',
}
#этот словарь нужен для последующего формирования ссылки на карточку объекта
links_dict = {
    0: 'https://krasnodar.etagi.com/realty/',
    1: 'https://krasnodar.etagi.com/realty_out/',
    2: 'https://krasnodar.etagi.com/realty_rent/',
    3: 'https://krasnodar.etagi.com/commerce/',
}
# список со ссылками на категории(квартиры, дома и т.д)
urls = [
    'https://krasnodar.etagi.com/rest/plugin.etagi?protName=flatsWithCharacteristics&fields&filter=%5B%22and%22%2C%5B%5B%22in%7C%3D%22%2C%22f.city_id%22%2C%5B223%5D%5D%2C%5B%22%3D%22%2C%22class%22%2C%22flats%22%5D%2C%5B%22in%22%2C%22status%22%2C%5B%22active%22%2C%22sold%22%5D%5D%5D%5D&order=%5B%22(CASE%20WHEN%20f.premium_status_id%20IN%20(224%2C227%2C278%2C280)%20THEN%201%20WHEN%20f.premium_status_id%20IN%20(225%2C228%2C279)%20THEN%202%20ELSE%20NULL%20END)%20ASC%20NULLS%20LAST%22%2C%22f.premium_start_max%20DESC%22%2C%22array_position(array%24%2Cf.object_id)%22%2C%22vladis_external_id%20desc%22%2C%22coalesce(f.partner_realization_id%2C0)%20in%20(14%2C15%2C16%2C17%2C18%2C19%2C20)%20desc%22%2C%22f.contract_type%3D%27exclusive%27%20DESC%20NULLS%20LAST%22%2C%22(visual%20is%20null)%22%2C%22f.prof_photo%3D%27f%27%22%2C%22f.date_rise%20desc%22%2C%22f.date_update%20desc%22%2C%22f.object_id%20desc%22%5D&orderId=default&limit=30&offset=0&as=f&join&lang=ru&caseFilters=%7B%7D&bAddLimit=0&bIsFunction=0&cityId=223&module=with-nh-and-archive&countryISO=RU&sourceTable=etagi.flats&resetOrders=default&getAdvanced=true&withBotDescription=false&recommendedMode=client&domainId=223&valueToSort=%5B9963238%2C9588629%2C8845768%2C7459402%2C9690578%2C9192282%2C9608731%2C7739776%2C9940624%2C9906185%5D&count=1',
    'https://krasnodar.etagi.com/rest/plugin.etagi?protName=cottagesWithCharacteristics&fields&filter=%5B%22and%22%2C%5B%5B%22in%7C%3D%22%2C%22f.city_id%22%2C%5B223%5D%5D%2C%5B%22in%22%2C%22f.status%22%2C%5B%22active%22%2C%22sold%22%2C%22rent%22%2C%22rent_o_agency%22%5D%5D%2C%5B%22%3D%22%2C%22f.action_sl%22%2C%22sale%22%5D%2C%5B%22%3D%22%2C%22class%22%2C%22cottages%22%5D%5D%5D&order=%5B%22(CASE%20WHEN%20f.premium_status_id%20IN%20(224%2C227%2C278%2C280)%20THEN%201%20WHEN%20f.premium_status_id%20IN%20(225%2C228%2C279)%20THEN%202%20ELSE%20NULL%20END)%20ASC%20NULLS%20LAST%22%2C%22f.premium_start_max%20DESC%22%2C%22array_position(array%24%2Cf.object_id)%22%2C%22vladis_external_id%20desc%22%2C%22(visual%20is%20null)%22%2C%22f.prof_photo%3D%27f%27%22%2C%22f.date_create%20desc%22%2C%22f.date_rise%20desc%22%2C%22f.date_update%20desc%22%2C%22f.object_id%20desc%22%5D&orderId=default&limit=30&offset=0&as=f&join&lang=ru&caseFilters=%7B%7D&bAddLimit=0&bIsFunction=0&cityId=223&module=with-nh-and-archive&countryISO=RU&sourceTable=etagi.cottages&resetOrders=default&getAdvanced=true&withBotDescription=false&recommendedMode=client&domainId=223&valueToSort=%5B8739062%2C9521629%2C9440653%2C9966029%2C9265088%2C9915032%2C9451498%2C8410413%2C9011112%2C9900952%5D&count=1',
    'https://krasnodar.etagi.com/rest/plugin.etagi?protName=rentsWithCharacteristics&fields&filter=%5B%22and%22%2C%5B%5B%22in%7C%3D%22%2C%22f.city_id%22%2C%5B223%5D%5D%2C%5B%22in%22%2C%22status%22%2C%5B%22active%22%2C%22rent%22%2C%22rent_o_agency%22%5D%5D%5D%5D&order=%5B%22(CASE%20WHEN%20f.premium_status_id%20IN%20(224%2C227%2C278%2C280)%20THEN%201%20WHEN%20f.premium_status_id%20IN%20(225%2C228%2C279)%20THEN%202%20ELSE%20NULL%20END)%20ASC%20NULLS%20LAST%22%2C%22f.premium_start_max%20DESC%22%2C%22array_position(array%24%2Cf.object_id)%22%2C%22vladis_external_id%20desc%22%2C%22f.contract_type%3D%27vozmezdnuy%27%22%2C%22(CASE%20WHEN(f.discount%20AND%20(f.old_price%20IS%20NULL%20OR%20f.old_price-f.price%3C%3D0))%20THEN%201%20ELSE%200%20END)%20desc%22%2C%22(visual%20is%20null)%22%2C%22f.prof_photo%3D%27f%27%22%2C%22f.price%3E%3D30000%20desc%22%2C%22f.date_rise%20desc%22%2C%22f.date_update%20desc%22%2C%22f.object_id%20desc%22%5D&orderId=default&limit=30&offset=0&as=f&join&lang=ru&caseFilters=%7B%7D&bAddLimit=0&bIsFunction=0&cityId=223&module=with-nh-and-archive&countryISO=RU&sourceTable=etagi.rent&resetOrders=default&getAdvanced=true&withBotDescription=false&recommendedMode=client&domainId=223&count=1',
    'https://krasnodar.etagi.com/rest/plugin.etagi?protName=commerceWithCharacteristics&fields&filter=%5B%22and%22%2C%5B%5B%22in%7C%3D%22%2C%22f.city_id%22%2C%5B223%5D%5D%2C%5B%22%3D%22%2C%22f.action_sl%22%2C%22sale%22%5D%2C%5B%22in%22%2C%22f.status%22%2C%5B%22active%22%2C%22sold%22%2C%22rent%22%2C%22rent_o_agency%22%5D%5D%5D%5D&order=%5B%22(CASE%20WHEN%20f.premium_status_id%20IN%20(224%2C227%2C278%2C280)%20THEN%201%20WHEN%20f.premium_status_id%20IN%20(225%2C228%2C279)%20THEN%202%20ELSE%20NULL%20END)%20ASC%20NULLS%20LAST%22%2C%22f.premium_start_max%20DESC%22%2C%22array_position(array%24%2Cf.object_id)%22%2C%22vladis_external_id%20desc%22%2C%22(visual%20is%20null)%22%2C%22f.prof_photo%3D%27f%27%22%2C%22f.date_update%20desc%22%2C%22f.object_id%20desc%22%5D&orderId=default&limit=30&offset=0&as=f&join&lang=ru&caseFilters=%7B%7D&bAddLimit=0&bIsFunction=0&cityId=223&module=with-nh-and-archive&countryISO=RU&sourceTable=etagi.offices&resetOrders=default&getAdvanced=true&withBotDescription=false&recommendedMode=client&domainId=223&valueToSort=%5B9304861%2C9799259%2C9983217%2C9493508%2C9817990%2C9717440%2C9351744%2C7368456%2C9837396%2C9562197%5D&count=1'
]
payload = {}
headers = {
  'authority': 'krasnodar.etagi.com',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'content-type': 'application/json; charset=utf-8',
  'referer': 'https://krasnodar.etagi.com/realty/?page=3',
  'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.931 Safari/537.36',
  'Cookie': '_ga_sync=wrokGWQ1h3h+HAAVA5BeAg=='
}
#название категорий недвижимости в соответствии с индексом url`a
categories_names={
    0:'Квартиры',
    1:'Дома и участки',
    2:'Арендная недвижимость',
    3:'Коммерческая недвижимость',

}
# ключи по которым можно найти номер дома и корпус
house_num_keys = ['house_address_number', 'house_num']

sleep = 0.1
start=time.perf_counter()
# открываю файл exel для записи
with open('krasnodar.csv', 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(fields)
    # прохожу по списку ссылок
    for url in urls:
        page = 0  # отвечает за номер страницы
        index = urls.index(url)
        number = 1
        card = 0
        while True:
            if page == 0:
                link = url
            else:
                if index==0:
                    link=url[:934]+str(page)+url[935:]
                elif index==1:
                    link=url[:897]+str(page)+url[898:]
                elif index==2:
                    link=url[:964]+str(page)+url[965:]
                elif index==3:
                    link=url[:792]+str(page)+url[793:]

            # в этом цикле пытаюсь получить ответ от сервера, ответ приходит не всегда с первого раза, поэтому закинул его в цикл while с рандомными задержками
            while True:
                try:
                    response = requests.request("GET", link, headers=headers, data=payload)
                    data = response.json()
                    break
                except Exception:
                    sleep = sleep * 2 + randint(1, 10) / 10
                    time.sleep(sleep)
                    continue
            page += 30  # для отображения следующей страницы увеличиваю page на 30
            # если переменная дата пустая, значит на этой странице ничего нет и страницы по этому url закончились, прерываю цикл
            if data['data'] == []:
                break
            else:
                time.sleep(0.5)
                for object in data['data']:
                    object_id = object['object_id']
                    print(object_id)
                    user = '@andrtazet'
                    phone = '+7(918)116-51-42'
                    # пытаюсь определить тип недвижимости, если ключ 'type' если в полученном json и значение этого ключа есть в словаре types_of_commerce, то тип определится, если нет, то ставим тип в значение 'Не определена'
                    try:
                        type = object['type']
                        purpose = types_of_commerce[type]
                    except Exception:
                        purpose = 'Остальное'
                    # определяю тип сделки. если в json существует ключ period, и он не None, то эта арендная сделка, иначе сделка по продаже
                    try:
                        rent = object['period']
                        if rent is None:
                            type_of_deal = 'Продажа'
                        else:
                            type_of_deal = 'Аренда'
                    except Exception:
                        type_of_deal = 'Продажа'
                    # Определяю форму недвижимости
                    if purpose in ['Квартира','Апартаменты/Студия','Малосемейка','Дом','Дача','Таунхаус','Комната','Общежитие','Коттедж']:
                        form='Жилая'
                    else:
                        form='Не жилая'
                    city = 'Краснодар'
                    district = object['meta']['district']
                    street = object['meta']['street']
                    if district is None:
                        district = "Регион не указан"
                    if street is None:
                        street = "Улица не указана"
                    # определяю есть ли у объекта номер дома по ключам из списка
                    for i in range(2):
                        try:
                            house_number = object[house_num_keys[i]]
                            if house_number:
                                break
                            if house_number is None:
                                house_number = ''
                                break
                        except:
                            house_number = ''
                    # определяю есть ли у объекта номер корпуса
                    try:
                        korpus = object['house_address_corpus']
                    except:
                        korpus = ""
                    if korpus is None:
                        korpus = ""
                    elif korpus:
                        korpus = f"Корпус {korpus}"
                    location = city + ' ' + district + ' ' + street + ' ' + house_number + ' ' + korpus
                    #определяю количество комнат, ключ rooms есть не везде поэтому обернул в try except
                    try:
                        rooms=object['rooms']
                    except Exception as ex:
                        rooms='-'
                    # Определяю площадь, в разных типах недвижимости, площадь находится под разными ключами
                    if type in ['flat', 'apart', 'office', 'other', 'torg', 'dev', 'busines', 'base', 'room', 'malosem',
                                'obshaga', 'garage_type']:
                        square = object['square']
                    elif type in ['house', 'garden', 'cottage', 'townhouse']:
                        square = object['area_house']
                    elif type == 'land':
                        try:
                            square = object['area_land']
                        except Exception:
                            square = object['square']
                    #определяю цену
                    price = object['price']
                    #берет ссылку на карточку товара
                    card_link = links_dict[index] + str(object_id) + "/"
                    #пытается пополучить ответ на запрос к карточке товара
                    while True:
                        try:
                            card_response = requests.request("GET", card_link, headers=headers, data=payload)
                            break
                        except Exception:
                            time.sleep(sleep)
                            sleep = sleep * 2 + randint(1, 10) / 10
                            continue
                    # --------Берет json из карточки товара----------
                    response_card = card_response.text.split('={"filters":')
                    response_card = response_card[1].split('}}}</script>')
                    result = '{"filters":' + response_card[0] + "}}}"
                    result = unquote(result)
                    data = json.loads(result)
                    data = dict(data)
                    try:
                        photos = ['https://cdn.esoft.digital/19201080' + photo['fname'] for photo in
                                  data['objects']['groupedObjectMedia']['byType']['photos']]
                    except Exception:
                        print(id)
                    photos123=[None,None,None]
                    for i in range(3):
                        try:
                            photos123[i] = photos[i]
                        except:
                            photos123[i] = 'Отсутствует'
                    if 'commerceObject' in data['objects']:
                        description = data['objects']['commerceObject']['notes']
                    elif 'flat' in data['objects']:
                        description = data['objects']['flat']['notes']
                    elif 'cottage' in data['objects']:
                        description = data['objects']['cottage']['notes']
                    elif 'garage' in data['objects']:
                        description = data['objects']['garage']['notes']
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow([object_id, '-', '-', user, phone, type_of_deal, form, purpose, location, rooms,
                                     square, price, photos123[0], photos123[1], photos123[2], description
                                     ])
                print(f"Cобрано {number} страниц с карточками недвижимости '{categories_names[index]}'")
                number += 1
finish=time.perf_counter()
print(f'Сбор данных занял {finish-start}')


