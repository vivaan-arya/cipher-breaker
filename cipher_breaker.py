import numpy as np
import string
import re
import pickle

# ------------------------
# Load trigram model ONCE
# ------------------------
with open("trigram_probs.pkl", "rb") as f:
    data = pickle.load(f)
    LOG_PROBS = data["log_probs"]
    DEFAULT_PROB = data["default_prob"]

ALPH = string.ascii_uppercase

# ------------------------
# Scoring
# ------------------------
def score_text(txt: str) -> float:
    txt = re.sub(r"[^A-Z]", "", txt.upper())
    if len(txt) < 3:
        return float("-inf")
    return sum(
        LOG_PROBS.get(txt[i:i+3], DEFAULT_PROB)
        for i in range(len(txt)-2)
    )

# ------------------------
# Caesar
# ------------------------
def caesar_decrypt(ct: str, shift: int) -> str:
    out = []
    for ch in ct:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            out.append(chr((ord(ch) - base - shift) % 26 + base))
        else:
            out.append(ch)
    return "".join(out)


def break_caesar(ciphertext):
    best = (-1e300, None, None)

    for shift in range(26):
        pt = caesar_decrypt(ciphertext, shift)
        score = score_text(pt)
        if score > best[0]:
            best = (score, shift, pt)

    score, shift, text = best
    return {
        "cipher": "caesar",
        "key": chr(shift + ord("a")),
        "plaintext": text,
        "score": score
    }


# ------------------------
# Vigenère
# ------------------------
def vigenere_decrypt(ciphertext, key):
    res, idx = [], 0
    for ch in ciphertext:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            res.append(chr((ord(ch) - base - key[idx % len(key)]) % 26 + base))
            idx += 1
        else:
            res.append(ch)
    return "".join(res)


def cem_vigenere(ciphertext, L, iters=300, samples=600, elite_frac=0.2, alpha=0.9):
    probs = np.ones((L, 26)) / 26
    best = (-1e300, None, None)
    Ne = max(1, int(samples * elite_frac))

    for _ in range(iters):
        keys = [
            [np.random.choice(26, p=probs[i]) for i in range(L)]
            for _ in range(samples)
        ]
        scored = [
            (score_text(pt := vigenere_decrypt(ciphertext, k)), k, pt)
            for k in keys
        ]
        scored.sort(reverse=True)
        elites = scored[:Ne]

        if elites[0][0] > best[0]:
            best = elites[0]

        new_probs = np.zeros_like(probs)
        for _, k, _ in elites:
            for i, s in enumerate(k):
                new_probs[i, s] += 1

        new_probs /= new_probs.sum(axis=1, keepdims=True)
        probs = alpha * new_probs + (1 - alpha) * probs

        if probs.max() > 0.995:
            break

    return best


def break_vigenere(ciphertext, min_L=2, max_L=10):
    best = (-1e300, None, None, None)

    for L in range(min_L, max_L + 1):
        score, key, text = cem_vigenere(ciphertext, L)
        if score > best[0]:
            best = (score, L, key, text)

    score, L, key, text = best

    key_letters = "".join(chr(k + ord("a")) for k in key)

    return {
        "cipher": "vigenere",
        "key": key_letters,      
        "plaintext": text,
        "score": score
    }
