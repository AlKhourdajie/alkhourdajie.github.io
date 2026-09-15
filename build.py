#!/usr/bin/env python3
"""
Build the site.

    python3 build.py

Reads every file in content/ and writes one HTML page per file into this folder.
Nothing to install: standard library only, Python 3.9 or newer.

CONTENT FORMAT
--------------
Each page is a markdown file in content/ with a small header:

    ---
    title: About                  the page title, and the <h1>
    slug: about                   the file written, about.html
    nav: About                    label in the navigation, or "nav: none" to hide the page
    order: 2                      position in the navigation
    standfirst: One line under the title
    banner: tall                  optional, only the home page uses it
    ---

Then the body. Ordinary markdown works: ## and ### headings, paragraphs,
[links](https://example.com), **bold**, *italic*.

Blocks open with :::name and close with :::

    :::section 2            a full-width band. 1 = parchment, 2 = linen, 3 = dark green
    :::split                text on the left, image on the right
    :::cards                a responsive grid of cards, each card starts with ###
    :::rows                 title and note pairs, each chunk starts with **Title**
    :::entries              publications, one chunk each, a line starting with ^ is small text
    :::years                collapsible groups, each group starts with ### 2026
    :::buttons              one link per line, the first is filled, the rest outlined
    :::video URL            a YouTube embed
    :::quote                an italic quotation between two rules

Every page gets the navigation and the footer automatically. Edit the footer and
the site details in SITE below.
"""

import html
import os
import re
from pathlib import Path

HERE = Path(__file__).parent
CONTENT = HERE / "content"

SITE = {
    "name": "Alaa Al Khourdajie",
    "url": "https://alkhourdajie.github.io",
    "email": "a.alkhourdajie@imperial.ac.uk",
    "role_lines": [
        "Advanced Research Fellow",
        "Department of Chemical Engineering",
        "Imperial College London",
    ],
    "elsewhere": [
        ("Google Scholar", "https://scholar.google.co.uk/citations?user=NeUIQeAAAAAJ"),
        ("ORCID", "https://orcid.org/0000-0003-1376-7529"),
        ("ResearchGate", "https://www.researchgate.net/profile/Alaa_Al_Khourdajie"),
        ("GitHub", "https://github.com/AlKhourdajie"),
        ("LinkedIn", "https://www.linkedin.com/in/alaakh"),
        ("Dimensions", "https://app.dimensions.ai/details/entities/publication/author/ur.014756040475.74"),
        ("Bluesky", "https://bsky.app/profile/dralaaclimate.bsky.social"),
        ("X", "https://twitter.com/DrAlaaClimate"),
    ],
    "updated": "September 2026",
}

# --------------------------------------------------------------------------- #
# inline markdown
# --------------------------------------------------------------------------- #

