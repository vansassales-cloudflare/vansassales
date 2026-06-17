import anthropic
import os
import json
import re
from datetime import datetime
import random

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

TOPICS = [
    {"topic": "Demand generation versus leadgeneratie: het fundamentele verschil dat uw aanpak bepaalt", "pillar": "Demand Generation", "tag": "Demand Generation"},
    {"topic": "Waarom autoriteit de enige duurzame bron van B2B-pipeline is", "pillar": "Autoriteit", "tag": "Autoriteit"},
    {"topic": "Community als demand generation kanaal: wat de data zegt", "pillar": "Community", "tag": "Community"},
    {"topic": "Consistentie is de meest onderschatte groeistrategie in B2B", "pillar": "Consistentie", "tag": "Consistentie"},
    {"topic": "Authenticiteit als onderscheidend vermogen in B2B-marketing", "pillar": "Authenticiteit", "tag": "Authenticiteit"},
    {"topic": "Waarom 94% van B2B-kopers al een voorkeursleverancier heeft voor het eerste gesprek", "pillar": "Demand Generation", "tag": "Demand Generation"},
    {"topic": "Het verschil tussen een netwerk en een community en waarom dat uw omzet bepaalt", "pillar": "Community", "tag": "Community"},
    {"topic": "Hoe thought leadership werkt als je het consequent volhoudt", "pillar": "Autoriteit", "tag": "Autoriteit"},
    {"topic": "Waarom de meeste B2B-contentstrategieeen na drie maanden stoppen", "pillar": "Consistentie", "tag": "Consistentie"},
    {"topic": "Dark social en de onzichtbare koopbeslissing: wat B2B-marketeers missen", "pillar": "Relevantie", "tag": "Demand Generation"},
    {"topic": "Hoe authentieke merken meer pipeline genereren dan gepolijste campagnes", "pillar": "Authenticiteit", "tag": "Authenticiteit"},
    {"topic": "Waarom kopers AI-gegenereerde content meteen herkennen en wat dat betekent voor uw strategie", "pillar": "Authenticiteit", "tag": "Authenticiteit"},
    {"topic": "Het compounding effect van consistente aanwezigheid in uw markt", "pillar": "Consistentie", "tag": "Consistentie"},
    {"topic": "Hoe je een B2B-community opbouwt die daadwerkelijk pipeline genereert", "pillar": "Community", "tag": "Community"},
    {"topic": "Relevantie is geen contentprobleem het is een strategie-probleem", "pillar": "Relevantie", "tag": "Relevantie"},
    {"topic": "Waarom de marketingfunnel niet meer bestaat en wat ervoor in de plaats is gekomen", "pillar": "Demand Generation", "tag": "Demand Generation"},
    {"topic": "Autoriteit in een niche: waarom smal beter is dan breed", "pillar": "Autoriteit", "tag": "Autoriteit"},
    {"topic": "Hoe community-led growth werkt voor kleine B2B-teams", "pillar": "Community", "tag": "Community"},
    {"topic": "Van campagnedenken naar altijd-aan marketing: de mentale switch die alles verandert", "pillar": "Consistentie", "tag": "Demand Generation"},
    {"topic": "Hoe moderne B2B-kopers beslissingen nemen en wat dat betekent voor uw go-to-market", "pillar": "Demand Generation", "tag": "Demand Generation"},
    {"topic": "Buitenlandse bedrijven in Nederland: hoe demand generation werkt in een nieuwe markt", "pillar": "Demand Generation", "tag": "Marktentree"},
    {"topic": "Hoe je bepaalt wat je doelgroep echt bezighoudt en hoe je daarop inspeelt", "pillar": "Relevantie", "tag": "Relevantie"},
    {"topic": "LinkedIn als demand generation kanaal: van likes naar pipeline", "pillar": "Community", "tag": "Community"},
    {"topic": "Thought leadership zonder zelfpromotie: hoe je autoriteit opbouwt door anderen te helpen", "pillar": "Autoriteit", "tag": "Autoriteit"},
    {"topic": "Waarom B2B-kopers vertrouwen op peers niet op vendors", "pillar": "Community", "tag": "Community"},
]

RESEARCH_FACTS = [
    "94% van B2B-koopgroepen heeft al een voorkeursleverancier bepaald voor het eerste gesprek met sales (6sense, 2025)",
    "B2B-kopers consumeren gemiddeld 13 stukken content voor ze met sales spreken, waarvan 9 in kanalen die marketeers niet kunnen tracken (HubSpot, 2025)",
    "73% van B2B-marketeers rapporteert dalende performance van tactieken die in 2023 nog werkten (LinkedIn B2B Marketing Benchmark, 2025)",
    "B2B-bedrijven met actieve communities zien 28% hogere klantretentie en 43% snellere deal velocity (CMX Community Report, 2025)",
    "Bedrijven die hun aanpak aanpasten richting demand generation zagen 2,4x meer pipeline-efficientie (LinkedIn, 2025)",
    "83% van B2B-kopers rondt 70% van het onderzoek af voor ze met een salesvertegenwoordiger spreken (Gartner)",
    "Het bouwen van autoriteit kost 6-12 maanden voor je significante, voorspelbare pipeline-impact ziet (MarketBetter, 2025)",
    "96% van B2B-marketeers gebruikt AI voor contentcreatie, maar kwaliteit bewaken is de nummer 1 uitdaging (Demand Gen Report, 2026)",
]

