import anthropic
import os
import json
import re
from datetime import datetime
import random

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

# Onderwerpen gericht op doelgroep: buitenlandse bedrijven die NL betreden
# + kritische visie op leadgeneratie + community als kernthema
TOPICS = [
    # Leadgeneratie 2.0 — kritische visie
    {
        "topic": "Waarom traditionele leadgeneratie dood is — en wat ervoor in de plaats komt",
        "angle": "Kritisch: leadgeneratie als losstaande activiteit werkt niet meer. Autoriteit en community zijn de nieuwe motor.",
        "tag": "Leadgeneratie 2.0"
    },
    {
        "topic": "Community als verkoopkanaal: hoe je van volgers betalende klanten maakt",
        "angle": "Community is niet soft — het is het meest schaalbare saleskanaal dat er bestaat als je het goed inricht.",
        "tag": "Community & Sales"
    },
    {
        "topic": "Buitenlandse bedrijven in Nederland: waarom remote sales vacatures een signaal zijn dat ze hulp nodig hebben",
        "angle": "Als een buitenlands bedrijf remote sales/marketing werft in NL, zoeken ze eigenlijk een lokale gids. Dat ben jij.",
        "tag": "Marktentree Nederland"
    },
    {
        "topic": "Autoriteit opbouwen voordat je een lead aanraakt: de nieuwe volgorde in B2B sales",
        "angle": "81% van de kopers heeft al een voorkeur voor ze met sales praten. Wie dan nog koud belt, verliest.",
        "tag": "Leadgeneratie 2.0"
    },
    {
        "topic": "Waarom bedrijven die remote sales posten in Nederland eigenlijk zoeken naar meer dan een medewerker",
        "angle": "Remote hiring is een symptoom van gebrek aan lokale marktkennis. Slim consultants herkennen dit signaal.",
        "tag": "Marktentree Nederland"
    },
    {
        "topic": "Het verschil tussen een community en een mailinglijst — en waarom dat je omzet bepaalt",
        "angle": "Een mailinglijst is een database. Een community is een gesprek. Alleen het tweede levert duurzame omzet.",
        "tag": "Community & Sales"
    },
    {
        "topic": "Hoe buitenlandse IT- en cybersecuritybedrijven de Nederlandse markt verkeerd benaderen",
        "angle": "Ze kopiëren hun buitenlandse go-to-market en begrijpen de Nederlandse directheid, netwerkcultuur en besluitvorming niet.",
        "tag": "Marktentree Nederland"
    },
    {
        "topic": "Leadgeneratie zonder bekendheid is geld verspillen: de wiskunde van B2B autoriteit",
        "angle": "Concreet: hoeveel duurder is koud acquireren vs. inbound vanuit autoriteit? De cijfers zijn schokkend.",
        "tag": "Leadgeneratie 2.0"
    },
    {
        "topic": "Van vacature tot klant: hoe je LinkedIn-vacatures van buitenlandse bedrijven omzet in salesgesprekken",
        "angle": "Praktische aanpak: hoe herken je de signalen, hoe benader je ze en wat werkt in de eerste conversatie.",
        "tag": "Marktentree Nederland"
    },
    {
        "topic": "Waarom consistent zichtbaar zijn meer oplevert dan de beste salespitch",
        "angle": "Consistentie in content en community bouwt vertrouwen op schaal — iets wat geen enkele koude acquisitie kan evenaren.",
        "tag": "Community & Sales"
    },
    {
        "topic": "De mythe van de marketingfunnel: waarom B2B kopers zich niet gedragen zoals marketeers denken",
        "angle": "Kopers doorlopen geen lineaire funnel. Ze oriënteren zich in het donker — communities en autoriteit bepalen wie ze kiezen.",
        "tag": "Leadgeneratie 2.0"
    },
    {
        "topic": "Hoe je als sales- en marketingconsultant onmisbaar wordt voor bedrijven die Nederland betreden",
        "angle": "Positionering voor consultants: wat buitenlandse bedrijven echt zoeken en hoe je dat als propositie formuleert.",
        "tag": "Marktentree Nederland"
    },
    {
        "topic": "Community-led growth: de strategie die B2B-bedrijven gebruiken om zonder advertentiebudget te groeien",
        "angle": "Hoe toonaangevende B2B-bedrijven community inzetten als primair groeicanaal — met concrete voorbeelden.",
        "tag": "Community & Sales"
    },
    {
        "topic": "Waarom de meeste go-to-market strategieën van buitenlandse bedrijven in Nederland falen",
        "angle": "Ze missen lokaal netwerk, lokale autoriteit en begrijpen de Nederlandse koopbeslissing niet. Dat is jouw kans.",
        "tag": "Marktentree Nederland"
    },
    {
        "topic": "Thought leadership als leadgeneratie: hoe je van expertise een constante stroom van inbound klanten maakt",
        "angle": "Thought leadership is geen pr-activiteit. Het is een salesstrategie — als je het consequent en gericht inzet.",
        "tag": "Leadgeneratie 2.0"
    },
    {
        "topic": "Hoe je een community bouwt rondom een nichemarkt: lessen uit de IT- en cybersecuritysector",
        "angle": "Niche communities zijn krachtiger dan brede. Kleinere, relevantere groepen leveren betere klanten op.",
        "tag": "Community & Sales"
    },
    {
        "topic": "De rol van vertrouwen in B2B sales: waarom kopers kopen van mensen die ze al kennen",
        "angle": "Vertrouwen is niet abstract — het is de som van zichtbaarheid, consistentie en relevantie over tijd.",
        "tag": "Leadgeneratie 2.0"
    },
    {
        "topic": "Hoe een buitenlands bedrijf in 90 dagen autoriteit opbouwt in de Nederlandse markt",
        "angle": "Concreet 90-dagen plan: van onbekend naar relevant in een nieuwe markt zonder groot budget.",
        "tag": "Marktentree Nederland"
    },
    {
        "topic": "Waarom sales en marketing niet gescheiden mogen zijn — zeker niet voor bedrijven die een nieuwe markt betreden",
        "angle": "Silos tussen sales en marketing zijn dodelijk voor marktentrees. De oplossing: één geïntegreerde commerciële strategie.",
        "tag": "Marktentree Nederland"
    },
    {
        "topic": "LinkedIn als community-platform voor B2B: hoe je van likes naar leads komt",
        "angle": "LinkedIn is geen advertentiekanaal maar een community-platform. De bedrijven die dat begrijpen winnen.",
        "tag": "Community & Sales"
    },
    {
        "topic": "Het einde van de koude acquisitie: wat de data zegt over outbound in 2026",
        "angle": "Respons rates van koude outreach zijn historisch laag. Maar er is een alternatief dat wél werkt.",
        "tag": "Leadgeneratie 2.0"
    },
    {
        "topic": "Hoe je als consultant buitenlandse bedrijven vindt die actief op zoek zijn naar lokale expertise",
        "angle": "Praktisch: welke signalen zoek je op LinkedIn, Indeed en Glassdoor en hoe vertaal je dat naar een eerste gesprek.",
        "tag": "Marktentree Nederland"
    },
    {
        "topic": "Van content naar conversie: hoe je thought leadership omzet in betalende klanten",
        "angle": "Content zonder conversiepad is een hobby. Hoe richt je het zo in dat autoriteit leidt tot opdrachten.",
        "tag": "Leadgeneratie 2.0"
    },
    {
        "topic": "Klantcases als community-anker: waarom bewijs de sterkste vorm van leadgeneratie is",
        "angle": "Klantcases zijn geen marketingmateriaal — ze zijn community-content die vertrouwen opbouwt bij nieuwe prospects.",
        "tag": "Community & Sales"
    },
    {
        "topic": "Waarom consistentie belangrijker is dan creativiteit in B2B marketing",
        "angle": "De meeste B2B-bedrijven falen niet door gebrek aan ideeën maar door gebrek aan consistentie. Dat is het echte probleem.",
        "tag": "Leadgeneratie 2.0"
    },
]

