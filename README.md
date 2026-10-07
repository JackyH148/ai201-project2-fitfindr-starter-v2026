# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr helps you shop for secondhand clothes. You type what you want in plain words, like "vintage graphic tee under $30, size M". It searches the thrift listings for the best match within your size and budget, then suggests outfits that pair the item with clothes you already own. Finally, it writes a short social-media caption (a "fit card") about the find. If nothing matches, it stops and tells you what to change, such as raising your budget or trying a different size.





---

## Tool Inventory

### 1. `search_listings`

- **What it does:** Searches the listings data for items that match a keyword description, optionally filtered by size and a maximum price, and returns the best matches first.
- **Inputs:**
  - `description` (str): keywords describing the item, e.g. `"vintage graphic tee"`.
  - `size` (str or None): a size to filter by, e.g. `"M"` or `"9"`. `None` skips size filtering.
  - `max_price` (float or None): highest price allowed, inclusive. `None` skips price filtering.
- **Returns:** A list of listing dicts, highest score first, at most `config.SEARCH_RESULT_LIMIT` long. Each dict has `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None), and `platform`.
  - **Size match rule:** the listing's `size` is split on `/` and spaces into tokens, and a listing matches only if one token equals the requested size exactly, ignoring case. `"M"` matches `"S/M"` and `"m"`. `"S"` does **not** match `"XS"` or `"US 9"`. `"9"` matches `"US 9"`.
  - **Price rule:** keep a listing only if `price <= max_price`.
  - **Scoring:** the description is lowercased and split into words. A listing's score is the number of those words that appear in its `title`, `description`, `category`, `style_tags` or `colors` (and `brand` when it isn't None). Listings with a score of 0 are dropped. Ties keep the order they had in the data.
- **When nothing matches:** returns an empty list `[]`. It never returns `None` and never raises.

### 2. `suggest_outfit`

- **What it does:** Asks the model for one or two outfits built around the new item, using pieces from the user's wardrobe when it has any.
- **Inputs:**
  - `new_item` (dict): one listing dict, in the format `search_listings` returns.
  - `wardrobe` (dict): a dict with an `"items"` key holding a list of wardrobe item dicts. The list may be empty.
- **Returns:** A non-empty string with one or two outfit suggestions. When the wardrobe has items, each outfit names specific pieces from `wardrobe["items"]`.
- **When there's nothing to work with:** if `wardrobe["items"]` is empty, it returns a non-empty string of general styling advice for the item (what kinds of pieces pair well with it), and never returns `""` or raises. If the model can't be reached, `generate()` raises `ModelUnavailable`, which the loop handles (unit 4).

### 3. `create_fit_card`

- **What it does:** Asks the model for a short, social-media-style caption about the find and the outfit.
- **Inputs:**
  - `outfit` (str): the outfit suggestion returned by `suggest_outfit`.
  - `new_item` (dict): the listing dict for the item.
- **Returns:** A 2–4 sentence caption string that reads like a real post rather than a product description. It mentions the item, its `price` and its `platform` once each, and is specific about the vibe. It leaves the brand out when `brand` is None. Uses a temperature above 0 with caching off, so different runs produce different wording.
- **When there's nothing to work with:** if `outfit` is empty or only whitespace, it returns the string `"Can't create a fit card: no outfit suggestion was provided."` without calling the model and without raising.

### Helper: `parse_query`

- **What it does:** Uses regex to split the user's plain-language query into a description, a size and a max price. It does not call the model.
- **Input:** `query` (str), e.g. `"vintage graphic tee under $30, size M"`.
- **Returns:** a dict with exactly three keys: `description` (str), `size` (str or None, uppercased) and `max_price` (float or None). For example: `{"description": "vintage graphic tee", "size": "M", "max_price": 30.0}`.
- **When there's nothing to parse:** `size` and `max_price` are `None`, and `description` is `""` if no keywords are left.

## The Branch

**If `search_listings` returns an empty list,** set `session["error"]` to a message that tells the user what to change (raise the budget, try another size, or use broader keywords), then stop and return the session without calling `suggest_outfit` or `create_fit_card`.

**Otherwise,** put the first result in `session["selected_item"]`, then call `suggest_outfit` and then `create_fit_card`.

### `search_listings`

- **What it does:**
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
- **Returns:**
- **When it has nothing:**

### `suggest_outfit`

- **What it does:**
- **Inputs:**
- **Returns:**
- **When it has nothing:**

### `create_fit_card`

- **What it does:**
- **Inputs:**
- **Returns:**
- **When it has nothing:**

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that tells the user what to change (raise the budget, try another size, or use broader words), then stop and return the session without calling `suggest_outfit` or `create_fit_card`. Otherwise, put the first result in `session["selected_item"]`, then call `suggest_outfit`, and then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `tools.py::parse_query`. It finds the price ("under $30", "below 30", "max $30"), the size ("size M" or a size word like "XXS"), and uses the leftover words as the description.

**What moves through the session:** Each step saves its result in the session, and the next step reads it back from there. The order is:

1. `query` → `parse_query` → `parsed`
2. `parsed` → `search_listings` → `search_results`
3. **Branch:** if `search_results` is empty → `error` is set and the run stops
4. `search_results[0]` → `selected_item`
5. `selected_item` + `wardrobe` → `suggest_outfit` → `outfit_suggestion` (the item passed in is also saved as `item_sent_to_outfit`, so I can check it matches `selected_item`)
6. `outfit_suggestion` + `selected_item` → `create_fit_card` → `fit_card`

The loop is a `while` loop driven by a `next_step` variable. Every pass calls `trace.check_iterations(count)` so it can never run forever.


**Branch rule:**

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->

**What moves through the session:** <!-- which fields, in what order -->

---

## Sample Run

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Casual Y2K Streetwear**
Pair the Y2K Baby Tee with the baggy straight-leg jeans (dark wash) and the brown leather belt to accentuate your waist. Layer the black cropped zip hoodie over top, and finish the look with the chunky white sneakers and the black crossbody bag.

**Outfit 2: Edgy Contrast**
Tuck the Y2K Baby Tee into the wide-leg khaki trousers. Layer the vintage black denim jacket over it, and ground the outfit with the black combat boots for a cool, mixed-aesthetic vibe.

  Fit card: Found this adorable butterfly baby tee on depop for only $18 and I’m literally obsessed. It gives off major early 2000s mallrat energy, especially when you style it with baggy dark-wash jeans and a chunky belt. Honestly such a steal for a piece this nostalgic!
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None,'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
**Outfit 1: Casual Streetwear**
Pair the Vintage Levi's 501 Jeans with the **White ribbed tank top** tucked in, layered under the **Oversized grey crewneck sweatshirt**. Cinch the waist with the **Brown leather belt**, and finish with the **Chunky white sneakers** and **Black crossbody bag** for an effortless, classic look.

**Outfit 2: Edgy Contrast**
Style the Vintage Levi's 501 Jeans with the **Black cropped zip hoodie** and the **Vintage black denim jacket** on top for a cool denim-on-denim vibe. Add the **Brown leather belt** to define the waist, and lace up the **Black combat boots** to complete the outfit.```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
**Outfit 1: Casual Streetwear**
Pair the Vintage Levi's 501 Jeans with the **White ribbed tank top** tucked in, layered under the **Oversized grey crewneck sweatshirt**. Cinch the waist with the **Brown leather belt**, and finish with the **Chunky white sneakers** and **Black crossbody bag** for an effortless, classic look.

