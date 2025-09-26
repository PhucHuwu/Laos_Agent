import os
from dotenv import load_dotenv
from groq import Groq
import faiss
import pickle
from chunking import chunking
from embedding import embedding

load_dotenv()
api = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api)

LLAMA3_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"


def build_index():
    import json

    data = json.load(open("data/data.json", encoding='utf-8'))

    docs = chunking(data)
    texts = [doc['text'] for doc in docs]
    metadatas = [{"text": doc["text"], **doc["metadata"]} for doc in docs]

    embeddings = embedding(docs)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    os.makedirs("embeddings", exist_ok=True)

    faiss.write_index(index, "embeddings/faiss_index.bin")
    with open("embeddings/metadata.pkl", "wb") as f:
        pickle.dump(metadatas, f)


def search_rag(query, k=5):
    import pickle
    import faiss
    from embedding import embedding

    query = query.strip().lower()

    index = faiss.read_index("embeddings/faiss_index.bin")
    metadata = pickle.load(open("embeddings/metadata.pkl", "rb"))

    q_emb = embedding([query])
    D, I = index.search(q_emb, k)

    threshold = 1.2
    contexts = []

    for dist, idx in zip(D[0], I[0]):
        if dist < threshold:
            contexts.append(metadata[idx])
    if not contexts:
        contexts = [metadata[i] for i in I[0]]

    return contexts


def generate_answer(query, contexts, temperature=1.2, max_tokens=2048):
    prompt = f"""Bạn là một trợ lý AI chuyên hỗ trợ người dân về việc KYC căn cước công dân
                 Dưới đây là thông tin từ các tài liệu liên quan\n:
              """
    for context in contexts:
        prompt += f"- {context['text']}\n"

    prompt += f"Người dân hỏi: {query}\n"
    prompt += "Vui lòng trả lời dựa trên các thông tin đã cung cấp"
    prompt += "Nếu không đủ thông tin, hãy nói rõ bạn không thể trả lời chính xác."
    prompt += "Trả lời đầy đủ, rõ ý, dễ hiểu bằng tiếng Việt."

    try:
        response = client.chat.completions.create(
            model=LLAMA3_MODEL_ID,
            messages=[
                {"role": "system",
                 "content": """Bạn là một trợ lý AI chuyên hỗ trợ người dân về việc KYC căn cước công dân.
                               Hãy trả lời một cách ngắn gọn, súc tích, dễ hiểu, và bằng tiếng Việt."""},
                {"role": "user",
                 "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Đã xảy ra lỗi khi tạo câu trả lời: {str(e)}"


def get_answer(query, k=10, temperature=1.2, max_tokens=2048):
    contexts = search_rag(query, k)
    answer = generate_answer(query, contexts, temperature, max_tokens)
    return {
        "query": query,
        "contexts": contexts,
        "answer": answer
    }
