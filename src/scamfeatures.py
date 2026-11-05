# Shared text-signal features used by the classifier and the scam checker
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

def signal_features(texts):
    t = pd.Series(texts).reset_index(drop=True)
    return pd.DataFrame({
        "word_count":     t.str.split().str.len(),
        "digits":         t.str.count(r"\d"),
        "has_phone":      t.str.contains(r"\d{10,}").astype(int),
        "has_shortcode":  t.str.contains(r"\b\d{4,6}\b").astype(int),
        "has_url":        t.str.contains(r"http|www\.|\.com|\.co\.uk|\.ly|\.io", case=False).astype(int),
        "has_currency":   t.str.contains(r"[£$€]").astype(int),
        "caps_pct":       t.str.count(r"[A-Z]") / t.str.len().clip(lower=1) * 100,
        "exclaim":        t.str.count("!"),
        "call_to_action": t.str.contains(r"\b(?:call|txt|text|reply|click|send|visit)\b", case=False).astype(int),
        "sentiment":      t.apply(lambda x: sia.polarity_scores(x)["compound"]),
    })