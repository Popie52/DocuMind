import re
from typing import List


def is_page_query(question: str) -> bool:
    text = question.lower()

    keywords = [
        "page",
        "pages",
        "pg",
        "compare",
        "vs",
        "versus",
        "difference",
        "summarize page",
        "what is on page",
        "explain page",
    ]

    return any(k in text for k in keywords)


def extract_page_numbers(question: str) -> List[int]:
    text = question.lower()
    pages = set()

    range_patterns = [
        r"page\s+(\d+)\s*-\s*(\d+)",
        r"pages\s+(\d+)\s*-\s*(\d+)",
        r"page\s+(\d+)\s+to\s+(\d+)",
        r"pages\s+(\d+)\s+to\s+(\d+)",
        r"(\d+)\s*-\s*(\d+)",
    ]

    for pattern in range_patterns:
        match = re.search(pattern, text)
        if match:
            start, end = map(int, match.groups())
            if start <= end:
                pages.update(range(start, end + 1))

    explicit_patterns = [
        r"\bpage\s+(\d+)\b",
        r"\bon\s+page\s+(\d+)\b",
        r"\bpg\s+(\d+)\b",
        r"\bpage\s*#\s*(\d+)\b",
    ]

    for pattern in explicit_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            pages.add(int(m))

    if any(word in text for word in ["compare", "vs", "versus", "difference"]):
        nums = re.findall(r"\b\d+\b", text)
        for n in nums:
            pages.add(int(n))

    if is_page_query(text) and not pages:
        nums = re.findall(r"\b\d+\b", text)
        for n in nums:
            pages.add(int(n))

    return sorted(pages)
