import json
from transformers import pipeline

# Импортируйте модель и токенизатор
qa_pipeline = pipeline("question-answering", model="timpal0l/mdeberta-v3-base-squad2")

# Тестовые данные
try:
    with open('context_0000001.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
except FileNotFoundError:
    pass

context = "\n".join(data)

print(context)
question = "Қазақстан Республикасының ең қымбат қазынасына не жатады?"

# Задайте вопрос модели
result = qa_pipeline(question=question, context=context)

# Выведите результат
print("Answer:", result["answer"])
