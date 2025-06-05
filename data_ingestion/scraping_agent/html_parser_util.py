from bs4 import BeautifulSoup

def parse_static_html(html_content: str) -> dict:
    """
    Parses static HTML content to extract a title and all paragraph texts.
    Demonstrates basic BeautifulSoup usage for parsing static content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find('title').text if soup.find('title') else 'No Title'
    paragraphs = [p.text for p in soup.find_all('p')]
    return {"title": title, "paragraphs": paragraphs}

if __name__ == "__main__":
    # Example usage
    sample_html = """
    <html>
    <head><title>Sample Document</title></head>
    <body>
        <h1>Welcome</h1>
        <p>This is the first paragraph.</p>
        <p>This is the second paragraph with more information.</p>
    </body>
    </html>
    """
    parsed_data = parse_static_html(sample_html)
    print(f"Parsed Title: {parsed_data['title']}")
    print("Parsed Paragraphs:")
    for p in parsed_data['paragraphs']:
        print(f"- {p}") 