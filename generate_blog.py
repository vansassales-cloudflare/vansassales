import anthropic
import os
import json
import re
from datetime import datetime
import random

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

TOPICS = [
    # zoekwoord-gerichte onderwerpen: het onderwerp is tegelijk de zoekvraag waarop het artikel moet ranken
    {"topic": "Wanneer heeft uw organisatie een interim sales directeur nodig", "pillar": "Interim", "tag": "Interim Sales"},
    {"topic": "Interim sales directeur inhuren: wat het kost en wat het oplevert", "pillar": "Interim", "tag": "Interim Sales"},
    {"topic": "Interim marketing directeur: wanneer tijdelijk leiderschap meer oplevert dan werven", "pillar": "Interim", "tag": "Interim Sales"},
    {"topic": "Salesproces optimaliseren in B2B: waar de meeste omzet weglekt", "pillar": "Sales", "tag": "Sales"},
    {"topic": "Sales enablement in B2B: van dik handboek naar dagelijkse praktijk", "pillar": "Sales", "tag": "Sales"},
    {"topic": "Sales en marketing alignment: waarom het misgaat en hoe het wel kan", "pillar": "Sales", "tag": "Sales"},
    {"topic": "B2B leadgeneratie zonder koude acquisitie: wat werkt er echt", "pillar": "Demand Generation", "tag": "Demand Generation"},
    {"topic": "Demand generation strategie opzetten: een praktisch stappenplan", "pillar": "Demand Generation", "tag": "Demand Generation"},
    {"topic": "Dark social en de onzichtbare koopbeslissing: wat B2B-marketeers missen", "pillar": "Demand Generation", "tag": "Demand Generation"},
    {"topic": "Go-to-market strategie voor SaaS- en IT-bedrijven in Nederland", "pillar": "Go-to-Market", "tag": "Go-to-Market"},
    {"topic": "Marktentree in Nederland: go-to-market voor buitenlandse techbedrijven", "pillar": "Marktentree", "tag": "Marktentree"},
    {"topic": "Uw B2B-positionering aanscherpen: een praktische aanpak", "pillar": "Relevantie", "tag": "Relevantie"},
    {"topic": "Hoe je bepaalt wat je doelgroep echt bezighoudt en hoe je daarop inspeelt", "pillar": "Relevantie", "tag": "Relevantie"},
    {"topic": "Thought leadership opbouwen: praktisch stappenplan voor B2B-bedrijven", "pillar": "Autoriteit", "tag": "Autoriteit"},
    {"topic": "Waarom autoriteit de enige duurzame bron van B2B-pipeline is", "pillar": "Autoriteit", "tag": "Autoriteit"},
    {"topic": "LinkedIn-strategie voor B2B: van bedrijfspagina naar pipeline", "pillar": "Community", "tag": "Community"},
    {"topic": "Hoe je een B2B-community opbouwt die daadwerkelijk pipeline genereert", "pillar": "Community", "tag": "Community"},
    {"topic": "Het verschil tussen een netwerk en een community en waarom dat uw omzet bepaalt", "pillar": "Community", "tag": "Community"},
    {"topic": "Waarom consistentie in B2B-marketing meer oplevert dan budget", "pillar": "Consistentie", "tag": "Consistentie"},
    {"topic": "Het compounding effect van consistente aanwezigheid in uw markt", "pillar": "Consistentie", "tag": "Consistentie"},
    {"topic": "AI-content in B2B: wanneer het werkt en wanneer het uw merk schaadt", "pillar": "Authenticiteit", "tag": "Authenticiteit"},
    {"topic": "Hoe authentieke merken meer pipeline genereren dan gepolijste campagnes", "pillar": "Authenticiteit", "tag": "Authenticiteit"},
]

# interne links per pijler: [artikel-slugs], (dienst-slug, dienstnaam)
RELATED_POOL = {
    "Demand Generation": ["demand-generation-vs-leadgeneratie", "hoe-b2b-kopers-beslissen-voordat-u-berhaupt-belt"],
    "Community": ["community-als-demand-gen-kanaal-wat-de-data-onthult", "linkedin-als-demand-generation-kanaal-van-likes-naar-pipeline"],
    "Autoriteit": ["autoriteit-in-een-niche-waarom-smal-altijd-wint", "thought-leadership-werkt-alleen-als-je-het-volhoudt"],
    "Consistentie": ["consistentie-de-meest-onderschatte-groeistrategie-in-b2b", "waarom-consistente-marktaanwezigheid-uw-sterkste-verkooptool-is"],
    "Authenticiteit": ["waarom-b2b-kopers-ai-content-meteen-doorzien", "authentieke-merken-winnen-de-pipeline-strijd-van-gepolijste-campagnes"],
    "Relevantie": ["relevantie-is-geen-contentprobleem-het-is-een-strategie-probleem", "wat-je-doelgroep-echt-bezighoudt-en-hoe-je-daarop-inspeelt"],
    "Interim": ["van-50-naar-400-miljoen", "go-to-market-it-sector"],
    "Sales": ["94-van-b2b-kopers-kiest-leverancier-vr-eerste-gesprek", "waarom-b2b-kopers-peers-vertrouwen-en-vendors-negeren"],
    "Go-to-Market": ["go-to-market-it-sector", "demand-generation-vs-leadgeneratie"],
    "Marktentree": ["go-to-market-it-sector", "demand-generation-vs-leadgeneratie"],
}
SERVICE_LINK = {
    "Demand Generation": ("leadgeneratie", "Leadgeneratie & Demand Generation"),
    "Community": ("leadgeneratie", "Leadgeneratie & Demand Generation"),
    "Autoriteit": ("marketing-communicatie", "Marketing & Communicatie"),
    "Consistentie": ("marketing-communicatie", "Marketing & Communicatie"),
    "Authenticiteit": ("marketing-communicatie", "Marketing & Communicatie"),
    "Relevantie": ("positionering-marktanalyse", "Positionering & Marktanalyse"),
    "Interim": ("interim-sales-directeur", "Interim Sales Directeur"),
    "Sales": ("sales-optimalisatie", "Commerciële Optimalisatie & Sales"),
    "Go-to-Market": ("go-to-market-strategie", "Go-to-Market Strategie"),
    "Marktentree": ("go-to-market-strategie", "Go-to-Market Strategie"),
}


