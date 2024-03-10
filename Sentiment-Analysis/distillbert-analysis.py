import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load pre-trained DistilBERT model and tokenizer
model_name = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForSequenceClassification.from_pretrained(model_name)

# Sample dataset (replace with your dataset)
texts = ["I love this product!", "The service was terrible.", "The weather is nice today."]
labels = [1, 2, 3]  # 1 for positive, 2 for negative, 3 for neutral

# Tokenize and split the dataset
inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
X_train, X_val, y_train, y_val = train_test_split(inputs["input_ids"], labels, test_size=0.2, random_state=42)

# Define training arguments
training_args = TrainingArguments(
    output_dir="sentiment_distilbert_model",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="../logs",
)

# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=(X_train, y_train),
    eval_dataset=(X_val, y_val),
)

# Fine-tune the model
trainer.train()

# Save the fine-tuned model
model.save_pretrained("./sentiment_distilbert_model")
tokenizer.save_pretrained("./sentiment_distilbert_model")

# Evaluate the fine-tuned model
predictions = trainer.predict(X_val)
accuracy = accuracy_score(y_val, predictions.predictions.argmax(axis=1))
print(f"Validation Accuracy: {accuracy}")