def slugify(text):
    text = text.lower()
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text[:70]

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
    available = [t for t in TOPICS if t['topic'] not in used]
    if not available:
        used = []
        available = TOPICS
    topic_obj = random.choice(available)
    used.append(topic_obj['topic'])
    save_used_topics(used)
    return topic_obj

def clean_json(raw):
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw)
    raw = raw.strip()
    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1:
        raw = raw[start:end+1]
    raw = raw.replace('\u2018', "'").replace('\u2019', "'")
    raw = raw.replace('\u201c', '"').replace('\u201d', '"')
    return raw

def generate_article(topic_obj):
    topic = topic_obj['topic']
    pillar = topic_obj['pillar']
    facts = random.sample(RESEARCH_FACTS, 3)
    facts_text = "\n".join(f"- {f}" for f in facts)

    prompt = f"""Write a professional B2B blog article in Dutch for vansassales.nl.

TOPIC: {topic}
PILLAR: {pillar}

TONE: Independent expert analysis. No personal career stories. No "I have X years experience". Write like a respected industry analyst sharing market insights. Direct, critical, substantive. Use concrete data.

RESEARCH DATA (include at least 2 facts naturally):
{facts_text}

CONTEXT: Modern demand generation rests on five pillars: authority, authenticity, relevance, consistency, and community. Traditional lead generation as standalone activity is outdated. Buyers decide before contacting vendors.

Return ONLY valid JSON, no markdown, no backticks. Straight double quotes only.

{{
  "title": "Compelling title max 10 words",
  "intro": "Strong opening naming the problem directly. 3-4 sentences. No self-promotion.",
  "quote": "Sharp provocative insight max 15 words.",
  "section1_heading": "First section title",
  "section1_content": "Two paragraphs 3-4 sentences each. Concrete with data.",
  "section2_heading": "Second section title",
  "section2_content": "Two paragraphs 3-4 sentences each.",
  "section3_heading": "Third section title",
  "section3_content": "Two paragraphs with practical takeaway.",
  "conclusion": "Closing 3-4 sentences. Thought-provoking not salesy.",
  "meta_description": "SEO meta max 150 characters"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text
    print(f"Response preview: {raw[:150]}")
    cleaned = clean_json(raw)
    data = json.loads(cleaned)
    data['sections'] = [
        {"heading": data.get('section1_heading', ''), "content": data.get('section1_content', '')},
        {"heading": data.get('section2_heading', ''), "content": data.get('section2_content', '')},
        {"heading": data.get('section3_heading', ''), "content": data.get('section3_content', '')},
    ]
    return data

def build_article_html(data, slug, tag, date_str, date_display):
    sections_html = ""
    for section in data['sections']:
        content = section['content'].replace('\n\n', '</p><p>').replace('\n', ' ')
        sections_html += f"\n<h2>{section['heading']}</h2>\n<p>{content}</p>"

    meta_desc = data.get('meta_description', data['intro'][:150])

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} | Van Sas Sales & Marketing</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="https://www.vansassales.nl/blog/{slug}.html">
    <link rel="stylesheet" href="../style.css">
    <style>
        .article-hero {{background:linear-gradient(135deg,#0a2342 0%,#1a3a5c 100%);color:#fff;padding:4rem 0;}}
        .article-tag {{display:inline-block;background:#d3a625;color:#fff;font-size:.75rem;font-weight:700;padding:.3rem .8rem;border-radius:20px;margin-bottom:1.25rem;text-transform:uppercase;}}
        .article-hero h1 {{font-size:2.4rem;font-family:'Montserrat',sans-serif;line-height:1.3;margin-bottom:1rem;max-width:800px;}}
        .article-meta {{opacity:.8;font-size:.95rem;}}
        .article-body {{max-width:780px;margin:0 auto;padding:4rem 0;}}
        .article-body h2 {{font-size:1.6rem;color:#0a2342;margin:2.5rem 0 1rem;font-family:'Montserrat',sans-serif;}}
        .article-body p {{font-size:1.05rem;line-height:1.85;margin-bottom:1.5rem;color:#444;}}
        .highlight-box {{background:#f0f4f9;border-left:4px solid #d3a625;padding:1.5rem 2rem;margin:2rem 0;border-radius:0 8px 8px 0;}}
        .highlight-box p {{margin:0;font-style:italic;font-size:1.1rem;color:#0a2342;}}
        .back-link {{display:inline-block;margin-bottom:2rem;color:#0a2342;font-weight:600;text-decoration:none;}}
        .author-box {{background:#fff;border-radius:8px;box-shadow:0 4px 15px rgba(0,0,0,.08);padding:2rem;display:flex;gap:1.5rem;align-items:center;margin-top:3rem;border-top:3px solid #d3a625;}}
        .author-box img {{width:70px;height:70px;border-radius:50%;object-fit:cover;}}
        .author-box h3 {{font-size:1rem;color:#0a2342;margin-bottom:.25rem;}}
        .author-box p {{font-size:.875rem;color:#666;margin:0;line-height:1.6;}}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="logo"><a href="/"><img src="../logo.png" alt="Van Sas Sales & Marketing" class="logo-img"></a></div>
            <nav><ul>
                <li><a href="/">Home</a></li>
                <li><a href="/#over">Over</a></li>
                <li><a href="/#diensten">Diensten</a></li>
                <li><a href="/#aanpak">Mijn Aanpak</a></li>
                <li><a href="/blog/" style="color:#d3a625;">Blog</a></li>
                <li><a href="/#contact">Contact</a></li>
            </ul></nav>
        </div>
    </header>
    <div class="article-hero">
        <div class="container">
            <span class="article-tag">{tag}</span>
            <h1>{data['title']}</h1>
            <p class="article-meta">Van Sas Sales &amp; Marketing &middot; {date_display} &middot; 6 min leestijd</p>
        </div>
    </div>
    <div class="container">
        <div class="article-body">
            <a href="/blog/" class="back-link">&larr; Terug naar overzicht</a>
            <p>{data['intro']}</p>
            <div class="highlight-box"><p>&ldquo;{data['quote']}&rdquo;</p></div>
            {sections_html}
            <p>{data['conclusion']}</p>
            <div class="author-box">
                <img src="../vincent.jpg" alt="Vincent van Sas" onerror="this.src='../vincent.png'">
                <div>
                    <h3>Vincent van Sas</h3>
                    <p>Sales- en marketingconsultant gespecialiseerd in demand generation, go-to-market strategie en marktentree voor IT- en cybersecuritybedrijven in Nederland.</p>
                </div>
            </div>
        </div>
    </div>
    <footer id="contact">
        <div class="container">
            <h2>Meer weten?</h2>
            <p>Neem contact op voor een vrijblijvend gesprek over demand generation voor uw organisatie.</p>
            <p class="contact-info">Email: <a href="mailto:info@vansassales.nl" class="email-link">info@vansassales.nl</a></p>
            <p class="contact-info">Tel: <a href="tel:+31613144827" class="email-link">+31 (0)6 13 14 48 27</a></p>
            <p class="copyright">&copy; 2026 Van Sas Sales &amp; Marketing. Alle rechten voorbehouden.</p>
        </div>
    </footer>
</body>
</html>"""

