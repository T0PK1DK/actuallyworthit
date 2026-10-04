"""Image-free product art, shared by the homepage tiles and review pages.

The site does not show product photos: Amazon listing images may not be
downloaded and self-hosted under the Associates IP License, and manufacturer
press images need written permission to sit beside an affiliate link. Each
product is drawn instead as a typographic card: brand, a short model mark
and a hand-drawn category icon, tinted per category. Everything here is
original to the site.
"""

import html

_SVG = ('<svg class="cat-icon" viewBox="0 0 24 24" width="24" height="24" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true" focusable="false">%s</svg>')

ICONS = {
    "phones": '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M10.5 5.5h3"/>',
    "watches": ('<rect x="6" y="6" width="12" height="12" rx="3.2"/>'
                '<path d="M9 6l.6-3.5h4.8L15 6M9 18l.6 3.5h4.8L15 18M12 9.5V12l1.8 1.2"/>'),
    "earbuds": ('<circle cx="7.5" cy="7.5" r="3.5"/><path d="M8.5 10.9v7.6a1.5 1.5 0 0 1-3 0v-7.9"/>'
                '<circle cx="16.5" cy="7.5" r="3.5"/><path d="M15.5 10.9v7.6a1.5 1.5 0 0 0 3 0v-7.9"/>'),
    "headphones": ('<path d="M4 15v-3a8 8 0 0 1 16 0v3"/>'
                   '<rect x="3" y="14" width="4.5" height="7" rx="1.6"/>'
                   '<rect x="16.5" y="14" width="4.5" height="7" rx="1.6"/>'),
    "speakers": ('<rect x="2.5" y="7" width="19" height="10" rx="5"/>'
                 '<circle cx="8" cy="12" r="2.4"/><circle cx="16" cy="12" r="2.4"/>'),
    "gps": ('<path d="M12 21.5s-6.5-5.9-6.5-11a6.5 6.5 0 0 1 13 0c0 5.1-6.5 11-6.5 11z"/>'
            '<circle cx="12" cy="10.5" r="2.3"/>'),
}

LABELS = {
    "phones": "Phone", "watches": "Watch", "earbuds": "Earbuds",
    "headphones": "Over-ear", "speakers": "Speaker", "gps": "Satellite GPS",
}


def icon(cat):
    return _SVG % ICONS[cat]


def art_inner(p):
    """Brand, model mark and category line. Decorative: the product name is
    always in real text next to it, so the whole block is aria-hidden."""
    return ('<span class="art-mark">%s</span>'
            '<span class="art-brand">%s</span>'
            '<span class="art-mono">%s</span>'
            '<span class="art-cat">%s%s</span>'
            % (icon(p["category"]), html.escape(p["brand"]), html.escape(p["mono"]),
               icon(p["category"]), LABELS[p["category"]]))


def thumb(p, extra=""):
    """Small square used where a buy-box thumbnail used to be."""
    return ('<span class="art-thumb art-%s%s" aria-hidden="true">%s</span>'
            % (p["category"], (" " + extra) if extra else "", icon(p["category"])))
