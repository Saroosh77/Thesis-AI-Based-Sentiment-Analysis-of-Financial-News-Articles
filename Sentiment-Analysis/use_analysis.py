import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pandas as pd
from tqdm import tqdm

# Load the Universal Sentence Encoder
use_model_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
use_model = hub.load(use_model_url)


# Define a function for semantic analysis using USE
def analyze_semantics(sentences):
    embeddings = use_model(sentences)
    return embeddings.numpy()


# Example sentences
positive_sentence = "I love this product! It's amazing."
negative_sentence = "The service was terrible. I wouldn't recommend it."
neutral_sentence = "The weather is nice today."

# Analyze semantics for each sentence
sentences = [positive_sentence, negative_sentence, neutral_sentence]
embeddings = analyze_semantics(sentences)

# Print results
for i, sentence in enumerate(sentences):
    print(f"Sentence: {sentence}")
    print(f"Semantic Embedding: {embeddings[i]}")
    print("=" * 50)
