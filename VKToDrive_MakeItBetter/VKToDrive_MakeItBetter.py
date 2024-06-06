import requests
import json
import configparser
from pprint import pprint
from tqdm import tqdm
import classVK
import classYNDX

'''
Функция обработки фото, которая прнимает на вход результат выполнения метода get_photos и название папки
и возвращает в качестве результата список фотографий, состоящий из словарей с ключами file_name, которое формируется
из полученных кол-ва лайков и типоразмера фото, которое будет иметь максимальные высоту и ширину в пикселях'''
def processing_photos(result,folder):
    list_of_names = [] #создаем список, в который будем помещать имена файлов. Имя файла - это количество лайков
    json_result = [] #сюда будем помещать информацию о фото. В нашем случае имя файла и размер

    # разбор результата
    count_photos = result['response']['count']  # кол-во фото в профиле
    if count_photos > 15: #ограничим кол-во фото 15
        count_photos = 15
    print(f'Количество фото: {count_photos}')

    for i in tqdm(range(count_photos)):
#        time.sleep(1)
    #for i in range(count_photos): #запускаем цикл дя указанного/полученного кол-ва фото
        #print(f'Обрабатывается фото: {i + 1} из {count_photos}') #некое информирование пользователя о прогрессе
        photo_details = {} # сюда будем помещать имя файла и его размер
        number_of_likes = result['response']['items'][i]['likes']['count']  # вытаскиваем кол-во лайков, не своих
        date_of_creation = result['response']['items'][i]['date']  # вытаскиваем дату создания

        photo_list = result['response']['items'][i]['sizes']  # получаем общий список фото во всех разрешениях
#            link = photo_list[len(photo_list) - 1]['url']  # получаем только ссылку
        max_file_height = 0
        max_file_width = 0
        for images in photo_list:
            file_height = images['height']
            file_width = images['width']
            if file_height == 0 and file_width == 0:
                link = images['url']  # получаем только ссылку
                file_size = images['type']
            elif file_height > max_file_height and file_width > max_file_width:
                max_file_height = file_height
                max_file_width = file_width
                link = images['url']  # получаем только ссылку
                file_size = images['type']
        # переменная, которая будет сожержать имя файла, состоящего из кол-ва лайков
        # и расширения оригинального имени файла
        file_name_to_save = str(number_of_likes) + '.jpg'
        # проверяем, существует ли уже такое имя файла в наем списке имен,
        # и если уже существует, то приписываем к нему дату создания
        if file_name_to_save in list_of_names:
            file_name_to_save = f'{str(number_of_likes)}_{str(date_of_creation)}.jpg'
        # добавление имени файла в список имен файлов для имения возможности сравнить на следующей итерации
        list_of_names.append(file_name_to_save)
        photo_details.setdefault("file_name", file_name_to_save) #добавялем в словарь информацию о имени файла
        photo_details.setdefault("size", file_size) #добавялем в словарь информацию о размере файла
        json_result.append(photo_details) #добавляем информацию в общий файл- результат
        response_img_url = requests.get(link) #передаем ссылку с максимальным разрешением фото для получения результата

        # сохранения фото в макс разрешении с именем кол-во лайков на локальный диск
        #if response_img_url.status_code == 200:
        #    with open(file_name_to_save, 'wb') as f:
        #        f.write(response_img_url.content)

        # сохранения фото в макс разрешении с именем кол-во лайков на диск яндекс
        # если успешно, то вызываем метод сохранения файла на Яндекс диск, в который передаем ссылку, имя файла и имя папки
        if response_img_url.status_code == 200:
            yndx.file_saving(link, file_name_to_save,folder)

    return json_result

if __name__ == '__main__':
    config = configparser.ConfigParser()

    # Чтение файла конфигурации
    config.read('config.ini')

    # Получение данных из файла конфигурации
    access_token = config.get('Settings', 'access_token')
    yandex_polygon_token = config.get('Settings', 'yandex_polygon_token')

    folder_profile = 'VKProfilePhotos' #переменная для создания папки с фото из профайла
    folder_wall = 'VKWallPhotos' #переменная для создания папки с фото со стены

    #запрашиваем общедоступное ИД пользователя, у которого нужно скопировать фото
    user_id = input('Укажите ИД пользователя в VK:\n')

    vk = classVK.VK(access_token, user_id)
    yndx = classYNDX.YNDX(yandex_polygon_token)

    #предоставляем возможность пользователю выбрать откуда сохранить фото: 0 - Из профиля, 1 - Cо стены
    place_selection = int(input('Укажите откуда взять фото для копирования: 0 - Profile, 1 - Wall\n'))

    #в зависимости от того, что ввел пользователь - 0 или 1, выполняем код
    if place_selection == 0:
        # сначала создадим папку на яндекс диске вызвав метод создания
        # если папка успешно создана, вызываем метод получения фото с VK профиля
        # и помещаем результат выполенения в переменную result
        if yndx.yandex_folder_creation(folder_profile) == 201 or yndx.yandex_folder_creation(folder_profile) == 409:
            result = vk.get_photos('profile')
            #по окончании выполнения перемещения фото с VK на Яндекс, записываем в файл информацию
            # о результате выполнения метода processing_photos
            with open('../vk_to_yandex_profile.json', 'w+') as f:
                f.write(json.dumps(processing_photos(result,folder_profile), indent=2))
            print("Обработка завершена")
        else:
            print('Неизвестная ошибка')
    else:
        #выполняем те же проверки и действия в случае выбора пользователем 1 - Wall
        if yndx.yandex_folder_creation(folder_wall) == 201 or yndx.yandex_folder_creation(folder_wall) == 409:
            result = vk.get_photos('wall')
            with open('../vk_to_yandex_wall.json', 'w+') as f:
                f.write(json.dumps(processing_photos(result,folder_wall), indent=2))
            print("Обработка завершена")
        else:
            print('Неизвестная ошибка')