def article_title(slug):
    try:
        with open(f'blog/{slug}.html', encoding='utf-8') as f:
            m = re.search(r'<title>(.*?)</title>', f.read(), re.S)
        return m.group(1).split('|')[0].strip()
    except Exception:
        return slug.replace('-', ' ').capitalize()


def related_block(pillar, own_slug):
    pool = [s for s in RELATED_POOL.get(pillar, RELATED_POOL["Demand Generation"]) if s != own_slug][:2]
    svc_slug, svc_name = SERVICE_LINK.get(pillar, SERVICE_LINK["Demand Generation"])
    items = "\n".join(f'                <li><a href="/blog/{s}.html">{article_title(s)}</a></li>' for s in pool)
    return f'''<div class="related-box">
                <h2>Verder lezen</h2>
                <ul>
{items}
                </ul>
                <p>Meer weten over hoe ik dit in de praktijk aanpak? Bekijk mijn dienst <a href="/{svc_slug}/">{svc_name}</a>.</p>
            </div>'''

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

SEO: The topic doubles as the target search query. Use its main keyword naturally in the title, the first paragraph and at least one section heading — never forced or repeated unnaturally.

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

def build_article_html(data, slug, tag, date_str, date_display, pillar="Demand Generation"):
    related = related_block(pillar, slug)
    sections_html = ""
    for section in data['sections']:
        content = section['content'].replace('\n\n', '</p><p>').replace('\n', ' ')
        sections_html += f"\n<h2>{section['heading']}</h2>\n<p>{content}</p>"

    meta_desc = data.get('meta_description', data['intro'][:150])

    canonical = f"https://www.vansassales.nl/blog/{slug}.html"
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": data['title'],
        "description": meta_desc,
        "datePublished": date_str,
        "dateModified": date_str,
        "inLanguage": "nl-NL",
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "image": "https://www.vansassales.nl/vincent.jpg",
        "author": {"@type": "Person", "name": "Vincent van Sas",
                   "url": "https://www.vansassales.nl",
                   "sameAs": ["https://www.linkedin.com/in/vansas/"]},
        "publisher": {"@type": "Organization", "name": "Van Sas Sales & Marketing",
                      "url": "https://www.vansassales.nl",
                      "logo": {"@type": "ImageObject", "url": "https://www.vansassales.nl/logo.png"}}
    }, ensure_ascii=False, indent=2)
    esc = lambda s: s.replace('&', '&amp;').replace('"', '&quot;')

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} | Van Sas Sales & Marketing</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:title" content="{esc(data['title'])}">
    <meta property="og:description" content="{esc(meta_desc)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="article">
    <meta property="og:locale" content="nl_NL">
    <meta property="og:image" content="https://www.vansassales.nl/vincent.jpg">
    <meta property="article:published_time" content="{date_str}">
    <meta name="twitter:card" content="summary">
    <script type="application/ld+json">
{jsonld}
    </script>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header>
        <div class="container">
            <a class="wordmark" href="/" aria-label="van Sas Sales &amp; Marketing"><span class="mark">van <em>Sas</em></span><span class="mark-sub">Sales &amp; Marketing</span></a>
            <nav>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/#over">Over</a></li>
                    <li class="has-sub">
                        <a href="/#diensten">Diensten</a>
                        <ul class="subnav">
                            <li><a href="/positionering-marktanalyse/">Positionering &amp; Marktanalyse</a></li>
                            <li><a href="/go-to-market-strategie/">Go-to-Market Strategie</a></li>
                            <li><a href="/marketing-communicatie/">Marketing &amp; Communicatie</a></li>
                            <li><a href="/leadgeneratie/">Leadgeneratie &amp; Demand Generation</a></li>
                            <li><a href="/sales-optimalisatie/">Commerci&euml;le Optimalisatie &amp; Sales</a></li>
                            <li><a href="/interim-sales-directeur/">Interim Sales Directeur</a></li>
                        </ul>
                    </li>
                    <li><a href="/#aanpak">Mijn Aanpak</a></li>
                    <li><a href="/blog/" class="nav-active">Blog</a></li>
                    <li><a href="/#contact">Contact</a></li>
                </ul>
            </nav>
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
            {related}
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
            <span class="eyebrow">Contact</span>
            <h2>Meer weten?</h2>
            <p>Neem contact op voor een vrijblijvend gesprek over demand generation voor uw organisatie.</p>
            <p class="contact-info">Email: <a href="mailto:info@vansassales.nl" class="email-link">info@vansassales.nl</a></p>
            <p class="contact-info">Tel: <a href="tel:+31613144827" class="email-link">+31 (0)6 13 14 48 27</a></p>
            <p class="contact-info"><a href="https://www.linkedin.com/in/vansas/" class="email-link" target="_blank" rel="noopener">LinkedIn &rarr;</a></p>
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
    article_html = build_article_html(data, slug, tag, date_str, date_display, topic_obj['pillar'])
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
