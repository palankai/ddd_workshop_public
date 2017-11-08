from json import dumps as json_encode
from json import loads as json_decode
from order import Order


class TestOrder:

    def test_add_lines_to_empty_document(self):
        # given document
        document = '{}'
        order = Order(document)

        # because we add line
        order.add_line({'item': 'Burguer', 'qty': 1, 'price': 1})

        # We should have one line
        assert json_decode(order.document) == \
            json_decode('''
                {
                    "lines": [
                        {"id": 1, "item": "Burguer", "qty": 1, "price": 1}
                    ]
                }
            ''')

    def test_add_lines_to_document_with_line(self):
        # given document
        document = '''
{"lines": [{"id": 1, "item": "Burguer", "qty": 1, "price": 1}]}
'''
        order = Order(document)

        # because we add line
        order.add_line({'item': 'Salad', 'qty': 1, 'price': 1})

        # We should have one line
        assert json_decode(order.document) == \
                json_decode('''
                    {
                        "lines": [
                            {"id": 1, "item": "Burguer", "qty": 1, "price": 1},
                            {"id": 2, "item": "Salad", "qty": 1, "price": 1}
                        ]
                    }
                ''')

    def test_add_unknown_thing_to_document(self):
        # given document
        document = '{}'
        order = Order(document)

        # because we modify it
        the_document = json_decode(order.document)
        the_document['foo'] = True
        order.document = json_encode(the_document)

        # We should have one line
        assert json_decode(order.document) == json_decode('{"foo": true}')
