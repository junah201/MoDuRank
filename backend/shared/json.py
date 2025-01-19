import json
from decimal import Decimal


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        elif isinstance(o, type):
            return o.__name__
        return super().default(o)
