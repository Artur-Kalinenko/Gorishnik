import base64
import hashlib
import json


# Клиент для работы с LiqPay API (генерация подписи и данных для формы)
class LiqPay:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

    # Генерирует base64-кодированные данные для отправки в форму оплаты
    def cnb_data(self, params):
        params.update({'public_key': self.public_key})
        json_str = json.dumps(params, separators=(',', ':'), ensure_ascii=False)
        return base64.b64encode(json_str.encode('utf-8')).decode('ascii')

    # Генерирует подпись по схеме: private_key + base64(data) + private_key
    def cnb_signature(self, params):
        data = self.cnb_data(params)
        str_to_sign = self.private_key + data + self.private_key
        sha1 = hashlib.sha1()
        sha1.update(str_to_sign.encode('utf-8'))
        return base64.b64encode(sha1.digest()).decode('ascii')

    # Генерация SHA1-подписи строки (может использоваться для верификации)
    def str_to_sign(self, s):
        sha1 = hashlib.sha1()
        sha1.update(s.encode('utf-8'))
        return base64.b64encode(sha1.digest()).decode('ascii')
