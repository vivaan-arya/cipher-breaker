import re, math, pickle, os
from collections import Counter
import nltk
from nltk.corpus import brown

TRIGRAM_PKL = "trigram_probs.pkl"

if os.path.exists(TRIGRAM_PKL):
    print("Trigram model already exists.")
    exit()

nltk.download("brown")

text = " ".join(brown.words()).upper()
text = re.sub(r"[^A-Z]", "", text)

trigrams = [text[i:i+3] for i in range(len(text)-2)]
counts = Counter(trigrams)
total = sum(counts.values())

V = 26**3
smoothing = 1.0

log_probs = {
    tri: math.log((c + smoothing) / (total + smoothing * V))
    for tri, c in counts.items()
}
default_prob = math.log(smoothing / (total + smoothing * V))

with open(TRIGRAM_PKL, "wb") as f:
    pickle.dump(
        {"log_probs": log_probs, "default_prob": default_prob},
        f
    )

print("Saved trigram model to trigram_probs.pkl")
