"""
Zoo Baby Announcements - a TinyFish web agent
Finds new baby animals born at zoos around the world and builds a cute
"birth card" page for each one.

TinyFish endpoints used:
  1. Search  - finds fresh zoo birth news
  2. Fetch   - pulls the full text of each article
  3. Agent   - reads each article page and returns a structured birth card
  4. Monitor - (created once, see create_monitor()) re-runs the search daily

Setup:
  pip install -U tinyfish
  export TINYFISH_API_KEY="your_key"   # from agent.tinyfish.ai/api-keys
  python zoo_babies.py
Output: babies.json and zoo_babies.html
"""
import json
import datetime as dt
from tinyfish import TinyFish, RunStatus

client = TinyFish()

SEARCHES = [
    "zoo baby animal born named",
    "zoo welcomes newborn cub calf",
    "zoo baby animal birth announced",
]
BIRTH_WORDS = ("born", "birth", "newborn", "baby", "cub", "calf", "welcomes")
CARD_FIELDS = (
    "zoo, city_country, species, baby_name (null if not named yet), "
    "sex, birth_date, parents, conservation_status (IUCN), "
    "fun_fact (one short sentence about the species)"
)


def find_articles(days_back=30, limit=10):
    """Step 1 - TinyFish Search: recent zoo birth news."""
    since = (dt.date.today() - dt.timedelta(days=days_back)).isoformat()
    seen, articles = set(), []
    for q in SEARCHES:
        res = client.search.query(q, domain_type="news", after_date=since)
        for r in res.results:
            url, title = r.url, (r.title or "").lower()
            if url in seen or not any(w in title for w in BIRTH_WORDS):
                continue
            seen.add(url)
            articles.append({"url": url, "title": r.title})
    return articles[:limit]


def fetch_text(urls):
    """Step 2 - TinyFish Fetch: full article text (up to 10 URLs at once)."""
    res = client.fetch.get_contents(urls=urls)
    return {r.url: r.text for r in res.results}


def make_card(url):
    """Step 3 - TinyFish Agent: read the page, return a structured birth card."""
    run = client.agent.run(
        url=url,
        goal=(
            "Read this article about a baby animal born at a zoo. Do not click "
            f"anything. Return JSON with fields: {CARD_FIELDS}. "
            'If the article is not about a zoo birth, return {"skip": true}.'
        ),
    )
    if run.status != RunStatus.COMPLETED:
        return None
    card = run.result if isinstance(run.result, dict) else json.loads(run.result)
    if card.get("skip"):
        return None
    card["source"] = url
    return card


def create_monitor():
    """Step 4 - TinyFish Monitor: run once to keep the search going daily.
    (Already created for this build as 'Zoo Baby Watch' via the TinyFish MCP,
    id 1162a612-a324-4b34-a22d-2db82f6d5aaa, runs 8am London time.
    Check docs.tinyfish.ai/monitor/api-reference if the SDK method name differs.)"""
    return client.monitor.create(
        name="Zoo Baby Watch",
        type="search",
        schedule_cron="CRON_TZ=Europe/London 0 8 * * *",
        config={"query": "zoo baby animal born named", "recency_minutes": 1440},
        purpose="A zoo announces a newly born baby animal or the baby's name",
    )


def render_html(cards):
    rows = "".join(
        f"""<article><h2>{c.get('baby_name') or 'Name coming soon'}</h2>
        <p><b>{c.get('species')}</b> · {c.get('zoo')}, {c.get('city_country')}</p>
        <p>Born {c.get('birth_date')} · {c.get('sex')} · Parents: {c.get('parents')}</p>
        <p>{c.get('fun_fact')}</p><p><i>{c.get('conservation_status')}</i>
        · <a href="{c['source']}">source</a></p></article>"""
        for c in cards
    )
    return f"""<!doctype html><meta charset="utf-8"><title>Zoo Baby Announcements</title>
<style>body{{font-family:Nunito,sans-serif;background:#fdf6f8;max-width:900px;margin:auto;padding:16px}}
article{{background:#fff;border:2px solid #f7b8cb;border-radius:24px;padding:16px;margin:16px 0}}
h2{{color:#e2678f;margin:0}}</style><h1>🍼 Zoo Baby Announcements</h1>{rows}"""


if __name__ == "__main__":
    articles = find_articles()
    print(f"Search found {len(articles)} birth stories")
    texts = fetch_text([a["url"] for a in articles])
    print(f"Fetched {len(texts)} articles")
    # only send articles that actually mention a zoo to the Agent
    cards = [c for a in articles
             if "zoo" in (texts.get(a["url"]) or "").lower()
             and (c := make_card(a["url"]))]
    print(f"Agent built {len(cards)} birth cards")
    json.dump(cards, open("babies.json", "w"), indent=2)
    open("zoo_babies.html", "w").write(render_html(cards))
    print("Saved babies.json and zoo_babies.html")