def load_blog_index():
    with open('blog/index.html', 'r', encoding='utf-8') as f:
        return f.read()

def add_card_to_index(html, title, intro, slug, tag, date_display):
    new_card = f"""
                <div class="blog-card">
                    <div class="blog-card-content">
                        <span class="blog-tag">{tag}</span>
                        <h2>{title}</h2>
                        <p>{intro[:150]}...</p>
                        <div class="blog-meta">Van Sas Sales &amp; Marketing &middot; {date_display} &middot; 6 min leestijd</div>
                        <a href="{slug}.html" class="blog-read-more">Lees artikel &rarr;</a>
                    </div>
                </div>
"""
    return html.replace('<div class="blog-grid">', '<div class="blog-grid">' + new_card, 1)

def format_dutch_date(now):
    months = ['januari','februari','maart','april','mei','juni',
              'juli','augustus','september','oktober','november','december']
    return f"{now.day} {months[now.month-1]} {now.year}"

def update_sitemap(slug, date_str):
    try:
        with open('sitemap.xml', 'r') as f:
            sitemap = f.read()
        new_url = f"""  <url>
    <loc>https://www.vansassales.nl/blog/{slug}.html</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""
        sitemap = sitemap.replace('</urlset>', new_url)
        with open('sitemap.xml', 'w') as f:
            f.write(sitemap)
        print(f"Sitemap bijgewerkt met {slug}")
    except Exception as e:
        print(f"Sitemap update mislukt: {e}")

def main():
    topic_obj = pick_topic()
    print(f"Onderwerp: {topic_obj['topic']}")
    print(f"Pijler: {topic_obj['pillar']}")

    data = generate_article(topic_obj)
    print(f"Titel: {data['title']}")

    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    date_display = format_dutch_date(now)
    slug = slugify(data['title'])
    if not slug:
        slug = f"artikel-{date_str}"
    tag = topic_obj['tag']

    article_path = f'blog/{slug}.html'
    article_html = build_article_html(data, slug, tag, date_str, date_display)
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(article_html)
    print(f"Artikel: {article_path}")

    index_html = load_blog_index()
    updated_index = add_card_to_index(index_html, data['title'], data['intro'], slug, tag, date_display)
    with open('blog/index.html', 'w', encoding='utf-8') as f:
        f.write(updated_index)
    print("Index bijgewerkt")

    update_sitemap(slug, date_str)

if __name__ == '__main__':
    main()
