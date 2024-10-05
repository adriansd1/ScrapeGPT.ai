import openai
import requests
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import bleach

# Initialize OpenAI API
openai.api_key = ''

app = Flask(__name__)

def scrape_website(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        return None

def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove unwanted tags (like script, style, etc.)
    for script in soup(["script", "style", "noscript"]):
        script.decompose()

    # Convert frozenset to a list before concatenation
    allowed_tags = list(bleach.ALLOWED_TAGS) + ['p', 'div', 'span', 'h1', 'h2', 'h3', 'ul', 'li', 'table']

    # Optionally strip out attributes or tags you don't want (e.g., class, id)
    clean_html = bleach.clean(str(soup), tags=allowed_tags, attributes={}, strip=True)

    return clean_html


def send_to_openai(dom_content, instructions):
    try:
        messages = [
            {"role": "system", "content": "You are an assistant that helps with data processing. Please respond with your answer in HTML that can be embedded to be rendered in a web page."},
            {"role": "user", "content": f"DOM content: {dom_content}\nInstructions: {instructions}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # You can also use "gpt-3.5-turbo"
            messages=messages,
            max_tokens=1500
        )

        return response.choices[0].message['content'].strip()
    except Exception as e:
        return None

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        url = request.form["url"]
        instructions = request.form["instructions"]

        # Scrape the website
        dom_content = scrape_website(url)

        if dom_content:
            # Clean the HTML content
            cleaned_content = clean_html_content(dom_content)

            # Send cleaned DOM and instructions to OpenAI API
            result = send_to_openai(cleaned_content, instructions)

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
