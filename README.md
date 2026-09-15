# alkhourdajie.github.io

The personal site of Dr Alaa Al Khourdajie, published at
https://alkhourdajie.github.io

## Editing the site

Every word on the site lives in `content/`, one markdown file per page:

    content/index.md        the home page
    content/about.md
    content/research.md     publications, preprints, assessments, data and code
    content/projects.md
    content/teaching.md
    content/engagement.md
    content/people.md
    content/cv.md           hidden from the navigation

Edit the markdown, then rebuild:

    python3 build.py

That rewrites the `.html` files in the root. Commit the markdown and the HTML together
and GitHub Pages serves the result within a few minutes.

If Settings > Pages > Source is set to "GitHub Actions", the workflow in
`.github/workflows/deploy.yml` runs `build.py` for you on every push, so editing a markdown
file in the GitHub web editor is enough and no local build is needed.

## The content format

A page starts with a short header between `---` lines: `title`, `slug`, `nav`, `order`,
`standfirst`, `description`. Then ordinary markdown, with a few blocks:

    :::section 2        a full-width band. 1 = parchment, 2 = linen, 3 = dark green.
                        A section runs until the next :::section or the end of the file.
    :::cards ... :::    a grid of cards, each card starts with ###
    :::rows ... :::     bold title on one line, note on the next
    :::entries ... :::  publications, one per blank-line separated chunk
    :::years ... :::    collapsible year groups, each group starts with ### 2026
    :::buttons ... :::  one link per line, the first filled, the rest outlined
    :::video URL ... :::  a YouTube embed with text beside it
    :::quote ... :::    an italic quotation between two rules
    :::split ... :::    text and one image side by side

Inside any block a line starting with `^` becomes small grey text.

`build.py` carries the same notes at the top of the file.

## The design

One stylesheet, `styles.css`, holds the palette and the type. Every text colour clears a
contrast ratio of 7:1 against its background, body text is 18px with 1.6 line spacing, and the
layout reflows to one column on a phone. Fonts are Alegreya for headings and Atkinson
Hyperlegible for body text, both from Google Fonts.

Images live in `assets/`. Replace a file there and keep the name to swap an image without
touching any page.

## Credits

Built from the design in the Google Site rebuild, September 2026.
