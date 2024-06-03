import requests
import json
from pprint import pprint

#открываем файл credentials.json для получения данных о токенах VK и Yandex, user_id
with open('credentials.json', 'r') as file:
    s = json.load(file)
    access_token = s['access_token'] #VK токен
    yandex_polygon_token = s['yandex_polygon_token'] #Yandex токен

class VK:
    API_BASE_URL = 'https://api.vk.com/method'
    YANDEX_DRIVE_URL = 'https://cloud-api.yandex.net/v1/disk'

    def __init__(self, access_token, user_id, version='5.236'):
        self.token = access_token
        self.id = user_id
        self.version = version

    #метод, который будет возварщать параметры
    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.236'
        }

    #метод, который будет возвращать результат обращения к фото стены
    def get_wall_photos(self):
        params = self.get_common_params()
        params.update({'owner_id': self.id,'album_id': 'wall','extended': '1'})
        response_wall = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        result = response_wall.json()
        return result

    #метод, который будет возвращать результат обращения к фото профиля
    def get_photos(self):
        params = self.get_common_params()
        params.update({'owner_id': self.id, 'album_id': 'profile','extended': '1'})
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        result = response.json()
        return result

    #метод, который будет обрабатывать фото, обращаться к фото, переименовывать, формировать результирующие файлы
    def processing_photos(self,result,folder):
        list_of_names = [] #создаем список, в который будем помещать имена файлов. Имя файла - это количество лайков
        json_result = [] #сюда будем помещать информацию о фото. В нашем случае имя файла и размер

        # разбор результата
        count_photos = result['response']['count']  # кол-во фото в профиле
        if count_photos > 15: #ограничим кол-во фото 15
            count_photos = 15
        print(f'Количество фото: {count_photos}')

        for i in range(count_photos): #запускаем цикл дя указанного/полученного кол-ва фото
            print(f'Обрабатывается фото: {i + 1} из {count_photos}') #некое информирование пользователя о прогрессе
            photo_details = {} # сюда будем помещать имя файла и его размер
            number_of_likes = result['response']['items'][i]['likes']['count']  # вытаскиваем кол-во лайков, не своих
            date_of_creation = result['response']['items'][i]['date']  # вытаскиваем дату создания
            photo_list = result['response']['items'][i]['sizes']  # получаем общий список фото во всех разрешениях
            max_file_height = 0
            max_file_width = 0
            #поиск фото с максимальными шириной и высотой, которое будем считать максимальным
            for images in photo_list:
                file_height = images['height'] #получаем высоты изображения
                file_width = images['width'] #получаем ширину изображения
                #сравниваем полученные значения, и если условие выполняется, 
                #то вытаскиваем ссылку для последующего запроса, а также типоразмер изображения
                if file_height > max_file_height and file_width > max_file_width:
                    max_file_height = file_height
                    max_file_width = file_width
                    link = images['url']  # получаем только ссылку
                    file_size = images['type'] #типоразмер изображения
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
            response_1 = requests.get(link) #передаем ссылку с максимальным разрешением фото для получения результата

            # сохранения фото в макс разрешении с именем кол-во лайков на локальный диск
            #if response_1.status_code == 200:
            #    with open(file_name_to_save, 'wb') as f:
            #        f.write(response_1.content)

            # сохранения фото в макс разрешении с именем кол-во лайков на диск яндекс
            # если успешно, то вызываем метод сохранения файла на Яндекс диск, в который передаем ссылку, имя файла и имя папки
            if response_1.status_code == 200:
                vk.file_saving(link, file_name_to_save,folder)

        return json_result

    #метод создания папки на Яндекс диск для хранения фото из профиля
    def yandex_folder_creation(self,folder):
        yandex_params = {'path': folder}
        headers = {'Authorization': yandex_polygon_token}
        yandex_response = requests.put(f'{self.YANDEX_DRIVE_URL}/resources',
                                       params=yandex_params,
                                       headers=headers)
        return yandex_response.status_code

    # метод создания папки на Яндекс диск для хранения фото со стены
    def yandex_wall_folder_creation(self,folder):
        yandex_params = {'path': folder}
        headers = {'Authorization': yandex_polygon_token}
        yandex_wall_response = requests.put(f'{self.YANDEX_DRIVE_URL}/resources',
                                       params=yandex_params,
                                       headers=headers)
        return yandex_wall_response.status_code

    #метод сохранения фото на Яндекс диске
    def file_saving(self, link, file_name,folder):
        yandex_params = {'path': f'{folder}/{file_name}'}
        yandex_params.update({'url': link})
        headers = {'Authorization': yandex_polygon_token}
        response_to_save = requests.post(f'{self.YANDEX_DRIVE_URL}/resources/upload',
                                         params=yandex_params,
                                         headers=headers)

if __name__ == '__main__':
    #просим пользователя ввести ИД пользователя в VK
    user_id = input('Укажите ИД пользователя в VK:\n')
    vk = VK(access_token, user_id)
    #предоставляем возможность пользователю выбрать откуда сохранить фото: 0 - Из профиля, 1 - Cо стены
    place_selection = int(input('Укажите откуда взять фото для копирования: 0 - Profile, 1 - Wall\n'))

    #в зависимости от того, что ввел пользователь - 0 или 1, выполняем код
    if place_selection == 0:
        # сначала создадим папку на яндекс диске вызвав метод создания
        # если папка успешно создана, вызываем метод получения фото с VK профиля
        # и помещаем результат выполенения в переменную result
        if vk.yandex_folder_creation('VKProfilePhotos') == 201 or vk.yandex_folder_creation('VKProfilePhotos') == 409:
            result = vk.get_photos()
            #по окончании выполнения перемещения фото с VK на Яндекс, записываем в файл информацию
            # о результате выполнения метода processing_photos
            with open('vk_to_yandex_profile.json', 'w+') as f:
                f.write(json.dumps(vk.processing_photos(result,'VKProfilePhotos'), indent=2))
            print("Обработка завершена")
        else:
            print('Неизвестная ошибка')
    else:
        #выполняем те же проверки и действия в случае выбора пользователем 1 - Wall
        if vk.yandex_wall_folder_creation('VKWallPhotos') == 201 or vk.yandex_wall_folder_creation('VKWallPhotos') == 409:
            result = vk.get_wall_photos()
            with open('vk_to_yandex_wall.json', 'w+') as f:
                f.write(json.dumps(vk.processing_photos(result,'VKWallPhotos'), indent=2))
            print("Обработка завершена")
        else:
            print('Неизвестная ошибка')