def get_tag(topic_obj):
    return topic_obj.get("tag", "Leadgeneratie 2.0")

def slugify(text):
    text = text.lower()
    for old, new in [('à','a'),('á','a'),('â','a'),('ã','a'),('ä','a'),('å','a'),
                     ('è','e'),('é','e'),('ê','e'),('ë','e'),('ì','i'),('í','i'),
                     ('î','i'),('ï','i'),('ò','o'),('ó','o'),('ô','o'),('õ','o'),
                     ('ö','o'),('ù','u'),('ú','u'),('û','u'),('ü','u'),('ç','c'),('ñ','n')]:
        text = text.replace(old, new)
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

def search_web(query):
    """Use Anthropic web search tool to find current data."""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": f"Search for recent statistics and research about: {query}. Give me 3-5 key facts with numbers that I can use in a blog article."}]
        )
        result = ""
        for block in response.content:
            if hasattr(block, 'text'):
                result += block.text
        return result[:2000]
    except Exception as e:
        print(f"Web search failed: {e}")
        return ""

def generate_article(topic_obj):
    topic = topic_obj['topic']
    angle = topic_obj['angle']
    tag = topic_obj['tag']

    # Search for relevant current data
    print(f"Zoeken naar actuele data...")
    search_query = f"B2B {tag} statistics research 2025 2026 Netherlands"
    search_results = search_web(search_query)

    prompt = f"""Schrijf een professioneel blogartikel voor de website van Vincent van Sas (vansassales.nl).

OVER VINCENT:
Vincent van Sas is een ervaren sales- en marketingconsultant met decennia ervaring in IT, media en cybersecurity. Hij heeft als marketingdirecteur een IT-hardwarebedrijf laten groeien van 50 miljoen gulden naar 400 miljoen euro. Hij schrijft vanuit échte praktijkervaring op directieniveau.

VINCENTS KERNVISIE (verwerk dit altijd):
- "Leadgeneratie" als losstaande marketingactiviteit is een achterhaald concept
- Zonder autoriteit, bekendheid, netwerk en een consistente strategie is leadgeneratie weggegooid geld
- De nieuwe motor van B2B sales is: autoriteit + community + consistentie = mensen willen met jou in gesprek
- Buitenlandse bedrijven die remote sales/marketing vacatures posten in Nederland zoeken eigenlijk lokale marktkennis en autoriteit — dat is de doelgroep
- Community is geen soft begrip maar een commercieel kanaal

ONDERWERP: {topic}
INVALSHOEK: {angle}
TAG: {tag}

ACTUELE DATA UIT ONDERZOEK (gebruik minimaal 2 feiten hieruit):
{search_results}

SCHRIJFINSTRUCTIES:
- Nederlands, eerste persoon (ik/mijn), professioneel en direct
- Geen buzz words, wél concrete inzichten en cijfers
- Kritisch op conservatieve marketingaanpakken
- Kernwoorden "leadgeneratie" en "community" prominent verwerken
- Schrijf voor beslissers (directeuren, CCO's, VP Sales) van buitenlandse bedrijven die NL betreden

Geef je antwoord ALLEEN als JSON zonder markdown backticks:
{{
  "title": "Pakkende, specifieke titel (max 10 woorden)",
  "intro": "Openingsparagraaf die direct de pijn of het probleem benoemt (3-4 zinnen)",
  "quote": "Kernuitspraak van Vincent, max 20 woorden, provocerend en to-the-point",
  "sections": [
    {{
      "heading": "Sectietitel",
      "content": "2 alinea's van 3-4 zinnen elk. Concreet, met cijfers waar mogelijk."
    }},
    {{
      "heading": "Sectietitel",
      "content": "2 alinea's van 3-4 zinnen elk."
    }},
    {{
      "heading": "Sectietitel",
      "content": "2 alinea's van 3-4 zinnen elk."
    }}
  ],
  "conclusion": "Afsluitende alinea met concrete oproep of reflectie (3-4 zinnen)",
  "read_time": "6",
  "meta_description": "SEO meta description van max 155 tekens"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)

def build_article_html(data, slug, tag, date_str, date_display):
    sections_html = ""
    for section in data['sections']:
        paragraphs = [p.strip() for p in section['content'].split('\n\n') if p.strip()]
        if len(paragraphs) == 1:
            paragraphs = [p.strip() for p in section['content'].split('\n') if p.strip()]
        paras_html = '\n'.join(f'<p>{p}</p>' for p in paragraphs if p)
        sections_html += f"\n            <h2>{section['heading']}</h2>\n            {paras_html}"

    meta_desc = data.get('meta_description', data['intro'][:155])

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} | Vincent van Sas</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="https://www.vansassales.nl/blog/{slug}.html">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": "{data['title']}",
      "author": {{"@type": "Person", "name": "Vincent van Sas"}},
      "datePublished": "{date_str}",
      "publisher": {{"@type": "Organization", "name": "Van Sas Sales & Marketing"}},
      "url": "https://www.vansassales.nl/blog/{slug}.html",
      "keywords": "leadgeneratie, community, sales, marketing, Nederland, buitenlandse bedrijven"
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
        .cta-box {{ background: var(--primary-color); color: var(--white); padding: 2rem; border-radius: 8px; margin-top: 3rem; text-align: center; }}
        .cta-box h3 {{ color: var(--white); font-family: 'Montserrat', sans-serif; margin-bottom: 0.75rem; }}
        .cta-box p {{ color: rgba(255,255,255,0.9); margin-bottom: 1.25rem; }}
        .cta-box a {{ background: var(--accent-color); color: var(--white); padding: 0.75rem 2rem; border-radius: 4px; text-decoration: none; font-weight: 700; }}
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

            <div class="cta-box">
                <h3>Uw bedrijf betreedt Nederland?</h3>
                <p>Ik help buitenlandse bedrijven met lokale marktkennis, netwerk en een commerciële strategie die werkt.</p>
                <a href="mailto:info@vansassales.nl">Plan een gesprek</a>
            </div>

            <div class="author-box">
                <img src="../vincent.png" alt="Vincent van Sas">
                <div>
                    <h3>Vincent van Sas</h3>
                    <p>Sales- en marketingconsultant met decennia ervaring in IT, media en cybersecurity. Gespecialiseerd in marktentree Nederland voor buitenlandse bedrijven en het bouwen van commerciële autoriteit via community en leadgeneratie 2.0.</p>
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
    with open('blog/index.html', 'r') as f:
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
    tag = get_tag(topic_obj)

    article_path = f'blog/{slug}.html'
    article_html = build_article_html(data, slug, tag, date_str, date_display)
    with open(article_path, 'w') as f:
        f.write(article_html)
    print(f"Artikel: {article_path}")

    index_html = load_blog_index()
    updated_index = add_card_to_index(index_html, data['title'], data['intro'], slug, tag, date_display)
    with open('blog/index.html', 'w') as f:
        f.write(updated_index)
    print("Index bijgewerkt")

if __name__ == '__main__':
    main()
