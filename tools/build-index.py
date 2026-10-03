#!/usr/bin/env python3
"""Rebuild the homepage product grid from data/products.json.

This is the only place the homepage tiles are generated. To add a product,
change an ASIN, or fix a verdict, edit data/products.json and run:

    python3 tools/build-index.py
    python3 tools/check-links.py

Everything between <main id="main"> and </main> in index.html is replaced.
The rest of the page — head, masthead, footer — is left untouched.
"""

import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "products.json")
PAGE = os.path.join(ROOT, "index.html")


def load():
    with io.open(DATA, encoding="utf-8") as fh:
        return json.load(fh)


def buy_url(asin, aff):
    """Build the SiteStripe deep link. &amp; because it lives in an HTML attribute."""
    return aff["url_template"].format(
        asin=asin, tag=aff["tag"], link_code=aff["link_code"]
    ).replace("&", "&amp;")


def worth(pose, cls, height):
    return ('<img class="%s" src="/img/worth/v2/worth-%s.png" alt="" '
            'aria-hidden="true" height="%d" decoding="async">' % (cls, pose, height))


def image_size(path):
    """Intrinsic size, so tiles reserve space and the masonry doesn't jump."""
    from PIL import Image
    with Image.open(os.path.join(ROOT, path.lstrip("/"))) as im:
        return im.size


def rail_img(name):
    """Worth accent in the rail. Dimensions come from the file so the sprite
    set can be re-cut without this template going stale."""
    w, h = image_size("/img/worth/%s.png" % name)
    return ('<img class="worth-rail" src="/img/worth/%s.png" alt="" aria-hidden="true" '
            'width="%d" height="%d" decoding="async">' % (name, w, h))


def tile(p, aff):
    w, h = image_size(p["image"])
    verdict = p["verdict"]
    vclass = "v-worth" if verdict == "WORTH IT" else "v-depends"
    pose = "thumbs-up" if verdict == "WORTH IT" else "shrug"

    if p["asin"]:
        url = buy_url(p["asin"], aff)
        cta = ('<a class="tile-cta" href="%s" rel="%s" data-asin="%s" data-affiliate="live" '
               'aria-label="Check price on Amazon for %s, ASIN %s">Check price on Amazon</a>'
               % (url, aff["rel"], p["asin"], html.escape(p["name"]), p["asin"]))
        meta = '<span class="tile-asin">ASIN %s</span>' % p["asin"]
    else:
        # No confirmed listing. We never invent an ASIN — the tile says so instead.
        cta = ('<span class="tile-cta is-none" aria-disabled="true">%sNot listed yet</span>'
               % worth("curious", "worth-inline", 26))
        meta = '<span class="tile-asin">No ASIN — we don’t invent one</span>'

    if p["condition"] == "renewed":
        badge = '\n          <span class="flag flag-renewed">Renewed</span>'
    elif not p["asin"]:
        badge = '\n          <span class="flag flag-none">Not listed</span>'
    else:
        badge = ""

    return """        <article class="tile" data-cat="%s">
          <div class="tile-img" style="aspect-ratio:%d/%d">
            <img loading="lazy" decoding="async" src="%s" width="%d" height="%d" alt="%s">
            <span class="verdict-tag %s">%s%s</span>%s
          </div>
          <div class="tile-body">
            <h3 class="tile-name">%s</h3>
            <p class="tile-dek">%s</p>
            <div class="tile-foot"><span class="grade-chip">%s</span>%s</div>
            %s
            <p class="tile-src">Reviewed in <a href="%s">%s</a></p>
          </div>
        </article>
""" % (p["category"], w, h, p["image"], w, h, html.escape(p["alt"]),
       vclass, worth(pose, "worth-mini", 34), verdict, badge,
       html.escape(p["name"]), html.escape(p["dek"]),
       html.escape(p["evidence"]), meta, cta,
       p["review"]["href"], html.escape(p["review"]["label"]))


