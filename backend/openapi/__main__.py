import json

from . import get_openapi

if __name__ == "__main__":
    with open("openapi.json", "w") as f:
        # print(get_openapi())
        json.dump(get_openapi(), f, indent=2)
