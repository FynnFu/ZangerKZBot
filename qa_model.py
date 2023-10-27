from transformers import pipeline

# Импортируйте модель и токенизатор
qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

# Тестовые данные
context = "The quick brown fox jumps over the lazy dog."
question = "What does the fox jump over?"

# Задайте вопрос модели
result = qa_pipeline(question=question, context=context)

# Выведите результат
print("Answer:", result["answer"])
