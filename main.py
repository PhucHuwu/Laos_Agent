from rag import get_answer, build_index

# build_index()

query = "Hãy hướng dẫn tôi cách upload giấy tờ để KYC"
result = get_answer(query)

print("\n" + "=" * 50)
print("Query:", result["query"])

print("\n" + "=" * 50)
print("Contexts:")
for context in result["contexts"]:
    print("-", context["text"])
    

print("\n" + "=" * 50)
print("Answer:", result["answer"])

