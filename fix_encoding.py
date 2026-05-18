import os

replacements = {
    "â€”": "—",
    "â€“": "–",
    "âœ“": "✓",
    "â€¢": "•",
    "â†‘": "↑",
    "â†“": "↓",
    "â†’": "→",
    "â† ": "←",
    "âš ï¸ ": "⚠️",
    "âœ¨": "✨",
    "â„¹": "ℹ",
    "â— ": "●",
    "Ã©": "é",
    "Ã§": "ç",
    "Ã ": "à",
    "Ã¨": "è",
    "Ã´": "ô",
    "Ã¢": "â",
    "Ãª": "ê",
    "Ã®": "î",
    "Ã¯": "ï",
    "Ã»": "û",
    "Ã¹": "ù",
    "Ã¼": "ü",
    "âœ¦": "✦"
}

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for k, v in replacements.items():
            content = content.replace(k, v)
            
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed {filepath}")
    except Exception as e:
        pass

for root, _, files in os.walk(r"c:\Users\Yessine-PC\Desktop\pfev0\analytics-platform-front\src"):
    for file in files:
        if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.css', '.html')):
            fix_file(os.path.join(root, file))
