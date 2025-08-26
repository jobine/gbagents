import re

def clean_thinking(text):
    patterns = [
        r'<think>.*?</think>', # 移除<think>标签内容
    ]

    cleaned_text = text

    for pattern in patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL | re.MULTILINE)

    # cleaned_text = re.sub(r'\n{3, }', '\n\n', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text