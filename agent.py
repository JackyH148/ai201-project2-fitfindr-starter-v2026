"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import config
import trace
from tools import parse_query, suggest_outfit, create_fit_card
from mcp_client import call_tool, MCPError
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "item_sent_to_outfit": None, # the exact item passed to suggest_outfit (for checking state)
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def _kv(d: dict) -> str:
    """Show a dict as key=value pairs, so the trace shows values, not just keys."""
    return ", ".join(f"{k}={v!r}" for k, v in d.items())


def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    How it works:
        A while loop driven by `next_step`. Each pass runs one step, stores the
        result in the session, and picks the next step based on that result.
        Every step reads its inputs back out of the session — no values are
        passed straight from one tool call to the next.

        Parsing uses regex (see parse_query in tools.py).

        The branch: if search_listings returns an empty list, set
        session["error"] to a message naming what the user could change, and
        stop without calling suggest_outfit or create_fit_card. Otherwise,
        select the first result and continue.

    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    # 1. Start a session.
    session = new_session(query, wardrobe)

    # The loop: each pass looks at what the last step produced and picks the
    # next step. "done" ends the loop.
    next_step = "parse"
    count = 0

    while next_step != "done":

        # 2. Count every pass and check it before doing more work.
        count += 1
        trace.check_iterations(count)

        # 3. Parse the query — read it from the session.
        if next_step == "parse":
            session["parsed"] = parse_query(session["query"])
            trace.step("parse_query", inputs=session["query"],
                       returned=_kv(session["parsed"]))
            next_step = "search"

        # 4. Search, then BRANCH on what came back.
        elif next_step == "search":
            parsed = session["parsed"]
            search_args = {
                "description": parsed["description"],
                "size": parsed["size"],
                "max_price": parsed["max_price"],
            }
            try:
                session["search_results"] = call_tool("search_listings", search_args)
            except MCPError:
                session["error"] = (
                    "The listing search couldn't be reached, so nothing was searched. "
                    "Check that `python mcp_server.py` starts without errors, then try again."
                )
                trace.step("search_listings (via MCP)", inputs=_kv(search_args),
                           note="MCPError: server unreachable, stopping")
                next_step = "done"
                continue

            if not session["search_results"]:
                # ⚠️ The branch: nothing matched, so stop here and tell the
                # user what they could change.
                hints = []
                if parsed["max_price"] is not None:
                    hints.append(f"raise your budget above ${parsed['max_price']:g}")
                if parsed["size"]:
                    hints.append(f"try a size other than {parsed['size']}")
                hints.append(f"use broader words than \"{parsed['description']}\"")

                session["error"] = (
                    "No listings matched your search. You could "
                    + ", or ".join(hints) + "."
                )
                next_step = "done"          # do NOT go on to suggest_outfit
                trace.step("search_listings (via MCP)", inputs=_kv(search_args),
                           returned=session["search_results"],
                           note="branch: empty, stopping before suggest_outfit")
            else:
                next_step = "select"
                trace.step("search_listings (via MCP)", inputs=_kv(search_args),
                           returned=session["search_results"],
                           note="branch: results found, continuing")

        # 5. Choose an item — read the results from the session.
        elif next_step == "select":
            session["selected_item"] = session["search_results"][0]
            trace.step("select_item",
                       inputs=f"{len(session['search_results'])} results",
                       returned=session["selected_item"], note="took the top match")
            next_step = "outfit"

        # 6. Suggest an outfit — read the item and wardrobe from the session.
        elif next_step == "outfit":
            item = session["selected_item"]
            session["item_sent_to_outfit"] = item      # record what actually went in
            outfit_inputs = {
                "new_item": item.get("title"),
                "wardrobe_items": len(session["wardrobe"].get("items", [])),
            }
            try:
                session["outfit_suggestion"] = suggest_outfit(item, session["wardrobe"])
            except ModelUnavailable:
                session["error"] = (
                    f"Found \"{item.get('title')}\" (${item.get('price'):g} on "
                    f"{item.get('platform')}), but the styling model couldn't be reached, "
                    "so there's no outfit or fit card. Check GEMINI_API_KEY in your .env "
                    "and your internet connection, then try again."
                )
                trace.step("suggest_outfit", inputs=_kv(outfit_inputs),
                           note="ModelUnavailable: stopping before create_fit_card")
                next_step = "done"
                continue
            trace.step("suggest_outfit", inputs=_kv(outfit_inputs),
                       returned=session["outfit_suggestion"])
            next_step = "fit_card"

        # 7. Create the fit card — read the outfit and item from the session.
        elif next_step == "fit_card":
            fit_inputs = {
                "outfit": session["outfit_suggestion"],
                "new_item": session["selected_item"].get("title"),
            }
            try:
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"], session["selected_item"]
                )
            except ModelUnavailable:
                session["error"] = (
                    "Your outfit is ready, but the model couldn't be reached to write "
                    "the fit card. Check GEMINI_API_KEY in your .env and your internet "
                    "connection, then try again."
                )
                trace.step("create_fit_card", inputs=_kv(fit_inputs),
                           note="ModelUnavailable: no fit card")
                next_step = "done"
                continue
            trace.step("create_fit_card", inputs=_kv(fit_inputs),
                       returned=session["fit_card"])
            next_step = "done"

    # 8. Return the session.
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from pprint import pprint
    from utils.data_loader import get_example_wardrobe

    def _print_session(session):
        # Leave out the wardrobe so the printout stays readable.
        pprint({k: v for k, v in session.items() if k != "wardrobe"}, width=100)

    # ── Happy path ──
    print("=== A query the data can match ===")
    happy = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    _show(happy)
    print("\n--- full session ---")
    _print_session(happy)

    if not happy["error"]:
        selected_id = happy["selected_item"]["id"]
        sent_id = happy["item_sent_to_outfit"]["id"]
        print(f"\nCHECK selected_item id = {selected_id}, item sent to suggest_outfit id = {sent_id}")
        print("CHECK same item:", "PASS" if selected_id == sent_id else "FAIL")

    # ── No-match path ──
    print("\n=== A query it can't ===")
    empty = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    _show(empty)
    print("\n--- full session ---")
    _print_session(empty)

    print("\nCHECK fit_card is None:", "PASS" if empty["fit_card"] is None else "FAIL")
    print("CHECK suggest_outfit not called:", "PASS" if empty["item_sent_to_outfit"] is None else "FAIL")
    print("CHECK error is more than 'No results':",
          "PASS" if empty["error"] and "You could" in empty["error"] else "FAIL")