def main():
    doc = load()
    aff = doc["affiliate"]
    products = doc["products"]

    tiles = "".join(tile(p, aff) for p in products)
    chips = "".join(
        '\n        <button type="button" class="chip" data-filter="%s" aria-pressed="%s">%s</button>'
        % (c["id"], "true" if c["id"] == "all" else "false", html.escape(c["label"]))
        for c in doc["categories"])
    accs = "".join(
        """            <li>
              <a class="acc" href="%s" rel="%s" data-asin="%s" data-affiliate="live">
                <span class="acc-name">%s</span><span class="acc-asin">%s</span>
              </a>
              <p class="acc-note">%s</p>
            </li>
""" % (buy_url(a["asin"], aff), aff["rel"], a["asin"],
       html.escape(a["name"]), a["asin"], html.escape(a["note"]))
        for a in doc["accessories"])

    review_list = "".join(
        '          <li><a class="acc" href="%s"><span class="acc-name">%s</span></a></li>\n'
        % (r["href"], html.escape(r["label"])) for r in doc["reviews"])

    listed = sum(1 for p in products if p["asin"])
    main_html = MAIN_TEMPLATE % {
        "count": len(products),
        "reviews_count": len(doc["reviews"]),
        "listed": listed,
        "chips": chips,
        "tiles": tiles,
        "accs": accs,
        "reviews": review_list,
        "rail_unimpressed": rail_img("unimpressed-skip"),
        "rail_thinking": rail_img("thinker-tradeoffs"),
    }

    with io.open(PAGE, encoding="utf-8") as fh:
        src = fh.read()
    out = re.sub(r'<main id="main">.*?</main>\n', main_html, src, flags=re.S)
    if out == src or out.count('<main id="main">') != 1:
        sys.exit("ERROR: could not replace <main> in index.html")
    with io.open(PAGE, "w", encoding="utf-8") as fh:
        fh.write(out)

    print("index.html rebuilt from data/products.json")
    print("  %d products (%d linked, %d awaiting a listing)"
          % (len(products), listed, len(products) - listed))
    print("  %d accessories" % len(doc["accessories"]))


MAIN_TEMPLATE = """<main id="main">
  <div class="market-disclosure">
    <div class="wrap">
      Every product here was reviewed before it was listed. We don’t sell anything — every check-price link goes to Amazon, and we may earn a commission at no extra cost to you. <a href="/about.html">How we work</a>
    </div>
  </div>

  <section class="wrap browse-head" id="latest" aria-labelledby="browse-title">
    <div class="browse-head-in">
      <div class="browse-head-copy">
        <p class="kicker">%(count)d products · %(reviews_count)d reviews · every one graded Sourced</p>
        <h1 id="browse-title">Is it actually worth it?</h1>
        <p>Browse everything we’ve reviewed. Each product carries the verdict Worth reached before we linked it — and if we couldn’t confirm an Amazon listing, the tile says so instead of guessing.</p>
      </div>
      <img class="worth-hello" src="/img/worth/v2/worth-waving.png" alt="Worth, the Actually Worth It mascot, waving hello" width="503" height="440" decoding="async">
    </div>
  </section>

  <section class="wrap" aria-label="Filter by category">
    <div class="filters">%(chips)s
    </div>
  </section>

  <div class="wrap market">
    <div>
      <h2 class="vh">Reviewed products</h2>
      <div class="masonry" id="masonry">
%(tiles)s      </div>
      <p class="market-empty" id="market-empty" hidden>Nothing in that category yet.</p>
    </div>

    <aside class="rail" aria-labelledby="rail-title">
      <h2 class="vh" id="rail-title">Accessories and notes</h2>
      <div class="rail-block">
        <h2>Pairs with</h2>
        <p class="rail-sub">Accessories for iPhone 17 Pro / 18 Pro — the one page where the add-ons change the buy.</p>
        <ul>
%(accs)s        </ul>
      </div>

      <div class="rail-block">
        %(rail_unimpressed)s
        <h2>Why this rail is short</h2>
        <p class="rail-note"><b>We only list an accessory where it changes the decision.</b> A charger does not change whether you pick AirPods 5 or Pro 3, so those pages carry no rail. Padding it out would make this a shop, and we are not one.</p>
      </div>

      <div class="rail-block">
        %(rail_thinking)s
        <h2>Evidence grade</h2>
        <p class="rail-sub">All %(count)d products are graded <b>Sourced</b>: manufacturer specs and published reviews, attributed. We have run no owned testing, and we say so on every page.</p>
      </div>

      <div class="rail-block">
        <h2>Every review</h2>
        <p class="rail-sub">All %(reviews_count)d \u2014 comparisons first, then single-product reviews.</p>
        <ul>
%(reviews)s        </ul>
      </div>
    </aside>
  </div>
</main>
"""


if __name__ == "__main__":
    main()
