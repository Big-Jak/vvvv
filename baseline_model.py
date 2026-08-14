import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge


def load_split(path):
    path = Path(path)
    df = pd.read_csv(path)
    return df.dropna(subset=["full_text", "score"])


def train_baseline(train_df):
    vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        stop_words="english",
    )
    X = vectorizer.fit_transform(train_df["full_text"].astype(str))
    y = train_df["score"].astype(float)
    model = Ridge(alpha=1.0)
    model.fit(X, y)
    return vectorizer, model


def predict(vectorizer, model, df):
    X = vectorizer.transform(df["full_text"].astype(str))
    return model.predict(X)
