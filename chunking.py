def chunking(data_list):
    return [
        {"text": f"Danh mục: {item['category']}\nTiêu đề: {item['title']}\nNội dung: {item['content']}", "metadata": {"type": "data"}}
         for item in data_list
    ]
