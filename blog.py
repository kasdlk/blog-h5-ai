import json
import os
import random
from pathlib import Path
from openai import OpenAI
from datetime import datetime

# ✅ Load API Key from environment variable (do not hardcode keys)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY is missing. Set it in the environment variables.")

# ✅ Initialize OpenAI Client
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ✅ Define file paths
json_path = Path("filestructure.json")
blog_root = Path("blog")

# ✅ Available years and categories
available_years = [str(year) for year in range(2021, 2026)]
available_categories = ["AI", "Cryptocurrency", "Finance", "News_Analysis", "Programming", "Software", "Website_SEO", "Website_Recommendations"]

# ✅ Load existing file structure
if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
else:
    existing_data = {}

# ✅ Extract existing article titles to prevent duplication
existing_titles = set()
for year, categories in existing_data.items():
    for category, articles in categories.items():
        for article in articles:
            existing_titles.add(article)

# ✅ Randomly select year and category
selected_year = random.choice(available_years)
selected_category = random.choice(available_categories)

# ✅ Request AI to generate a unique article (English content, >1000 words)
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": (
                "Generate a JSON article structure with content exceeding 1000 words. "
                "Ensure the title does not duplicate existing articles. "
                "Here are the existing titles:\n"
                f"{json.dumps(list(existing_titles), ensure_ascii=False)}\n"
                "Use the following JSON format:"
                "{"
                f"  \"{selected_year}\": {{"
                f"    \"{selected_category}\": ["
                "      {"
                "        \"title\": \"Article_Title\","
                "        \"meta\": {\"published_on\": \"Date\", \"author\": \"Author_Name\"},"
                "        \"toc\": ["
                "          {\"id\": \"section1\", \"text\": \"Section 1 Title\"},"
                "          {\"id\": \"section2\", \"text\": \"Section 2 Title\"},"
                "          {\"id\": \"section3\", \"text\": \"Section 3 Title\"},"
                "          {\"id\": \"section4\", \"text\": \"Section 4 Title\"}"
                "        ],"
                "        \"content\": {"
                "          \"section1\": \"Detailed content for Section 1 (at least 250 words)\","
                "          \"section2\": \"Detailed content for Section 2 (at least 250 words)\","
                "          \"section3\": \"Detailed content for Section 3 (at least 250 words)\","
                "          \"section4\": \"Detailed content for Section 4 (at least 250 words)\""
                "        }"
                "      }"
                "    ]"
                "  }"
                "}"
                "Rules:"
                "1. `title` should use underscores (_) instead of spaces."
                "2. `content` should be broad, without specific years mentioned."
                "3. Logical, structured, and not mechanically generated."
                "4. Return **strict JSON format only**, no extra text."
                "5. **Language: English**."
            )
        }
    ],
    stream=False
)

# ✅ Validate AI response
if not response.choices or not response.choices[0].message.content.strip():
    raise ValueError("❌ AI returned empty content. Please check the API response.")

content = response.choices[0].message.content.strip()

# ✅ Remove potential JSON code block markers from AI output
if content.startswith("```json"):
    content = content.replace("```json", "").replace("```", "").strip()

# ✅ Parse JSON
try:
    new_article_data = json.loads(content)
except json.JSONDecodeError as e:
    print(f"❌ JSON Parsing Error: {e}")
    print("⚠️ AI Response:", content)
    exit(1)

# ✅ Update `filestructure.json` and generate HTML
for year, categories in new_article_data.items():
    if year not in existing_data:
        existing_data[year] = {}

    for category, articles in categories.items():
        if category not in existing_data[year]:
            existing_data[year][category] = []

        for article_data in articles:
            article_title = article_data["title"]
            if article_title not in existing_data[year][category]:  # Prevent duplicates
                existing_data[year][category].append(article_title)

                # ✅ Generate HTML content
                html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{article_title.replace("_", " ")}</title>
                    <link rel="stylesheet" href="../../../styles.css">
                </head>
                <body>
                    <div id="header"></div>
                    <div id="sidebar"></div>
                    <main>
                        <div class="container">
                            <div class="content">
                                <div class="article-header">
                                    <h1>{article_title.replace("_", " ")}</h1>
                                    <p class="article-meta" style="display: none">Published on <span>{article_data['meta']['published_on']}</span> by <span>{article_data['meta']['author']}</span></p>
                                </div>
                                <div class="article-toc">
                                    <h2>Table of Contents</h2>
                                    <ul>
                                        {''.join(f'<li><a href="#{section["id"]}">{section["text"]}</a></li>' for section in article_data['toc'])}
                                    </ul>
                                </div>
                                <div class="article-body">
                                    {''.join(f'<h2 id="{key}">{article_data["toc"][i]["text"]}</h2><p>{value}</p>' for i, (key, value) in enumerate(article_data['content'].items()))}
                                </div>
                            </div>
                        </div>
                    </main>
                    <script src="../../../common.js"></script>
                </body>
                </html>
                """

                # ✅ Save HTML file
                article_path = blog_root / year / category / f"{article_title}.html"
                article_path.parent.mkdir(parents=True, exist_ok=True)
                with open(article_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)

# ✅ Update `filestructure.json`
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(existing_data, f, indent=4, ensure_ascii=False)

print(f"✅ New article added: {new_article_data}")
print(f"✅ HTML file generated at: {article_path}")
