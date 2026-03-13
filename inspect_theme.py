from pathlib import Path
text=Path('templates/index.html').read_text(encoding='utf-8')
lines=text.splitlines()
for idx,line in enumerate(lines,1):
    if 'label for="theme"' in line:
        for offset in range(-2,4):
            print(f"{idx+offset}: {lines[idx+offset-1]}")
        break
