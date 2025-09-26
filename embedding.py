from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


def embedding(texts):
    return normalize(model.encode(texts, show_progress_bar=True))
