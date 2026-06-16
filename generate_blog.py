import anthropic
import os
import json
import re
from datetime import datetime
import random

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

TOPICS = [
    {"topic": "Waarom traditionele leadgeneratie dood is en wat ervoor in de plaats komt", "angle": "Kritisch: leadgeneratie als losstaande activiteit werkt niet meer. Autoriteit en community zijn de nieuwe motor.", "tag": "Leadgeneratie 2.0"},
    {"topic": "Community als verkoopkanaal: hoe je van volgers betalende klanten maakt", "angle": "Community is niet soft, het is het meest schaalbare saleskanaal dat er bestaat als je het goed inricht.", "tag": "Community & Sales"},
    {"topic": "Buitenlandse bedrijven in Nederland: waarom remote sales vacatures een signaal zijn dat ze hulp nodig hebben", "angle": "Als een buitenlands bedrijf remote sales of marketing werft in Nederland zoeken ze eigenlijk een lokale gids.", "tag": "Marktentree Nederland"},
    {"topic": "Autoriteit opbouwen voordat je een lead aanraakt: de nieuwe volgorde in B2B sales", "angle": "81 procent van de kopers heeft al een voorkeur voor ze met sales praten. Wie dan nog koud belt verliest.", "tag": "Leadgeneratie 2.0"},
    {"topic": "Het verschil tussen een community en een mailinglijst en waarom dat je omzet bepaalt", "angle": "Een mailinglijst is een database. Een community is een gesprek. Alleen het tweede levert duurzame omzet.", "tag": "Community & Sales"},
    {"topic": "Hoe buitenlandse IT- en cybersecuritybedrijven de Nederlandse markt verkeerd benaderen", "angle": "Ze kopieren hun buitenlandse go-to-market en begrijpen de Nederlandse directheid en netwerkcultuur niet.", "tag": "Marktentree Nederland"},
    {"topic": "Leadgeneratie zonder bekendheid is geld verspillen: de wiskunde van B2B autoriteit", "angle": "Hoeveel duurder is koud acquireren versus inbound vanuit autoriteit? De cijfers zijn schokkend.", "tag": "Leadgeneratie 2.0"},
    {"topic": "Van vacature tot klant: hoe je LinkedIn-vacatures van buitenlandse bedrijven omzet in salesgesprekken", "angle": "Praktische aanpak: hoe herken je de signalen en wat werkt in de eerste conversatie.", "tag": "Marktentree Nederland"},
    {"topic": "Waarom consistent zichtbaar zijn meer oplevert dan de beste salespitch", "angle": "Consistentie in content en community bouwt vertrouwen op schaal, iets wat geen enkele koude acquisitie kan evenaren.", "tag": "Community & Sales"},
    {"topic": "De mythe van de marketingfunnel: waarom B2B kopers zich niet gedragen zoals marketeers denken", "angle": "Kopers doorlopen geen lineaire funnel. Ze orienteren zich in het donker en communities bepalen wie ze kiezen.", "tag": "Leadgeneratie 2.0"},
    {"topic": "Hoe je als sales- en marketingconsultant onmisbaar wordt voor bedrijven die Nederland betreden", "angle": "Wat buitenlandse bedrijven echt zoeken en hoe je dat als propositie formuleert.", "tag": "Marktentree Nederland"},
    {"topic": "Community-led growth: de strategie die B2B-bedrijven gebruiken om zonder advertentiebudget te groeien", "angle": "Hoe toonaangevende B2B-bedrijven community inzetten als primair groeicanaal met concrete voorbeelden.", "tag": "Community & Sales"},
    {"topic": "Thought leadership als leadgeneratie: hoe je van expertise een constante stroom van inbound klanten maakt", "angle": "Thought leadership is geen pr-activiteit. Het is een salesstrategie als je het consequent en gericht inzet.", "tag": "Leadgeneratie 2.0"},
    {"topic": "Waarom de meeste go-to-market strategieen van buitenlandse bedrijven in Nederland falen", "angle": "Ze missen lokaal netwerk, lokale autoriteit en begrijpen de Nederlandse koopbeslissing niet. Dat is jouw kans.", "tag": "Marktentree Nederland"},
    {"topic": "Hoe een buitenlands bedrijf in 90 dagen autoriteit opbouwt in de Nederlandse markt", "angle": "Concreet 90-dagen plan: van onbekend naar relevant in een nieuwe markt zonder groot budget.", "tag": "Marktentree Nederland"},
    {"topic": "LinkedIn als community-platform voor B2B: hoe je van likes naar leads komt", "angle": "LinkedIn is geen advertentiekanaal maar een community-platform. De bedrijven die dat begrijpen winnen.", "tag": "Community & Sales"},
    {"topic": "Het einde van de koude acquisitie: wat de data zegt over outbound in 2026", "angle": "Respons rates van koude outreach zijn historisch laag. Maar er is een alternatief dat wel werkt.", "tag": "Leadgeneratie 2.0"},
    {"topic": "Klantcases als community-anker: waarom bewijs de sterkste vorm van leadgeneratie is", "angle": "Klantcases zijn geen marketingmateriaal, ze zijn community-content die vertrouwen opbouwt bij nieuwe prospects.", "tag": "Community & Sales"},
    {"topic": "Waarom sales en marketing niet gescheiden mogen zijn voor bedrijven die een nieuwe markt betreden", "angle": "Silos tussen sales en marketing zijn dodelijk voor marktentrees. De oplossing: een geintegreerde commerciele strategie.", "tag": "Marktentree Nederland"},
    {"topic": "Waarom consistentie belangrijker is dan creativiteit in B2B marketing", "angle": "De meeste B2B-bedrijven falen niet door gebrek aan ideeen maar door gebrek aan consistentie.", "tag": "Leadgeneratie 2.0"},
]

