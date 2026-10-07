# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

---

## 3. The selected item survives the whole run unchanged

For 5 matching queries, the `id` of `session["search_results"][0]`, the `id` of
`session["selected_item"]`, and the `id` of the `new_item` that reached both
`suggest_outfit` and `create_fit_card` are all the same

**Why this target:**
Passing an item from one step to the next is plain Python with no model
involved, so it should never fail. If it does, the cause is something like
reading the wrong session key or overwriting `selected_item`, and that would
make the outfit and the fit card describe a different item than the user was
shown. I compare `id` rather than title because two listings can share a
title, but each `id` is unique.

---

## 4. The fit card is a real caption about the right item

For 5 different matching items, each fit card (a) is 2–4 sentences long, contains that item's
exact price (e.g. `$24`) and its `platform` name, and does not start with the same first sentence
as any of the other four cards. At least 4 of 5 cards meet all three conditions.

**Why this target:**
I can't check the exact wording, since the model is meant to vary, but I can
check the things I'd be unhappy to see: a caption too long to post, one
missing the price or platform the docstring requires, or a template-like
opening repeated across items. I allow one miss because the model sometimes
rewrites a price (writing "twenty-four bucks" or "$24.00") or adds a fifth
sentence even when the prompt asks for 2–4. Fewer than 4 of 5 would mean my
prompt isn't steering it well enough.

---

## 5. Search respects the size and price the user asked for

For 5 queries that include both a size and a max price, every listing in
`session["search_results"]` has `price <= max_price` and a size token that
exactly matches the requested size. That's 5 of 5 queries, with 0 listings breaking the rule.

**Why this target:**
These filters are deterministic code with no model, so a single listing over
budget or in the wrong size is a bug. The `search_listings` docstring warns
that a plain substring check makes `"s" in "us 9"` True. This criterion
catches that exact mistake. Allowing even one bad listing would hide that
bug, and a shopper who sees an over-budget item stops trusting every
result after it.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
