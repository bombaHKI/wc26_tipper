import json
import os

config_path = os.path.join(os.path.dirname(__file__), 'data/config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    configJson = json.load(f)
    appConfigJson = configJson["app"]
    emailJson = configJson["email"]
    apiJson = configJson["API"]
    adminUser = configJson["admin-user"]