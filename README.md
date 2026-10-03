# Rapheldor Software

Static showcase and product pages for eight apps. GitHub Pages serves the
checked-in HTML. No Node runtime, external font, frontend framework or tracking
script is needed by visitors.

## Build and validate

```sh
python tools/build_site.py
python tools/check_site.py
```

Content lives in `content/apps.json`; shared translated labels live in
`content/ui.py`. There are 95 product/language pages, 26 localized
showcase pages, privacy/terms views and two account-deletion pages.

Each product only lists languages verified in its app repository. The product
copy distinguishes interface languages from practice languages. Speaktou's
store links stay unpublished until a public listing is verified. No invented
store ratings, prices, download totals or release claims are included.

To deliberately refresh the source snapshot from local Flutter app repositories:

```sh
python -m pip install Pillow
python tools/import_app_content.py /path/to/flutter/projects
python tools/build_site.py
python tools/check_site.py
```

The import reads app translations without changing the app repositories. Some
marketing copy is maintained in the import script. Beanjup's language inventory
was checked against its Unity localization resources. App colors were checked
against their themes. After a refresh, review generated copy before publishing.

## Images and legal text

`content/image-sources.json` records the original Google Play image URLs and
dimensions for the imported screenshots. Existing Booktou and Speaktou assets
are preserved. Screenshots are resized/compressed without changing their aspect
ratio or drawing replacement UI. Store screenshot language can differ from the
page language; the page explains this next to the gallery.

Original legal text is under `assets/privacy` and `assets/terms`. Legal documents
are currently English and product pages disclose that in the visitor's selected
language. Account-deletion instructions are maintained as HTML fragments in
`content/account-deletion-*.html`. Legal URLs used by existing apps remain valid.

The October 2026 update corrects outdated advertising, analytics and purchase
statements for Beanjup, Dictiony and Doitly against their current code, and fills
Doitly's missing terms file. Installed-version/platform differences are stated;
this does not change store privacy declarations or app consent implementations.

## UI verification

Review desktop and narrow mobile layouts, English/Turkish language switching,
an Arabic RTL product page, category filters, gallery next/previous/Escape,
keyboard focus, policy loading and reduced-motion styles. Automated checks cover
all generated routes, local links, assets, metadata, translation inventories and
text/button color contrast. These checks are not a full accessibility audit.

The home entry follows browser/phone language, with English as the fallback.
Explicit localized URLs are honored. Manual language selections are remembered
in local storage and take precedence on later visits to the home entry.
The homepage contains app information only, without a studio biography.
