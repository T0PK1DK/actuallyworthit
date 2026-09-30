#!/usr/bin/env python3
"""Verify every Amazon link on the site.

Run after any edit that touches a product link:

    python3 tools/check-links.py

Checks, across index.html and every reviews/*.html:
  1. Every Amazon URL is the SiteStripe form /dp/<ASIN>?tag=...&linkCode=...
  2. Every Amazon link carries rel="sponsored nofollow noopener"
  3. The affiliate disclosure appears before the first buy link on the page
  4. Every ASIN used anywhere on the site exists in data/products.json,
     which catches a link left stale after an ASIN changed
  5. Every local image and internal link actually resolves

Exit code is 0 when clean, 1 when anything fails, so it can gate a deploy.
"""

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        aff["url_template"].format(asin="\x00", tag=aff["tag"], link_code=aff["link_code"])
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
