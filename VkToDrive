import requests
import json
from pprint import pprint

#открываем файл credentials.json для получения данных о токенах VK и Yandex, user_id
with open('credentials.json', 'r') as file:
    s = json.load(file)
    access_token = s['access_token'] #VK токен
    user_id = s['user_id'] #VK ID
    yandex_polygon_token = s['yandex_polygon_token'] #Yandex токен

class VK:
    API_BASE_URL = 'https://api.vk.com/method'
    YANDEX_DRIVE_URL = 'https://cloud-api.yandex.net/v1/disk'

    def __init__(self, access_token, user_id, version='5.236'):
        self.token = access_token
        self.id = user_id
        self.version = version

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.236'
        }

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = self.get_common_params()
        params.update({'user_ids': self.id})
        response = requests.get(url, params=params)
        print(response.url)
        return response.json()

    def get_wall_photos(self):
        params = self.get_common_params()
        params.update({'album_id': 'wall','extended': '1'})
        response_wall = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        result = response_wall.json()
        return result

    def get_photos(self):
        params = self.get_common_params()
        params.update({'album_id': 'profile','extended': '1'})
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        result = response.json()
        return result

    def processing_photos(self,result,folder):
        list_of_names = []
        json_result = []

        # разбор результата
        count_photos = result['response']['count']  # кол-во фото в профиле
        if count_photos > 15:
            count_photos = 15
        print(f'Количество фото: {count_photos}')
        for i in range(count_photos):
            print(f'Обрабатывается фото: {i + 1} из {count_photos}')
            photo_details = {}
            photo_list = result['response']['items'][i]['sizes']  # получаем общий список фото во всех разрешениях
            number_of_likes = result['response']['items'][i]['likes']['count']  # вытаскиваем кол-во лайков, не своих
            date_of_creation = result['response']['items'][i]['date']  # вытаскиваем дату создания
            link = photo_list[len(photo_list) - 1]['url']  # получаем только ссылку
            file_name = photo_list[len(photo_list) - 1]["url"].split("/")[-1].split("?")[
                0]  # добрался до оригинальнго имени файла
            file_size = photo_list[len(photo_list) - 1]["url"].split("/")[-1].split("?")[1].split("&")[0].split("=")[
                1]  # добрался до оригинальнго имени файла
            file_name_to_save = str(number_of_likes) + file_name[-4:]
            if file_name_to_save in list_of_names:
                file_name_to_save = f'{str(number_of_likes)}_{str(date_of_creation)}{file_name[-4:]}'
            list_of_names.append(file_name_to_save)
            photo_details.setdefault("file_name", file_name_to_save)
            photo_details.setdefault("size", file_size)
            json_result.append(photo_details)
            response_1 = requests.get(link)

            # сохранения фото в макс разрешении с именем кол-во лайков на локальный диск
            #if response_1.status_code == 200:
            #    with open(file_name_to_save, 'wb') as f:
            #        f.write(response_1.content)

            # сохранения фото в макс разрешении с именем кол-во лайков на диск яндекс
            if response_1.status_code == 200:
                vk.file_saving(link, file_name_to_save,folder)

        return json_result

    #метод создания папки на Яндекс диск
    def yandex_folder_creation(self,folder):
        yandex_params = {'path': folder}
        headers = {'Authorization': yandex_polygon_token}
        yandex_response = requests.put(f'{self.YANDEX_DRIVE_URL}/resources',
                                       params=yandex_params,
                                       headers=headers)
        return yandex_response.status_code

    def yandex_wall_folder_creation(self,folder):
        yandex_params = {'path': folder}
        headers = {'Authorization': yandex_polygon_token}
        yandex_wall_response = requests.put(f'{self.YANDEX_DRIVE_URL}/resources',
                                       params=yandex_params,
                                       headers=headers)
        return yandex_wall_response.status_code

    def file_saving(self, link, file_name,folder):
        #yandex_params = {'path': f'VKProfilePhotos/{file_name}'}
        yandex_params = {'path': f'{folder}/{file_name}'}
        yandex_params.update({'url': link})
        headers = {'Authorization': yandex_polygon_token}
        response_to_save = requests.post(f'{self.YANDEX_DRIVE_URL}/resources/upload',
                                         params=yandex_params,
                                         headers=headers)


if __name__ == '__main__':
    vk = VK(access_token, user_id)
    place_selection = int(input('Укажите откуда взять фото для копирования: 0 - Profile, 1 - Wall\n'))

    #сначала создадим папку на яндекс диске вызвав метод создания
    if place_selection == 0:
        if vk.yandex_folder_creation('VKProfilePhotos') == 201:
            result = vk.get_photos()
            with open('vk_to_yandex_profile.json', 'w+') as f:
                f.write(json.dumps(vk.processing_photos(result,'VKProfilePhotos'), indent=2))
#                processing_photos
#                f.write(json.dumps(vk.get_photos(), indent=2))
            print("Обработка завершена")
        elif vk.yandex_folder_creation('VKProfilePhotos') == 409:
            print(f'Ошибка {vk.yandex_folder_creation("VKProfilePhotos")}: Папка с таким именем уже существует')
        else:
            print('Неизвестная ошибка')
    else:
        if vk.yandex_wall_folder_creation('VKWallPhotos') == 201:
            result = vk.get_wall_photos()
            with open('vk_to_yandex_wall.json', 'w+') as f:
                f.write(json.dumps(vk.processing_photos(result,'VKWallPhotos'), indent=2))
            print("Обработка завершена")
        elif vk.yandex_wall_folder_creation('VKWallPhotos') == 409:
            print(f'Ошибка {vk.yandex_wall_folder_creation("VKWallPhotos")}: Папка с таким именем уже существует')
        else:
            print('Неизвестная ошибка')