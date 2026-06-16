import anthropic
import os
import json
import re
from datetime import datetime
import random

# Onderwerpen gebaseerd op Vincent's expertise
TOPICS = [
    # Cybersecurity & Sales
    "Hoe cybersecurity-bedrijven hun salesproces kunnen verbeteren met betere storytelling",
    "De CISO als commerciële bondgenoot: hoe security beslissers te overtuigen",
    "Waarom MKB-bedrijven cybersecurity als groeistrategie moeten zien",
    "Van technische demo naar boardroom-gesprek: pitchen in de securitysector",
    "Hoe je een cybersecurity-propositie vertaalt naar business value",
    "Zero trust als verkoopargument: wat beslissers écht willen horen",
    "De rol van vertrouwen in het verkoopproces van cybersecurityoplossingen",

    # Marketing & IT
    "Contentmarketing voor IT-bedrijven: wat werkt en wat niet",
    "Hoe IT-bedrijven thought leadership opbouwen in een drukke markt",
    "De beste kanalen om IT-beslissers te bereiken in Nederland",
    "Account-based marketing in de IT-sector: praktische aanpak",
    "Hoe je als IT-bedrijf je merk bouwt zonder groot marketingbudget",
    "PR in de IT-sector: hoe je in de vakbladen komt",
    "Van vendor naar trusted advisor: de nieuwe positie van IT-leveranciers",

    # Sales Leadership & Strategie
    "Interim sales leadership: wanneer heb je het nodig en wat levert het op",
    "Hoe bouw je een succesvol salesteam in de IT-sector",
    "De drie grootste fouten in B2B-salesprocessen en hoe je ze vermijdt",
    "Pipeline management voor IT-bedrijven: van lead naar deal",
    "Hoe je als IT-bedrijf nieuwe markten betreedt zonder je te versnipperen",
    "Commerciële transformatie: wanneer je salesaanpak écht moet veranderen",
    "De kunst van het kwalificeren: waarom nee zeggen je salesresultaten verbetert",

    # Go-to-market & Groei
    "Schalen in de IT-sector: de vijf valkuilen die groei remmen",
    "Hoe positionering het verschil maakt tussen winnen en verliezen in IT",
    "Partnerstrategie in de IT-sector: hoe je het juiste ecosysteem bouwt",
    "Van productverkoop naar oplossingsverkoop in de IT-markt",
    "Hoe je als IT-scale-up enterprise-klanten wint",
]

TAGS = {
    "cybersecurity": "Cybersecurity & Sales",
    "marketing": "Marketing & IT",
    "sales": "Sales Leadership",
    "strategie": "Go-to-Market",
    "interim": "Sales Leadership",
    "content": "Marketing & IT",
    "partner": "Go-to-Market",
    "schalen": "Go-to-Market",
    "positionering": "Go-to-Market",
    "pipeline": "Sales Leadership",
    "pr": "Marketing & IT",
    "thought": "Marketing & IT",
    "boardroom": "Cybersecurity & Sales",
    "ciso": "Cybersecurity & Sales",
    "mkb": "Cybersecurity & Sales",
    "zero": "Cybersecurity & Sales",
}

def get_tag(topic):
    topic_lower = topic.lower()
    for keyword, tag in TAGS.items():
        if keyword in topic_lower:
            return tag
    return "Sales Leadership"

def slugify(text):
    text = text.lower()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text[:60]

def load_used_topics():
    if os.path.exists('used_topics.json'):
        with open('used_topics.json', 'r') as f:
            return json.load(f)
    return []

def save_used_topics(used):
    with open('used_topics.json', 'w') as f:
        json.dump(used, f)

def pick_topic():
    used = load_used_topics()
    available = [t for t in TOPICS if t not in used]
    if not available:
        # Reset als alle topics gebruikt zijn
        used = []
        available = TOPICS
    topic = random.choice(available)
    used.append(topic)
    save_used_topics(used)
    return topic

