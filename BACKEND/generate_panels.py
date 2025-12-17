import os
import re
from dotenv import load_dotenv
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"
if not OPENROUTER_API_KEY:
    raise ValueError("Please set the OPENROUTER_API_KEY environment variable.")

OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"  # Public/free model on OpenRouter
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


TEMPLATE = """
You are a professional comic book creator.

You will be given a short scenario, and you must split it into exactly 6 comic panels.

**Art Style:** {art_style}

For each comic panel, provide:
1. **Description**: A detailed background and character description (comma-separated, not full sentences).
2. **Text**: Exact dialogue in quotation marks, or if no dialogue, leave it empty or use `...`.

Ensure all text is clear, meaningful, and in proper English.

Format:
# Panel 1
Description: [Background and character details]
Text: "[Character]: [Dialogue]" OR "..." if no dialogue.

# Panel 2
Description: [Background and character details]
Text: "[Character]: [Dialogue]" OR "..." if no dialogue.

# end

Short Scenario:
{scenario}
"""

def generate_panels(scenario, art_style):
    """
    Generates six structured comic panels based on the given scenario and art style.
    Returns a list of dictionaries containing descriptions and dialogues.
    """
    formatted_prompt = TEMPLATE.format(scenario=scenario, art_style=art_style)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": formatted_prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.7
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.status_code} {response.text}")
    result = response.json()
    result_content = result["choices"][0]["message"]["content"].strip()
    return extract_panel_info(result_content)

def extract_panel_info(text):
    """
    Extracts structured panel descriptions and dialogues from the generated text.
    """
    panel_info_list = []
    panel_blocks = re.split(r"# Panel \d+", text)

    for block in panel_blocks:
        if block.strip():
            panel_info = {}
            desc_match = re.search(r"Description:\s*(.+)", block, re.IGNORECASE)
            if desc_match:
                panel_info['Description'] = desc_match.group(1).strip()
            else:
                panel_info['Description'] = "Unknown scene, ensure proper generation."

            text_match = re.findall(r'Text:\s*"([^"]+)"', block, re.IGNORECASE | re.DOTALL)
            
            if text_match:
                panel_info['Text'] = " ".join(text_match)  
            else:
                panel_info['Text'] = "..."  

            panel_info_list.append(panel_info)

    if len(panel_info_list) != 6:
        # Log a warning but do not raise
        print(f"Warning: Expected 6 panels, but got {len(panel_info_list)}. Using first 6.")
    return panel_info_list[:6]

if __name__ == '__main__':
    scenario = input("Enter your short comic scenario: ")
    print("\nChoose an art style: Manga, Anime, American, Belgian")
    art_style = input("Enter art style: ").strip().capitalize()

    valid_styles = ["Manga", "Anime", "American", "Belgian"]
    if art_style not in valid_styles:
        print("Invalid art style! Defaulting to 'Anime'.")
        art_style = "Anime"

    panels = generate_panels(scenario, art_style)

    for i, panel in enumerate(panels, 1):
        print(f"\nPanel {i}:")
        print(f"Description: {panel['Description']}")
        print(f"Text: {panel['Text']}")
