def inline(text):
    """Links, bold, italic and code inside a line of text."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return out


def chunks(lines):
    """Split a list of lines into blank-line separated groups."""
    groups, current = [], []
    for line in lines:
        if line.strip():
            current.append(line)
        elif current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return groups


# --------------------------------------------------------------------------- #
# blocks
# --------------------------------------------------------------------------- #

def render_paragraphs(lines, indent="      "):
    out = []
    for group in chunks(lines):
        if group[0].lstrip().startswith("### "):
            out.append(f'{indent}<h3>{inline(group[0].lstrip()[4:].strip())}</h3>')
            rest = group[1:]
            if rest:
                out.append(f'{indent}<p>{inline(" ".join(l.strip() for l in rest))}</p>')
            continue
        if group[0].lstrip().startswith("## "):
            out.append(f'{indent}<h2>{inline(group[0].lstrip()[3:].strip())}</h2>')
            out.append(f'{indent}<span class="rule-short"></span>')
            rest = group[1:]
            if rest:
                out.append(f'{indent}<p>{inline(" ".join(l.strip() for l in rest))}</p>')
            continue
        cls = ""
        text_lines = []
        for line in group:
            s = line.strip()
            if s.startswith("^"):
                text_lines.append(("meta", s[1:].strip()))
            elif s.startswith("{lede}"):
                cls = " class=\"lede\""
            else:
                text_lines.append(("body", s))
        body = " ".join(t for k, t in text_lines if k == "body")
        metas = [t for k, t in text_lines if k == "meta"]
        if body:
            out.append(f'{indent}<p{cls}>{inline(body)}</p>')
        for m in metas:
            out.append(f'{indent}<p class="meta">{inline(m)}</p>')
    return out


def render_cards(lines, indent="      "):
    out = [f'{indent}<div class="grid">']
    for group in chunks(lines):
        out.append(f'{indent}  <div class="card">')
        body, meta, link = [], None, None
        for line in group:
            s = line.strip()
            if s.startswith("### "):
                out.append(f'{indent}    <h3>{inline(s[4:].strip())}</h3>')
            elif s.startswith("^"):
                meta = s[1:].strip()
            elif s.startswith("[") and s.endswith(")"):
                link = s
            else:
                body.append(s)
        if meta:
            out.append(f'{indent}    <p class="meta">{inline(meta)}</p>')
        if body:
            out.append(f'{indent}    <p>{inline(" ".join(body))}</p>')
        if link:
            out.append(f'{indent}    <p class="card__link">{inline(link)}</p>')
        out.append(f'{indent}  </div>')
    out.append(f'{indent}</div>')
    return out


def render_rows(lines, indent="      ", columns=False):
    cls = "rows rows--cols" if columns else "rows"
    out = [f'{indent}<div class="{cls}">']
    for group in chunks(lines):
        out.append(f'{indent}  <div>')
        out.append(f'{indent}    <p class="row__title">{inline(group[0].strip())}</p>')
        rest = " ".join(l.strip() for l in group[1:])
        if rest:
            out.append(f'{indent}    <p class="meta">{inline(rest)}</p>')
        out.append(f'{indent}  </div>')
    out.append(f'{indent}</div>')
    return out


def render_entries(lines, indent="      "):
    out = []
    for group in chunks(lines):
        out.append(f'{indent}<div class="entry">')
        body = [l.strip() for l in group if not l.strip().startswith("^")]
        metas = [l.strip()[1:].strip() for l in group if l.strip().startswith("^")]
        if body:
            out.append(f'{indent}  <p>{inline(" ".join(body))}</p>')
        for m in metas:
            out.append(f'{indent}  <p class="meta">{inline(m)}</p>')
        out.append(f'{indent}</div>')
    return out


def render_years(lines, indent="      "):
    out, groups, current = [], [], None
    for line in lines:
        if line.strip().startswith("### "):
            if current:
                groups.append(current)
            current = {"label": line.strip()[4:].strip(), "lines": []}
        elif current is not None:
            current["lines"].append(line)
    if current:
        groups.append(current)
    for i, g in enumerate(groups):
        open_attr = " open" if i == 0 else ""
        out.append(f'{indent}<details class="year"{open_attr}>')
        out.append(f'{indent}  <summary>{html.escape(g["label"])}</summary>')
        out.append(f'{indent}  <div class="year__body">')
        out.extend(render_entries(g["lines"], indent + "    "))
        out.append(f'{indent}  </div>')
        out.append(f'{indent}</details>')
    return out


def render_buttons(lines, indent="      "):
    out = [f'{indent}<p class="buttons">']
    for i, line in enumerate([l.strip() for l in lines if l.strip()]):
        m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", line)
        if not m:
            continue
        cls = "btn" if i == 0 else "btn btn--outline"
        out.append(f'{indent}  <a class="{cls}" href="{m.group(2)}">{html.escape(m.group(1))}</a>')
    out.append(f'{indent}</p>')
    return out


def render_video(url, lines, indent="      "):
    vid = url.split("v=")[-1].split("&")[0].strip()
    out = [f'{indent}<div class="split">',
           f'{indent}  <div class="video">',
           f'{indent}    <iframe src="https://www.youtube-nocookie.com/embed/{vid}"',
           f'{indent}            title="What is climate change? Explained for the IPCC by Alaa Al Khourdajie"',
           f'{indent}            allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture"',
           f'{indent}            allowfullscreen></iframe>',
           f'{indent}  </div>',
           f'{indent}  <div class="split__text">']
    out.extend(render_paragraphs(lines, indent + "    "))
    out.append(f'{indent}  </div>')
    out.append(f'{indent}</div>')
    return out


def render_quote(lines, indent="      "):
    out = [f'{indent}<blockquote class="quote">']
    out.extend(render_paragraphs(lines, indent + "  "))
    out.append(f'{indent}</blockquote>')
    return out


def render_split(lines, indent="      "):
    """Text and one image side by side. The image line may come first or last."""
    img_line = next((l for l in lines if l.strip().startswith("![")), None)
    rest = [l for l in lines if l is not img_line]
    img_html = ""
    if img_line:
        m = re.match(r"!\[([^\]]*)\]\(([^)\s]+)\)", img_line.strip())
        if m:
            img_html = (f'{indent}  <div class="split__aside">'
                        f'<img src="{m.group(2)}" alt="{html.escape(m.group(1))}" width="560"></div>')
    first_is_image = img_line is not None and lines.index(img_line) == 0
    out = [f'{indent}<div class="split">']
    if first_is_image and img_html:
        out.append(img_html)
    out.append(f'{indent}  <div class="split__text">')
    out.extend(render_paragraphs(rest, indent + "    "))
    out.append(f'{indent}  </div>')
    if not first_is_image and img_html:
        out.append(img_html)
    out.append(f'{indent}</div>')
    return out


BLOCKS = {
    "cards": render_cards, "rows": render_rows, "entries": render_entries,
    "years": render_years, "buttons": render_buttons, "quote": render_quote,
    "split": render_split,
}


# --------------------------------------------------------------------------- #
# page assembly
# --------------------------------------------------------------------------- #

def parse_page(path):
    raw = path.read_text(encoding="utf-8").split("\n")
    meta, body_start = {}, 0
    if raw and raw[0].strip() == "---":
        for i, line in enumerate(raw[1:], start=1):
            if line.strip() == "---":
                body_start = i + 1
                break
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, raw[body_start:]


def render_body(lines):
    out, i = [], 0
    section_open = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith(":::section"):
            if section_open:
                out.append("    </div>")
                out.append("  </section>")
            style = stripped.split()[1] if len(stripped.split()) > 1 else "1"
            out.append(f'  <section class="section section--{style}">')
            out.append('    <div class="inner">')
            section_open = True
            i += 1
            continue
        if stripped == ":::" and section_open and _next_is_section_or_end(lines, i):
            out.append("    </div>")
            out.append("  </section>")
            section_open = False
            i += 1
            continue
        if stripped.startswith(":::"):
            name = stripped[3:].strip().split()[0] if stripped[3:].strip() else ""
            arg = stripped[3:].strip()[len(name):].strip()
            block, i = _collect_block(lines, i)
            if name == "video":
                out.extend(render_video(arg, block))
            elif name == "rows" and arg.startswith("columns"):
                out.extend(render_rows(block, columns=True))
            elif name in BLOCKS:
                out.extend(BLOCKS[name](block))
            continue
        # plain markdown until the next directive
        block, i = _collect_plain(lines, i)
        out.extend(render_paragraphs(block))
    if section_open:
        out.append("    </div>")
        out.append("  </section>")
    return "\n".join(out)


def _next_is_section_or_end(lines, i):
    for line in lines[i + 1:]:
        if line.strip().startswith(":::section"):
            return True
        if line.strip():
            return False
    return True


def _collect_block(lines, i):
    """Collect the lines of a :::name block, returning them and the index after it."""
    body, depth, i = [], 1, i + 1
    while i < len(lines):
        s = lines[i].strip()
        if s == ":::":
            depth -= 1
            if depth == 0:
                return body, i + 1
        body.append(lines[i])
        i += 1
    return body, i


def _collect_plain(lines, i):
    body = []
    while i < len(lines) and not lines[i].strip().startswith(":::"):
        body.append(lines[i])
        i += 1
    return body, i


def nav_html(pages, current):
    links = []
    for p in pages:
        if p["meta"].get("nav", "").lower() in ("", "none"):
            continue
        href = p["meta"]["slug"] + ".html"
        href = "index.html" if p["meta"]["slug"] == "index" else href
        aria = ' aria-current="page"' if p is current else ""
        links.append(f'      <a href="{href}"{aria}>{html.escape(p["meta"]["nav"])}</a>')
    return "\n".join(links)


def footer_html():
    role = "<br>".join(html.escape(l) for l in SITE["role_lines"])
    links = " &middot;\n        ".join(
        f'<a href="{u}">{html.escape(n)}</a>' for n, u in SITE["elsewhere"])
    return f"""  <footer class="site-footer">
    <div class="inner">
      <div>
        <h2>Dr {html.escape(SITE["name"])}</h2>
        <p>{role}<br>
        <a href="mailto:{SITE["email"]}">{SITE["email"]}</a></p>
      </div>
      <div>
        <h2>Elsewhere</h2>
        <p>{links}</p>
        <p>Last updated: {SITE["updated"]}</p>
      </div>
    </div>
  </footer>"""


TEMPLATE = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<link rel="icon" href="assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya:ital,wght@0,400;0,600;1,400&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<nav class="site-nav" aria-label="Main">
  <a class="site-nav__brand" href="index.html">
    <img src="assets/mark.png" alt="" width="30" height="30">
    <span>{sitename}</span>
  </a>
  <div class="site-nav__links">
{nav}
  </div>
</nav>
<main id="main">
  <header class="banner{banner_class}">
    <h1>{h1}</h1>
{standfirst}
  </header>
{body}
</main>
{footer}
</body>
</html>
"""


