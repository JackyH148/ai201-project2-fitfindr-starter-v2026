import re

"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # TODO: replace this with your implementation
        # Words too common to count as a keyword match.
    stopwords = {"a", "an", "the", "and", "or", "for", "with", "in", "of", "to", "on"}
    keywords = [
        w for w in re.findall(r"[a-z0-9]+", (description or "").lower())
        if w not in stopwords
    ]

    wanted_size = size.strip().lower() if size else None
    results = []

    # 1. Load every listing.
    for listing in load_listings():

        # 2a. Price filter (inclusive).
        if max_price is not None and float(listing.get("price", 0)) > max_price:
            continue

        # 2b. Size filter: split "S/M" or "US 9" into tokens and require an
        # exact token match, so "s" never matches "xs" or "us 9".
        if wanted_size:
            size_tokens = re.split(r"[/\s,]+", str(listing.get("size", "")).lower())
            if wanted_size not in size_tokens:
                continue

        # 3. Score by keyword overlap across the searchable fields.
        searchable = " ".join([
            str(listing.get("title", "")),
            str(listing.get("description", "")),
            str(listing.get("category", "")),
            " ".join(listing.get("style_tags") or []),
            " ".join(listing.get("colors") or []),
            listing.get("brand") or "",          # brand is often None
        ]).lower()
        searchable_words = set(re.findall(r"[a-z0-9]+", searchable))
        score = sum(1 for w in keywords if w in searchable_words)

        # 4. Drop zero scores.
        if score > 0:
            results.append((score, listing))

    # 5. Highest score first. sort() is stable, so ties keep data order.
    results.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in results][: config.SEARCH_RESULT_LIMIT]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    # TODO: replace this with your implementation
    item_text = _describe_item(new_item)
    items = (wardrobe or {}).get("items") or []

    # 1–2. Empty wardrobe: general advice instead of failing.
    if not items:
        prompt = (
            "A shopper is thinking about buying this thrifted item:\n"
            f"{item_text}\n\n"
            "They haven't told us what's in their wardrobe. Give general styling "
            "advice: suggest 2 outfits built around this item, naming the kinds "
            "of pieces that pair well with it (e.g. 'straight-leg dark jeans', "
            "'chunky white sneakers'). Keep it under 120 words."
        )
    # 3. Wardrobe has items: name pieces they already own.
    else:
        wardrobe_lines = "\n".join(f"- {_describe_wardrobe_item(w)}" for w in items)
        prompt = (
            "A shopper is thinking about buying this thrifted item:\n"
            f"{item_text}\n\n"
            "Here is what they already own:\n"
            f"{wardrobe_lines}\n\n"
            "Suggest 1 or 2 outfits that pair the new item with specific pieces "
            "from their wardrobe. Name the wardrobe pieces exactly as listed. "
            "Keep it under 120 words."
        )

    # 4. Return the model's response, with a fallback so it's never "".
    response = (generate(prompt) or "").strip()
    return response or f"Try styling the {new_item.get('title', 'item')} with simple basics in neutral colors."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    # TODO: replace this with your implementation
        # 1. Guard against an empty outfit.
    if not outfit or not outfit.strip():
        return "Can't create a fit card: no outfit suggestion was provided."

    # 2. Build the prompt.
    price = new_item.get("price")
    price_text = f"${price:g}" if isinstance(price, (int, float)) else str(price)

    prompt = (
        "Write a 2 to 4 sentence social media caption about a thrift find. "
        "It should sound like a real person posting, not a product listing.\n\n"
        f"Item: {new_item.get('title', 'thrifted item')}\n"
        f"Price: {price_text}\n"
        f"Platform: {new_item.get('platform', 'a thrift app')}\n"
        f"Style tags: {', '.join(new_item.get('style_tags') or [])}\n"
        f"Outfit: {outfit}\n\n"
        f"Rules: mention the item, the price written exactly as {price_text}, "
        "and the platform once each. Be specific about the vibe. "
        "No hashtags, and no more than 4 sentences."
    )

    # 3. Call the model.
    caption = (generate(prompt) or "").strip()
    return caption or f"Found this {new_item.get('title', 'piece')} for {price_text} on {new_item.get('platform', 'a thrift app')}."



# ── Helper: parse_query ───────────────────────────────────────────────────────

SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL"]

def parse_query(query: str) -> dict:
    """
    Pull a description, size, and max_price out of a plain-language query
    using regex. Does not call the model.

    Args:
        query: what the user typed, e.g. "vintage graphic tee under $30, size M".

    Returns:
        A dict with exactly three keys:
            description (str):          the leftover keywords, e.g. "vintage graphic tee".
                                        "" if nothing is left.
            size (str or None):         uppercased size, e.g. "M" or "9". None if not given.
            max_price (float or None):  the price ceiling, e.g. 30.0. None if not given.

    Examples:
        parse_query("vintage graphic tee under $30, size M")
            -> {"description": "vintage graphic tee", "size": "M", "max_price": 30.0}
        parse_query("designer ballgown size XXS under $5")
            -> {"description": "designer ballgown", "size": "XXS", "max_price": 5.0}
        parse_query("denim jacket")
            -> {"description": "denim jacket", "size": None, "max_price": None}

    Test it from a terminal:
        python -c "from tools import parse_query; print(parse_query('vintage graphic tee under \$30, size M'))"
    """
    text = query or ""

    # max_price: "under $30", "below 30", "less than $30.50", "max $30", "< 30"
    max_price = None
    price_match = re.search(
        r"(?:under|below|less than|max|<)\s*\$?(\d+(?:\.\d+)?)", text, re.IGNORECASE
    )
    if price_match:
        max_price = float(price_match.group(1))
        text = text.replace(price_match.group(0), " ")

    # size: "size M", "size: xl", "size 9", or a standalone size like "XXS"
    size = None
    size_match = re.search(r"\bsize[:\s]*([a-z]{1,3}|\d+(?:\.\d+)?)\b", text, re.IGNORECASE)
    if size_match:
        size = size_match.group(1).upper()
        text = text.replace(size_match.group(0), " ")
    else:
        # Case-sensitive on purpose, so the "s" or "m" inside ordinary words
        # never counts as a size.
        for s in SIZES:
            standalone = re.search(rf"\b{s}\b", text)
            if standalone:
                size = s
                text = text.replace(standalone.group(0), " ")
                break

    # description: whatever is left, minus filler words and punctuation
    text = re.sub(
        r"\b(looking for|i want|i need|find me|show me|a|an|some)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"[,.!?$]", " ", text)
    description = " ".join(text.split())   # collapse extra spaces

    return {"description": description, "size": size, "max_price": max_price}


def _describe_item(item: dict) -> str:
    """One readable line about a listing, skipping fields that are missing."""
    parts = [str(item.get("title", "Unknown item"))]
    if item.get("brand"):
        parts.append(f"by {item['brand']}")
    if item.get("colors"):
        parts.append(f"in {', '.join(item['colors'])}")
    if item.get("size"):
        parts.append(f"size {item['size']}")
    if item.get("condition"):
        parts.append(f"({item['condition']} condition)")
    if item.get("style_tags"):
        parts.append(f"— style: {', '.join(item['style_tags'])}")
    return " ".join(parts)


def _describe_wardrobe_item(item) -> str:
    """Wardrobe items may be strings or dicts; turn either into one line."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        name = item.get("name") or item.get("title") or item.get("item")
        extras = [str(v) for k, v in item.items()
                  if k not in ("name", "title", "item", "id") and v and not isinstance(v, (list, dict))]
        return f"{name} ({', '.join(extras)})" if name and extras else (name or ", ".join(extras))
    return str(item)