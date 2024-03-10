from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline

# Load pre-trained BERT model and tokenizer
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)


# Define a function for sentiment analysis using BERT
def analyze_sentiment(sentence):
    # Tokenize input sentence
    tokens = tokenizer(sentence, return_tensors="pt")

    # Make prediction
    output = model(**tokens)
    logits = output.logits

    # Predicted class (1 for positive, 2 for negative, 3 for neutral)
    predicted_class = logits.argmax().item()

    return predicted_class

# Example sentences
positive_sentence = "I love this product! It's amazing."
negative_sentence = "The service was terrible. I wouldn't recommend it."
neutral_sentence = "The weather is nice today."

# Analyze sentiment for each sentence
positive_result = analyze_sentiment(positive_sentence)
negative_result = analyze_sentiment(negative_sentence)
neutral_result = analyze_sentiment(neutral_sentence)

# Print results
print(f"Positive Sentence: {positive_sentence}")
print(f"Predicted Sentiment: {'Positive' if positive_result == 1 else 'Negative' if positive_result == 2 else 'Neutral'}")
print("="*50)

print(f"Negative Sentence: {negative_sentence}")
print(f"Predicted Sentiment: {'Positive' if negative_result == 1 else 'Negative' if negative_result == 2 else 'Neutral'}")
print("="*50)

print(f"Neutral Sentence: {neutral_sentence}")
print(f"Predicted Sentiment: {'Positive' if neutral_result == 1 else 'Negative' if neutral_result == 2 else 'Neutral'}")