**Outfit 2: Edgy Contrast**
Style the Vintage Levi's 501 Jeans with the **Black cropped zip hoodie** and the **Vintage black denim jacket** on top for a cool denim-on-denim vibe. Add the **Brown leather belt** to define the waist, and lace up the **Black combat boots** to complete the outfit.
(.venv) (base) jacky@Jackys-MacBook-Pro ai201-project2-fitfindr-starter-v2026 % python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Finally scored these vintage Levi's 501s and I am never taking them off. Found them on depop for just $38, which feels like an absolute steal for this exact medium wash. Threw them on with my beat-up white sneakers for that effortlessly lazy 90s streetwear vibe.```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I gave Claude the TODO steps in `agent.py` and asked it to build `run_agent`.
- *What came back:* A working `while` loop with the branch, but Claude put a new `parse_query` function inside `agent.py`. It also guessed the argument names for `search_listings` because it couldn't see my `tools.py`.
- *What I changed:* I moved `parse_query` into `tools.py` so I could test it from the terminal on its own, like the other tools. I imported it into `agent.py` and checked that the `search_listings` call matched my real parameter names (`description`, `size`, `max_price`).

**Moment 2**

- *What I asked for:* The milestone said every step must read its input from the session, not pass values straight from one call to the next. I asked Claude to check my loop against that rule.
- *What came back:* It found two problems. The parse step used the `query` argument instead of `session["query"]`, and nothing recorded which item actually reached `suggest_outfit`, so I couldn't prove it was the same as `selected_item`.
- *What I changed:* I made the parse step read `session["query"]` and added a session field, `item_sent_to_outfit`. I also added PASS/FAIL checks at the bottom of `agent.py` that compare its `id` to `selected_item`, and confirm `fit_card` is still `None` on the no-match query.

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

```
$ python -c "from tools import suggest_outfit; ..."

```

```
$ python -c "from tools import create_fit_card; ..."

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
