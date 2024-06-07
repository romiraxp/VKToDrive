import requests
class YNDX:

    YANDEX_DRIVE_URL = 'https://cloud-api.yandex.net/v1/disk'

    def __init__(self, ya_access_token):
        self.ya_token = ya_access_token
        self.ya_headers = {'Authorization': self.ya_token}

    # метод создания папки на Яндекс диск для хранения фото
    def create_yandex_folder(self,folder):
        yandex_params = {'path': folder}
        #headers = {'Authorization': self.ya_token}
        yandex_response = requests.put(f'{self.YANDEX_DRIVE_URL}/resources',
                                       params=yandex_params,
                                       headers=self.ya_headers)
        return yandex_response.status_code

    #метод сохранения фото на Яндекс диске
    def save_files(self, link, file_name,folder):
        #yandex_params = {'path': f'VKProfilePhotos/{file_name}'}
        yandex_params = {'path': f'{folder}/{file_name}'}
        yandex_params.update({'url': link})
        #headers = {'Authorization': self.ya_token}
        response_to_save = requests.post(f'{self.YANDEX_DRIVE_URL}/resources/upload',
                                         params=yandex_params,
                                         headers=self.ya_headers)