import re

with open('knowledge/faceless_conveyor_playbook.md', 'r') as f:
    text = f.read()

# Remove standard markdown characters
text = re.sub(r'[*_#`~-]', '', text)

print(text)
