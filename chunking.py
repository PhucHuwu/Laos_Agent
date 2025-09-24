from typing import Iterable, Mapping, Any, List

def chunk_data(data_list: Iterable[Mapping[str, Any]]) -> List[str]:
    if data_list is None:
        raise TypeError("data_list cannot be None")

    result: List[str] = []
    for index, item in enumerate(data_list):
        if not isinstance(item, Mapping):
            raise TypeError(f"Each item must be a mapping/dict, got {type(item)!r} at index {index}")
        category = item.get("category", "")
        title = item.get("title", "")
        content = item.get("content", "")
        result.append(f"Mục: {category}\nTiêu đề: {title}\nNội dung: {content}")

    return result