def slugify(text):
    text = text.lower()
    for old, new in [('a','a'),('e','e'),('i','i'),('o','o'),('u','u'),('c','c'),('n','n')]:
        pass
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    # Remove non-ascii
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-z0-9-]', '', text)
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

def clean_json_response(raw):
    """Clean and extract JSON from Claude response."""
    # Remove markdown code blocks
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw)
    raw = raw.strip()
    
    # Find JSON object boundaries
    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1:
        raw = raw[start:end+1]
    
    # Replace curly/smart quotes with straight quotes
    raw = raw.replace('\u2018', "'").replace('\u2019', "'")
    raw = raw.replace('\u201c', '"').replace('\u201d', '"')
    raw = raw.replace('\u00e9', 'e').replace('\u00eb', 'e')
    
    return raw

def generate_article(topic_obj):
    topic = topic_obj['topic']
    angle = topic_obj['angle']
    tag = topic_obj['tag']

    prompt = f"""Write a professional blog article in Dutch for Vincent van Sas (vansassales.nl).

Vincent van Sas is an experienced sales and marketing consultant with decades of experience in IT, media and cybersecurity. He grew an IT hardware company from 50 million guilders to 400 million euros as marketing director.

His core vision:
- Traditional lead generation as a standalone activity is outdated
- Without authority, visibility, network and consistent strategy, lead generation is wasted money
- The new B2B sales engine: authority + community + consistency
- Foreign companies posting remote sales/marketing jobs in Netherlands need local market expertise
- Community is a commercial channel, not a soft concept

Topic: {topic}
Angle: {angle}
Tag: {tag}

Write in Dutch, first person (ik/mijn), professional and direct. No buzzwords, concrete insights and data.
Keywords to include prominently: leadgeneratie, community.

IMPORTANT: Return ONLY a valid JSON object. No markdown, no backticks, no explanation.
Use only simple straight double quotes. No smart quotes. No apostrophes in JSON keys.
Keep all text values simple - avoid special characters that could break JSON.

JSON format:
{{
  "title": "Short punchy title max 10 words",
  "intro": "Opening paragraph naming the pain point directly. 3-4 sentences.",
  "quote": "Core statement from Vincent, max 15 words, provocative",
  "section1_heading": "First section title",
  "section1_content": "Two paragraphs of 3-4 sentences each. Concrete with data.",
  "section2_heading": "Second section title", 
  "section2_content": "Two paragraphs of 3-4 sentences each.",
  "section3_heading": "Third section title",
  "section3_content": "Two paragraphs of 3-4 sentences each.",
  "conclusion": "Closing paragraph with concrete call to action. 3-4 sentences.",
  "meta_description": "SEO meta description max 150 characters"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text
    print(f"Raw response (first 200 chars): {raw[:200]}")
    
    cleaned = clean_json_response(raw)
    data = json.loads(cleaned)
    
    # Convert flat structure to sections list
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
    <title>{data['title']} | Vincent van Sas</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="https://www.vansassales.nl/blog/{slug}.html">
    <link rel="stylesheet" href="../style.css">
    <style>
        .article-hero {{background:linear-gradient(135deg,var(--primary-color) 0%,#1a3a5c 100%);color:var(--white);padding:4rem 0;}}
        .article-tag {{display:inline-block;background:var(--accent-color);color:var(--white);font-size:.75rem;font-weight:700;padding:.3rem .8rem;border-radius:20px;margin-bottom:1.25rem;text-transform:uppercase;}}
        .article-hero h1 {{font-size:2.4rem;font-family:'Montserrat',sans-serif;line-height:1.3;margin-bottom:1rem;max-width:800px;}}
        .article-meta {{opacity:.8;font-size:.95rem;}}
        .article-body {{max-width:780px;margin:0 auto;padding:4rem 0;}}
        .article-body h2 {{font-size:1.6rem;color:var(--primary-color);margin:2.5rem 0 1rem;font-family:'Montserrat',sans-serif;}}
        .article-body p {{font-size:1.05rem;line-height:1.85;margin-bottom:1.5rem;color:#444;}}
        .highlight-box {{background:#f0f4f9;border-left:4px solid var(--accent-color);padding:1.5rem 2rem;margin:2rem 0;border-radius:0 8px 8px 0;}}
        .highlight-box p {{margin:0;font-style:italic;font-size:1.1rem;color:var(--primary-color);}}
        .back-link {{display:inline-block;margin-bottom:2rem;color:var(--primary-color);font-weight:600;text-decoration:none;}}
        .author-box {{background:var(--white);border-radius:8px;box-shadow:0 4px 15px rgba(0,0,0,.08);padding:2rem;display:flex;gap:1.5rem;align-items:center;margin-top:3rem;}}
        .author-box img {{width:80px;height:80px;border-radius:50%;object-fit:cover;}}
        .author-box h3 {{font-size:1.1rem;color:var(--primary-color);margin-bottom:.25rem;}}
        .author-box p {{font-size:.9rem;color:#666;margin:0;line-height:1.6;}}
        .cta-box {{background:var(--primary-color);color:var(--white);padding:2rem;border-radius:8px;margin-top:3rem;text-align:center;}}
        .cta-box h3 {{color:var(--white);font-family:'Montserrat',sans-serif;margin-bottom:.75rem;}}
        .cta-box p {{color:rgba(255,255,255,.9);margin-bottom:1.25rem;}}
        .cta-box a {{background:var(--accent-color);color:var(--white);padding:.75rem 2rem;border-radius:4px;text-decoration:none;font-weight:700;}}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="logo"><a href="/"><img src="../logo.png" alt="van Sas Sales Consultancy" class="logo-img"></a></div>
            <nav><ul>
                <li><a href="/">Home</a></li>
                <li><a href="/#over">Over</a></li>
                <li><a href="/#diensten">Diensten</a></li>
                <li><a href="/#aanpak">Mijn Aanpak</a></li>
                <li><a href="/blog/" style="color:var(--accent-color);">Blog</a></li>
                <li><a href="/#contact">Contact</a></li>
            </ul></nav>
        </div>
    </header>
    <div class="article-hero">
        <div class="container">
            <span class="article-tag">{tag}</span>
            <h1>{data['title']}</h1>
            <p class="article-meta">Vincent van Sas &middot; {date_display} &middot; {data.get('read_time','6')} min leestijd</p>
        </div>
    </div>
    <div class="container">
        <div class="article-body">
            <a href="/blog/" class="back-link">&larr; Terug naar blog</a>
            <p>{data['intro']}</p>
            <div class="highlight-box"><p>&ldquo;{data['quote']}&rdquo;</p></div>
            {sections_html}
            <p>{data['conclusion']}</p>
            <div class="cta-box">
                <h3>Uw bedrijf betreedt Nederland?</h3>
                <p>Ik help buitenlandse bedrijven met lokale marktkennis, netwerk en een commerciele strategie die werkt.</p>
                <a href="mailto:info@vansassales.nl">Plan een gesprek</a>
            </div>
            <div class="author-box">
                <img src="../vincent.png" alt="Vincent van Sas">
                <div>
                    <h3>Vincent van Sas</h3>
                    <p>Sales- en marketingconsultant met decennia ervaring in IT, media en cybersecurity. Gespecialiseerd in marktentree Nederland en leadgeneratie via community en autoriteit.</p>
                </div>
            </div>
        </div>
    </div>
    <footer id="contact">
        <div class="container">
            <h2>Sparren over uw strategie?</h2>
            <p>Neem contact op voor een vrijblijvend strategisch gesprek.</p>
            <p class="contact-info">Email: <a href="mailto:info@vansassales.nl" class="email-link">info@vansassales.nl</a></p>
            <p class="copyright">&copy; 2025 van Sas Sales &amp; Marketing. Alle rechten voorbehouden.</p>
        </div>
    </footer>
</body>
</html>"""