def generate_article(topic):
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

    prompt = f"""Schrijf een professioneel blogartikel voor de website van Vincent van Sas (vansassales.nl).

Vincent van Sas is een ervaren sales- en marketingconsultant met decennia ervaring in IT, media, sport en cybersecurity. Hij heeft als marketingdirecteur een IT-hardwarebedrijf zien groeien van 50 miljoen gulden naar 400 miljoen euro. Hij schrijft vanuit echte praktijkervaring, op directieniveau.

Onderwerp: {topic}

Schrijf het artikel in het Nederlands. Schrijf vanuit de eerste persoon (ik/mijn). Toon: professioneel, direct, praktisch — geen buzz words, wel concrete inzichten.

Geef je antwoord ALLEEN als JSON in dit exacte formaat, zonder markdown backticks:
{{
  "title": "De volledige titel van het artikel",
  "intro": "Een pakkende openingsparagraaf van 2-3 zinnen",
  "quote": "Een krachtige quote van maximaal 20 woorden die de kern van het artikel vat",
  "sections": [
    {{
      "heading": "Sectietitel",
      "content": "Twee alinea's van elk 3-4 zinnen. Praktisch en concreet."
    }},
    {{
      "heading": "Sectietitel",
      "content": "Twee alinea's van elk 3-4 zinnen."
    }},
    {{
      "heading": "Sectietitel", 
      "content": "Twee alinea's van elk 3-4 zinnen."
    }}
  ],
  "conclusion": "Een afsluitende alinea van 3-4 zinnen met een concrete oproep tot actie of reflectie.",
  "read_time": "6"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)

def build_article_html(data, slug, tag, date_str, date_display):
    sections_html = ""
    for section in data['sections']:
        paragraphs = section['content'].split('\n\n')
        paras_html = '\n'.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
        sections_html += f"""
            <h2>{section['heading']}</h2>
            {paras_html}"""

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} | Vincent van Sas</title>
    <meta name="description" content="{data['intro'][:155]}">
    <link rel="canonical" href="https://www.vansassales.nl/blog/{slug}.html">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": "{data['title']}",
      "author": {{"@type": "Person", "name": "Vincent van Sas"}},
      "datePublished": "{date_str}",
      "publisher": {{"@type": "Organization", "name": "Van Sas Sales & Marketing"}},
      "url": "https://www.vansassales.nl/blog/{slug}.html"
    }}
    </script>
    <link rel="stylesheet" href="../style.css">
    <style>
        .article-hero {{ background: linear-gradient(135deg, var(--primary-color) 0%, #1a3a5c 100%); color: var(--white); padding: 4rem 0; }}
        .article-tag {{ display: inline-block; background: var(--accent-color); color: var(--white); font-size: 0.75rem; font-weight: 700; padding: 0.3rem 0.8rem; border-radius: 20px; margin-bottom: 1.25rem; text-transform: uppercase; }}
        .article-hero h1 {{ font-size: 2.4rem; font-family: 'Montserrat', sans-serif; line-height: 1.3; margin-bottom: 1rem; max-width: 800px; }}
        .article-meta {{ opacity: 0.8; font-size: 0.95rem; }}
        .article-body {{ max-width: 780px; margin: 0 auto; padding: 4rem 0; }}
        .article-body h2 {{ font-size: 1.6rem; color: var(--primary-color); margin: 2.5rem 0 1rem; font-family: 'Montserrat', sans-serif; }}
        .article-body p {{ font-size: 1.05rem; line-height: 1.85; margin-bottom: 1.5rem; color: #444; }}
        .highlight-box {{ background: #f0f4f9; border-left: 4px solid var(--accent-color); padding: 1.5rem 2rem; margin: 2rem 0; border-radius: 0 8px 8px 0; }}
        .highlight-box p {{ margin: 0; font-style: italic; font-size: 1.1rem; color: var(--primary-color); }}
        .back-link {{ display: inline-block; margin-bottom: 2rem; color: var(--primary-color); font-weight: 600; text-decoration: none; }}
        .back-link:hover {{ color: var(--accent-color); }}
        .author-box {{ background: var(--white); border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); padding: 2rem; display: flex; gap: 1.5rem; align-items: center; margin-top: 3rem; }}
        .author-box img {{ width: 80px; height: 80px; border-radius: 50%; object-fit: cover; }}
        .author-box h3 {{ font-size: 1.1rem; color: var(--primary-color); margin-bottom: 0.25rem; }}
        .author-box p {{ font-size: 0.9rem; color: #666; margin: 0; line-height: 1.6; }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="logo"><a href="/"><img src="../logo.png" alt="van Sas Sales Consultancy" class="logo-img"></a></div>
            <nav>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/#over">Over</a></li>
                    <li><a href="/#diensten">Diensten</a></li>
                    <li><a href="/#aanpak">Mijn Aanpak</a></li>
                    <li><a href="/blog/" style="color: var(--accent-color);">Blog</a></li>
                    <li><a href="/#contact">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <div class="article-hero">
        <div class="container">
            <span class="article-tag">{tag}</span>
            <h1>{data['title']}</h1>
            <p class="article-meta">Vincent van Sas · {date_display} · {data['read_time']} min leestijd</p>
        </div>
    </div>

    <div class="container">
        <div class="article-body">
            <a href="/blog/" class="back-link">← Terug naar blog</a>
            <p>{data['intro']}</p>
            <div class="highlight-box"><p>"{data['quote']}"</p></div>
            {sections_html}
            <p>{data['conclusion']}</p>
            <div class="author-box">
                <img src="../vincent.png" alt="Vincent van Sas">
                <div>
                    <h3>Vincent van Sas</h3>
                    <p>Sales- en marketingconsultant met decennia ervaring in IT, media en cybersecurity. Helpt ambitieuze bedrijven groeien door commerciële strategie en technische expertise te combineren.</p>
                </div>
            </div>
        </div>
    </div>

    <footer id="contact">
        <div class="container">
            <h2>Sparren over uw strategie?</h2>
            <p>Neem contact op voor een vrijblijvend strategisch gesprek.</p>
            <p class="contact-info">Email: <a href="mailto:info@vansassales.nl" class="email-link">info@vansassales.nl</a></p>
            <p class="copyright">&copy; 2025 van Sas Sales & Marketing. Alle rechten voorbehouden.</p>
        </div>
    </footer>
</body>
</html>"""

