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