def build():
    pages = []
    for path in sorted(CONTENT.glob("*.md")):
        meta, body = parse_page(path)
        meta.setdefault("slug", path.stem)
        pages.append({"meta": meta, "body": body, "path": path})
    pages.sort(key=lambda p: int(p["meta"].get("order", 99)))

    for page in pages:
        meta = page["meta"]
        slug = meta["slug"]
        filename = "index.html" if slug == "index" else f"{slug}.html"
        standfirst = meta.get("standfirst", "").strip()
        title = meta.get("title", SITE["name"])
        page_title = title if slug == "index" else f"{title} — {SITE['name']}"
        page_title = page_title.replace("—", "|")
        out = TEMPLATE.format(
            title=html.escape(page_title),
            description=html.escape(meta.get("description", standfirst or SITE["name"])),
            canonical=f"{SITE['url']}/{'' if slug == 'index' else filename}",
            sitename=html.escape(SITE["name"]),
            nav=nav_html(pages, page),
            banner_class=" banner--tall" if meta.get("banner") == "tall" else "",
            h1=html.escape(meta.get("h1", title)),
            standfirst=f"    <p>{inline(standfirst)}</p>" if standfirst else "",
            body=render_body(page["body"]),
            footer=footer_html(),
        )
        (HERE / filename).write_text(out, encoding="utf-8")
        print(f"wrote {filename}")

    urls = "\n".join(
        f"  <url><loc>{SITE['url']}/{'' if p['meta']['slug'] == 'index' else p['meta']['slug'] + '.html'}</loc></url>"
        for p in pages)
    (HERE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n", encoding="utf-8")
    (HERE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8")
    (HERE / ".nojekyll").write_text("", encoding="utf-8")
    print("wrote sitemap.xml, robots.txt, .nojekyll")


if __name__ == "__main__":
    build()