def load_blog_index():
    index_path = 'blog/index.html'
    with open(index_path, 'r') as f:
        return f.read()

def add_card_to_index(html, title, intro, slug, tag, date_display):
    new_card = f"""
                <div class="blog-card">
                    <div class="blog-card-content">
                        <span class="blog-tag">{tag}</span>
                        <h2>{title}</h2>
                        <p>{intro[:150]}...</p>
                        <div class="blog-meta">Vincent van Sas · {date_display} · 6 min leestijd</div>
                        <a href="{slug}.html" class="blog-read-more">Lees artikel →</a>
                    </div>
                </div>
"""
    # Insert new card at the top of the grid
    return html.replace('<div class="blog-grid">', '<div class="blog-grid">' + new_card, 1)

def main():
    topic = pick_topic()
    print(f"Genereer artikel over: {topic}")

    data = generate_article(topic)
    print(f"Titel: {data['title']}")

    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    date_display = now.strftime('%-d %B %Y').replace(
        'January', 'januari').replace('February', 'februari').replace(
        'March', 'maart').replace('April', 'april').replace(
        'May', 'mei').replace('June', 'juni').replace(
        'July', 'juli').replace('August', 'augustus').replace(
        'September', 'september').replace('October', 'oktober').replace(
        'November', 'november').replace('December', 'december')

    slug = slugify(data['title'])
    tag = get_tag(topic)

    # Write article
    article_path = f'blog/{slug}.html'
    article_html = build_article_html(data, slug, tag, date_str, date_display)
    with open(article_path, 'w') as f:
        f.write(article_html)
    print(f"Artikel geschreven: {article_path}")

    # Update blog index
    index_html = load_blog_index()
    updated_index = add_card_to_index(index_html, data['title'], data['intro'], slug, tag, date_display)
    with open('blog/index.html', 'w') as f:
        f.write(updated_index)
    print("Blog index bijgewerkt")

if __name__ == '__main__':
    main()
