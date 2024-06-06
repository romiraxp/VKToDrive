import requests
class VK:

    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, access_token,user_id):
        self.params = {
            'access_token': access_token,
            'owner_id' : user_id,
            'v': '5.236',
            'extended': '1'
        }

    # метод, который будет возвращать результат обращения к фото профиля
    def get_photos(self,album_id):
        params = self.params
        params.update({'album_id': album_id})
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        result = response.json()
        return result