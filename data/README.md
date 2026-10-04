# Where the Amazon links live

`products.json` is the **one place** every Amazon link on the site is defined.
Nothing else needs editing to add a product, change an ASIN, or fix a verdict.

## Adding or changing a product link

1. Open `data/products.json`.
2. Find the product (or copy an existing block) and set its `asin`.
3. Run:

```bash
python3 tools/build-index.py     # rebuilds the homepage from this file
python3 tools/check-links.py     # verifies every link site-wide
```

`check-links.py` exits non-zero if anything is wrong, so it is safe to run in CI
or before a deploy.

## The one rule: never invent an ASIN

If a product has no confirmed Amazon listing, leave `"asin": null`. The tile
then renders a disabled **"Not listed yet"** button and the line *"No ASIN — we
don't invent one"* instead of a buy link. The moment Amazon lists it, paste the
real ASIN in and rebuild — that is the whole change.

## Fields

| Field | What it does |
|---|---|
| `id` | Slug, unique per product |
| `name` | Shown on the tile |
| `brand` / `mono` | Brand line and short model mark drawn on the tile’s image-free art card (e.g. `Sony` / `XM5`) |
| `asin` | Amazon ASIN, or `null` if there is no confirmed listing |
| `condition` | `new` or `renewed`. `renewed` puts a **Renewed** flag on the image |
| `category` | Must match a `categories[].id` — drives the filter chips |
| `verdict` | `WORTH IT` or `DEPENDS`. Picks Worth's pose and the pill colour |
| `evidence` | Evidence grade shown on the tile. Currently `Sourced` everywhere |
| `dek` | One or two sentences under the product name |
| `review` | `href` and `label` of the review that covers this product |

## How the link is built

From `affiliate.url_template`:

```
https://www.amazon.com/dp/{asin}/ref=nosim?tag={tag}
```

That is the simple text-link format Amazon documents for hand-built links in
Associates Central help (“How do I build a simple text link to a specific item
on Amazon?”). It is **not** SiteStripe output: real SiteStripe links for this
account look like `…/dp/<ASIN>?th=1&linkCode=ll2&tag=…&linkId=…`. We
deliberately do not hand-add a `linkCode` (an earlier version appended
`linkCode=ll1` and wrongly called that the SiteStripe form; Amazon publishes no
definition of `linkCode`). The `tag` parameter is what Amazon documents for
attribution. Spot-check a few links with the Link Checker in Associates
Central after any change to this template.

Every generated link also carries `rel="sponsored nofollow noopener"`, which is
what Google expects on affiliate links, and the visible text is always
“Check price on Amazon” — never “Buy now” or “Add to cart”.

## No product images, no prices

Tiles and review pages do not show product photos. Amazon listing images may
not be downloaded and self-hosted (Associates IP License), and manufacturer
press images need the vendor’s written permission to sit next to an affiliate
link. Each product is drawn as a typographic card instead (`tools/art.py`).

Tiles never show a price. Review pages may show a manufacturer MSRP only when it
is labelled as MSRP, dated to its source, and not next to a buy button.
`check-links.py` fails if a self-hosted product image, an Amazon image URL, or a
dollar figure in a tile or buy box comes back.

Change `affiliate.tag` here and every link on the homepage updates on the next
build.

## Review pages

The 16 pages under `reviews/` still have their ASINs written directly in the
HTML — `build-index.py` only generates the homepage. But `check-links.py` does
validate them: it checks format, `rel`, disclosure placement, **and** that every
ASIN they link to exists in this file. So if you change an ASIN here and forget
to update the review page, the checker fails and names the page.

Variants (a second SKU of the same product, like the AirPods 5 Wireless Charging
Case) live under a product's `variants` list. They are linked from review pages
rather than getting their own homepage tile.
