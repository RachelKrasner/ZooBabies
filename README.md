# 🍼 Zoo Baby Announcements

**Built live at the TinyFish × UCL AI Society Build Night (5 Oct 2026).**

A web agent that tells you when new baby animals are born at zoos around the world: their species, the baby's name (or that a name is coming soon), parents, birth date, conservation status, and a fun fact. It then turns each one into a cute "It's a girl! / It's a boy!" birth card.

**Live app:** open `index.html` (or the GitHub Pages link for this repo).

## How TinyFish is used

| Step | TinyFish endpoint | What it does |
| --- | --- | --- |
| 1 | **Search** | Finds fresh zoo birth news from the last 30 days |
| 2 | **Fetch** | Pulls the full text of each article and checks it is really about a zoo |
| 3 | **Agent** | Opens each article in a real browser and returns a structured birth card (species, name, sex, birth date, parents, IUCN status, fun fact) |
| 4 | **Monitor** | "Zoo Baby Watch" re-runs the search every day at 8am London time, so new babies keep arriving after tonight |

Tonight's run found 11 babies at 10 zoos in the USA, Ireland and Australia, including Sumatran tiger twins Barani & Malu (Fort Worth Zoo), Sarka the snow leopard (Bronx Zoo), Cassie the chimpanzee (Rockhampton Zoo) and a newborn siamang gibbon at Dublin Zoo.

## Run it yourself

```bash
pip install -r requirements.txt
export TINYFISH_API_KEY="your_key"   # get one at agent.tinyfish.ai/api-keys
python zoo_babies.py
```

Output:
- `babies.json` with the birth cards as data
- `zoo_babies.html`, a simple page of the cards

The Agent step reads each article in a real browser, so a full run takes a few minutes.

## Files

- `zoo_babies.py` is the agent (Search → Fetch → Agent, plus the Monitor setup)
- `index.html` is the cute birth-card app with tonight's results
- `requirements.txt` lists the Python dependency
