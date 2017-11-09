import json
import copy


class OrderDocument:

    def __init__(self, src=None):
        self._src = src or {}

    def __hasattr__(self, name):
        return name in self._src

    def __getattr__(self, name):
        try:
            return self._src[name]
        except KeyError:
            raise AttributeError(f'Attribute not found {name}')

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._src[name] = value

    def serialize(self):
        return json.dumps(self._src)

    def copy(self):
        new_src = copy.deepcopy(self._src)
        return OrderDocument(new_src)

    def add_line(self, **data):
        if 'lines' not in self._src:
            self._src['lines'] = []
        self._src['lines'].append(data)

    @property
    def lines(self):
        return [OrderLineDocument(kw) for kw in self._src.get('lines', [])]

    def __str__(self):
        return json.dumps(self._src)

    def __repr__(self):
        return 'OrderDocument({!r})'.format(self._src)


class OrderLineDocument:

    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        return self._data[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value
