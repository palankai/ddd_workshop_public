from json import loads as json_decode
from json import dumps as json_encode


class Order:

    def __init__(self, document=None):
        self.document = document or '{}'

    def add_line(self, line):
        object = json_decode(self.document)
        if 'lines' not in object:
            object['lines'] = []

        line['id'] = len(object['lines']) + 1
        object['lines'].append(line)
        self.document = json_encode(object)

    def add_price(self, id, price):
        object = json_decode(self.document)
        for line in object['lines']:
            if line['id'] == id:
                line['price'] = price
        self.document = json_encode(object)

    def pay_all(self):
        object = json_decode(self.document)
        object['payed'] = True
        self.document = json_encode(object)
