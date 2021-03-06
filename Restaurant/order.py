from json import dumps as json_encode
from json import loads as json_decode
import uuid


class Order:

    def __init__(self, document=None):
        self.document = document or '{}'
        self.add_id()

    def add_id(self):
        obj = json_decode(self.document)
        obj['id'] = str(uuid.uuid4())[:8]
        self.document = json_encode(obj)

    def add_line(self, line):
        obj = json_decode(self.document)
        if 'lines' not in obj:
            obj['lines'] = []

        line['id'] = len(obj['lines']) + 1
        obj['lines'].append(line)
        self.document = json_encode(obj)

    def add_price(self, _id, price):
        obj = json_decode(self.document)
        for line in obj['lines']:
            if line['id'] == _id:
                line['price'] = price
        self.document = json_encode(obj)

    def pay_all(self):
        obj = json_decode(self.document)
        obj['paid'] = True
        self.document = json_encode(obj)
