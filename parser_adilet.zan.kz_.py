import json

data = []

# Попробуем сначала загрузить существующий JSON-файл
try:
    with open('context_0000001.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
except FileNotFoundError:
    pass

while True:
    text = input()

    if text == "stop":
        break

    data.append(text)

with open('context_0000001.json', 'w', encoding='utf-8') as file:
    json.dump(data, file)

print("Данные сохранены в context_0000001.json")
