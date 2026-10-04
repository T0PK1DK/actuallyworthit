#!/usr/bin/env python3
"""Verify every Amazon link on the site.

Run after any edit that touches a product link:

    python3 tools/check-links.py

Checks, across index.html and every reviews/*.html:
  1. Every Amazon URL is Amazon's documented simple form /dp/<ASIN>/ref=nosim?tag=...
  2. Every Amazon link carries rel="sponsored nofollow noopener"
  3. The affiliate disclosure appears before the first buy link on the page
  4. Every ASIN used anywhere on the site exists in data/products.json,
     which catches a link left stale after an ASIN changed
  5. Every local image and internal link actually resolves
  6. The exact Amazon disclosure sentence is in the top banner and the footer
  7. No product photos (self-hosted /img/products/ or Amazon image hosts) and
     no dollar figures inside homepage tiles, buy boxes, or the buy dock

Exit code is 0 when clean, 1 when anything fails, so it can gate a deploy.
"""

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SENTENCE = "As an Amazon Associate I earn from qualifying purchases."


def banner_of(s):
    """The first .market-disclosure bar on the page (sitewide top banner)."""
    m = re.search(r'<div class="market-disclosure[^"]*">.*?</div>\s*</div>', s, re.S)
    return m.group(0) if m else ""


def pages():
    out = ["index.html", "about.html", "404.html"]
    rev = os.path.join(ROOT, "reviews")
    out += sorted("reviews/" + f for f in os.listdir(rev) if f.endswith(".html"))
    return out


def main():
    with io.open(os.path.join(ROOT, "data", "products.json"), encoding="utf-8") as fh:
        doc = json.load(fh)
    aff = doc["affiliate"]
    known = set(p["asin"] for p in doc["products"] if p["asin"])
    known |= set(a["asin"] for a in doc["accessories"])
    for p in doc["products"]:
        for v in p.get("variants", []):
            known.add(v["asin"])

    expected = re.escape(
        aff["url_template"].format(asin="\x00", tag=aff["tag"])
    ).replace(re.escape("\x00"), "([A-Z0-9]{10})").replace(re.escape("&"), "&amp;")
    url_re = re.compile("^" + expected + "$")

    failures = []
    total = 0
    print("%-46s %5s %5s  %s" % ("PAGE", "LINKS", "REL", "RESULT"))

    for page in pages():
        path = os.path.join(ROOT, page)
        with io.open(path, encoding="utf-8") as fh:
            s = fh.read()
        issues = []

        anchors = re.findall(r'<a\b[^>]*href="(https://www\.amazon\.com/[^"]*)"[^>]*>', s)
        tags = re.findall(r'<a\b[^>]*href="https://www\.amazon\.com/[^"]*"[^>]*>', s)
        rel_ok = [t for t in tags if 'rel="%s"' % aff["rel"] in t]
        total += len(anchors)

        for url in anchors:
            m = url_re.match(url)
            if not m:
                issues.append("malformed URL: %s" % url)
            elif m.group(1) not in known:
                issues.append("ASIN %s not in products.json (stale link?)" % m.group(1))

        if len(rel_ok) != len(tags):
            issues.append("%d link(s) missing rel" % (len(tags) - len(rel_ok)))

        if anchors:
            disc = [m.start() for m in
                    re.finditer(r'class="(?:disclosure|note|market-disclosure)"', s)]
            first_cta = s.find("https://www.amazon.com")
            if not disc or min(disc) > first_cta:
                issues.append("disclosure does not precede the first buy link")

        if SENTENCE not in banner_of(s):
            issues.append("disclosure sentence missing from top banner")
        foot = s[s.find('<footer class="site">'):]
        if SENTENCE not in foot:
            issues.append("disclosure sentence missing from footer")

        if re.search(r'/img/products/|media-amazon\.com|images-amazon\.com|ssl-images-amazon', s):
            issues.append("product photo / Amazon image reference")
        for block in re.findall(r'<article class="tile".*?</article>'
                                r'|<div class="buybox".*?</div>'
                                r'|<div class="buy-panel".*?\n</div>'
                                r'|<aside class="buy-dock".*?</aside>', s, re.S):
            if re.search(r'\$\s?\d', re.sub(r'<[^>]+>', ' ', block)):
                issues.append("price next to a buy button / in a tile")
                break

        for src in re.findall(r'src="(/[^"?]*)"', s):
            if not os.path.isfile(os.path.join(ROOT, src.lstrip("/"))):
                issues.append("missing asset " + src)

        for href in re.findall(r'href="(/[^"#?]*)"', s):
            cand = href.lstrip("/") or "index.html"
            full = os.path.join(ROOT, cand)
            if not (os.path.isfile(full) or os.path.isfile(full + ".html")
                    or os.path.isdir(full)):
                issues.append("dead link " + href)

        if issues:
            failures.append((page, issues))
        print("%-46s %5d %5d  %s"
              % (page, len(anchors), len(rel_ok), "; ".join(issues) if issues else "ok"))

    unlinked = [p["name"] for p in doc["products"] if not p["asin"]]
    print("\n%d Amazon links checked across %d pages" % (total, len(pages())))
    if unlinked:
        print("awaiting an Amazon listing (no ASIN invented): " + ", ".join(unlinked))

    if failures:
        print("\nFAILED:")
        for page, issues in failures:
            for i in issues:
                print("  %s: %s" % (page, i))
        return 1
    print("all clear")
    return 0


if __name__ == "__main__":
    sys.exit(main())
