import json
import time

def load_json():
    with open('unfinished.json', 'r') as f:
        loaded_refs = json.load(f)
        return loaded_refs

def add_json(element):
    orders = load_json()
    with open('unfinished.json', 'w') as f:
        orders[str(int(time.time()))] = element
        json.dump(orders, f)

def remove_json(element):
    orders = load_json()
    orders.pop(element)
    with open('unfinished.json', 'w') as f:
        json.dump(orders, f)