def load_blog_index():
    with open('blog/index.html', 'r') as f:
        return f.read()

def add_card_to_index(html, title, intro, slug, tag, date_display):
    new_card = f"""
                <div class="blog-card">
                    <div class="blog-card-content">
                        <span class="blog-tag">{tag}</span>
                        <h2>{title}</h2>
                        <p>{intro[:150]}...</p>
                        <div class="blog-meta">Vincent van Sas &middot; {date_display} &middot; 6 min leestijd</div>
                        <a href="{slug}.html" class="blog-read-more">Lees artikel &rarr;</a>
                    </div>
                </div>
"""
    return html.replace('<div class="blog-grid">', '<div class="blog-grid">' + new_card, 1)

def format_dutch_date(now):
    months = ['januari','februari','maart','april','mei','juni',
              'juli','augustus','september','oktober','november','december']
    return f"{now.day} {months[now.month-1]} {now.year}"

def main():
    topic_obj = pick_topic()
    print(f"Onderwerp: {topic_obj['topic']}")

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
    print(f"Artikel geschreven: {article_path}")

    index_html = load_blog_index()
    updated_index = add_card_to_index(index_html, data['title'], data['intro'], slug, tag, date_display)
    with open('blog/index.html', 'w', encoding='utf-8') as f:
        f.write(updated_index)
    print("Index bijgewerkt")

if __name__ == '__main__':
    main()
