# train_model.py
import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Load dataset
with open("backend/model_training/final_combined_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract questions
texts = [item["question"].strip() for item in data]

# Train vectorizer and model
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(texts)

model = KMeans(n_clusters=5, random_state=42)
model.fit(X)

# Save both
joblib.dump(vectorizer, "backend/model_training/vectorizer.pkl")
joblib.dump(model, "backend/model_training/model.pkl")

print("✅ Model training completed.")
