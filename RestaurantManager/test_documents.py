from documents import OrderDocument, OrderLineDocument


class TestDocument:

    def test_reader(self):
        src = '{"order_reference": "ABC-123"}'

        doc = OrderDocument(src)

        assert doc.order_reference == 'ABC-123'

    def test_writer(self):
        src = '{"order_reference": "ABC-123"}'
        expected = '{"order_reference": "321-CBA"}'

        doc = OrderDocument(src)
        doc.order_reference = '321-CBA'

        assert doc.order_reference == '321-CBA'

        dest = doc.serialize()

        assert dest == expected

    def test_add_line_to_and_empty_document(self):

        src = '{}'

        doc = OrderDocument(src)
        doc.add_line(OrderLineDocument('name', qty=1, price=100))

        [l] = doc.lines

        assert l.name == 'name'

        assert doc.serialize() == '{"lines": [{"name": "name", "qty": 1, "price": 100}]}'


    def test_add_unknown(self):
        src = '{"unknown": 1}'
        doc = OrderDocument(src)

        assert doc.serialize() == src
