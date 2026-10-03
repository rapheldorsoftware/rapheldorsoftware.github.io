"""Build static, indexable pages with no frontend dependencies.

Run: python tools/build_site.py
"""
from pathlib import Path
from html import escape
import json
import hashlib
import re
import sys
from urllib.parse import quote
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'content'))
from ui import UI, NAMES

ROOT = Path(__file__).resolve().parents[1]
CSS_VERSION = hashlib.sha256((ROOT/'assets/site.css').read_bytes()).hexdigest()[:12]
BASE = 'https://www.rapheldorsoftware.com'
APPS = json.loads((ROOT/'content/apps.json').read_text(encoding='utf-8'))
E = lambda value: escape(str(value), quote=True)

from home import HOME

def route(app=None, lang='en'):
    stem=f'/{app["id"]}/' if app else '/'
    return stem if lang=='en' else stem+lang+'/'

def home_lang(lang): return lang if lang in HOME else 'en'

def languages(app,lang):
    codes=sorted(HOME if app is None else app['locales'],key=lambda k:(k not in ('en','tr'),k))
    links=''.join(f'<a href="{route(app,c)+("?lang=en" if app is None and c=="en" else "")}" data-site-language="{c}" lang="{c}" hreflang="{c}"'+(' aria-current="page"' if c==lang else '')+f'>{E(NAMES[c])}</a>' for c in codes)
    return f'<details class="language-menu"><summary aria-label="{E(UI[lang]["language"])}">{E(NAMES[lang])}<span aria-hidden="true">⌄</span></summary><div class="language-options">{links}</div></details>'

def header(app,lang):
    u=UI[lang];home=route(None,home_lang(lang))
    return f'''<a class="skip" href="#main">{E(u['skip'])}</a>
<header class="site-header"><div class="wrap header-inner">
<a class="brand" href="{home}" aria-label="Rapheldor Software"><img src="/assets/brand-mark.webp" width="38" height="38" alt=""><span>Rapheldor<span class="brand-small">Software</span></span></a>
<nav aria-label="Rapheldor Software"><a href="{home}#apps">{E(u['apps'])}</a><a href="{home}#contact">{E(u['support'])}</a></nav>
{languages(app,lang)}</div></header>'''

def footer(lang,app=None):
    u=UI[lang]; query='?app='+app['id'] if app else ''
    return f'''<footer class="site-footer wrap"><a class="footer-brand" href="{route(None,home_lang(lang))}">Rapheldor Software</a>
<span>© 2026 Rapheldor Software</span><div><a href="/privacy{query}">Privacy policy</a><a href="/terms{query}">Terms of use</a><a href="mailto:rapheldorsoftware@gmail.com">{E(u['support'])}</a></div></footer>'''

def page(title,description,body,path,lang,app=None,extra_head=''):
    image='/'+(app['images'][0] if app else 'assets/social-preview.png')
    locales=app['locales'] if app else HOME
    alternatives=''.join(f'<link rel="alternate" hreflang="{c}" href="{BASE}{route(app,c)}">' for c in locales)
    alternatives+=f'<link rel="alternate" hreflang="x-default" href="{BASE}{route(app)}">'
    style=f' style="--accent:{app["accent"]};--tint:{app["tint"]}"' if app else ''
    return f'''<!doctype html><html lang="{lang}" dir="{'rtl' if lang=='ar' else 'ltr'}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(description)}"><meta name="theme-color" content="#faf9f6">
<link rel="canonical" href="{BASE}{path}">{alternatives}<link rel="icon" href="/assets/favicon.ico">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}{image}"><meta name="twitter:card" content="summary_large_image">
<script src="/assets/language.js"></script><link rel="stylesheet" href="/assets/site.css?v={CSS_VERSION}">{extra_head}<script src="/assets/site.js" defer></script></head>
<body{style}>{header(app,lang)}{body}{footer(lang,app)}</body></html>'''

def write(path,html):
    dest=ROOT/(path.strip('/')+'/index.html' if path!='/' else 'index.html')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(html+'\n',encoding='utf-8')

def category_group(app):
    return 'games' if app['category'] in ('arcade','voicegame') else 'learn' if app['category'] in ('speaking','diction') else 'tools'

def home(lang):
    c=HOME[lang];u=UI[lang]
    cards=[]
    for app in APPS:
        app_lang=lang if lang in app['locales'] else 'en'
        cards.append(f'''<a class="app-card" href="{route(app,app_lang)}" data-category="{category_group(app)}" style="--card-tint:{app['tint']};--card-accent:{app['accent']}">
<div class="card-top"><img src="/{app['icon']}" alt="" width="64" height="64" loading="lazy"><span class="card-arrow" aria-hidden="true">↗</span></div>
<h3>{E(app['name'])}</h3><p>{E(c[app['category']])}</p><span class="text-link">{E(u['explore'])} {E(app['name'])} <span aria-hidden="true">→</span></span></a>''')
    featured=''.join(f'''<a class="featured-product {a['id']}" href="{route(a,lang if lang in a['locales'] else 'en')}" style="--feature-tint:{a['tint']}"><div class="featured-caption"><img src="/{a['icon']}" alt="" width="36" height="36"><span>{E(a['name'])}</span><span aria-hidden="true">↗</span></div><img class="featured-shot" src="/{a['images'][0]}" width="270" height="480" alt="{E(a['name'])}: {E(u['screens'])}" fetchpriority="high"></a>''' for a in APPS[:2])
    filters=''.join(f'<button type="button" data-filter="{key}" aria-pressed="{str(key=="all").lower()}">{E(c[key])}</button>' for key in ('all','tools','learn','games'))
    body=f'''<main id="main"><section class="wrap home-hero"><div class="hero-copy"><p class="eyebrow brand-eyebrow">RAPHELDOR SOFTWARE</p><h1>{c['title']}</h1><p class="lead">{E(c['intro'])}</p><a class="button primary" href="#apps">{E(u['back'])}<span aria-hidden="true">↗</span></a><div class="mini-icons" aria-label="{E(c['count'])}">{''.join(f'<img src="/{a["icon"]}" width="34" height="34" alt="{E(a["name"])}">' for a in APPS)}<span>{E(c['count'])}</span></div></div><div class="hero-showcase">{featured}</div></section>
<section class="wrap apps-section" id="apps"><div class="section-heading"><div><p class="eyebrow">RAPHELDOR SOFTWARE</p><h2>{E(u['apps'])}</h2><p>{E(c['collectionBody'])}</p></div><div class="filters" role="group" aria-label="{E(u['apps'])}">{filters}</div></div><div class="app-grid">{''.join(cards)}</div><p class="filter-status visually-hidden" role="status" data-empty="{E(u['apps'])}: 0"></p></section>
<section class="wrap contact-section" id="contact"><div><p class="eyebrow">{E(u['contact'])}</p><h2>{E(u['support'])}</h2><p>{E(c['contactBody'])}</p></div><a class="button secondary" href="mailto:rapheldorsoftware@gmail.com">rapheldorsoftware@gmail.com<span aria-hidden="true">↗</span></a></section></main>'''
    structured={'@context':'https://schema.org','@type':'CollectionPage','name':'Rapheldor Software | '+u['apps'],'url':BASE+route(None,lang),'description':c['intro'],'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'name':a['name'],'url':BASE+route(a,lang if lang in a['locales'] else 'en')} for i,a in enumerate(APPS,1)]}}
    return page('Rapheldor Software | '+u['apps'],c['intro'],body,route(None,lang),lang,extra_head='<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False)+'</script>')

def stores(app,u):
    links=[]
    for key,label in [('play','Google Play'),('apple','App Store')]:
        if app[key]: links.append(f'<a class="button primary" href="{E(app[key])}">{label}<span aria-hidden="true">↗</span></a>')
    return ''.join(links) if links else f'<span class="release-note"><span class="status-dot"></span>{E(u["comingSoon"])}</span>'

def product(app,lang):
    d=app['locales'][lang];u=UI[lang];path=route(app,lang)
    features=''.join(f'<article class="feature"><span class="feature-number" aria-hidden="true">{i:02}</span><h3>{E(f["title"])}</h3>'+ (f'<p>{E(f["body"])}</p>' if f['body'] else '')+'</article>' for i,f in enumerate(d['features'],1))
    gallery=''.join(f'<button class="screenshot-button" type="button" data-shot="/{img}" aria-label="{E(app["name"])}: {E(u["screens"])} {i}"><img src="/{img}" alt="{E(app["name"])}: {E(u["screens"])} {i}" width="{app["imageSizes"][img][0]}" height="{app["imageSizes"][img][1]}" loading="lazy"></button>' for i,img in enumerate(app['images'],1))
    related=''.join(f'<a class="related-app" href="{route(a,lang if lang in a["locales"] else "en")}"><img src="/{a["icon"]}" width="44" height="44" alt="" loading="lazy"><span>{E(a["name"])}</span><span aria-hidden="true">↗</span></a>' for a in APPS if a['id']!=app['id'])
    body=f'''<main id="main"><section class="wrap product-hero"><div class="hero-copy"><a class="back-link" href="{route(None,home_lang(lang))}#apps"><span aria-hidden="true">←</span>{E(u['back'])}</a><div class="product-identity"><img src="/{app['icon']}" width="72" height="72" alt=""><div><p class="eyebrow">RAPHELDOR SOFTWARE</p><p class="product-name">{E(app['name'])}</p></div></div><h1>{E(d['title'])}</h1><p class="lead">{E(d['summary'])}</p><div class="store-links">{stores(app,u)}</div><a class="quiet-link" href="#features">{E(u['features'])}<span aria-hidden="true">↓</span></a></div><div class="product-showcase"><img src="/{app['images'][0]}" width="{app['imageSizes'][app['images'][0]][0]}" height="{app['imageSizes'][app['images'][0]][1]}" alt="{E(app['name'])}: {E(u['screens'])}" fetchpriority="high"></div></section>
<section class="wrap product-features" id="features"><div class="section-heading"><h2>{E(u['features'])}</h2><span class="section-index" aria-hidden="true">01</span></div><div class="feature-grid">{features}</div></section>
<section class="gallery-section"><div class="wrap"><div class="section-heading"><div><h2>{E(u['screens'])}</h2><p>{E(u['imageNote'])}</p></div><span class="section-index" aria-hidden="true">02</span></div><div class="screens-grid">{gallery}</div></div></section>
<section class="wrap product-download" id="download"><img src="/{app['icon']}" width="64" height="64" alt="" loading="lazy"><div><p class="eyebrow">{E(app['name'])}</p><h2>{E(u['getApp'])}</h2></div><div class="store-links">{stores(app,u)}</div></section>
<section class="wrap product-support"><div><h2>{E(u['support'])}</h2><a href="mailto:rapheldorsoftware@gmail.com">rapheldorsoftware@gmail.com</a></div><div class="legal-links"><a href="/privacy?app={app['id']}">Privacy policy <span aria-hidden="true">↗</span></a><a href="/terms?app={app['id']}">Terms of use <span aria-hidden="true">↗</span></a><small>{E(u['englishLegal'])}</small></div></section>
<section class="wrap more-apps"><h2>{E(u['moreApps'])}</h2><div class="related-grid">{related}</div></section></main>
<dialog class="image-dialog" aria-label="{E(u['screens'])}"><div class="dialog-tools"><button type="button" data-close>{E(u['close'])} ×</button></div><img alt=""><div class="dialog-navigation"><button type="button" data-previous>{E(u['previous'])}</button><span aria-live="polite" data-position></span><button type="button" data-next>{E(u['next'])}</button></div></dialog>'''
    schema={'@context':'https://schema.org','@type':'MobileApplication','name':app['name'],'description':d['summary'],'url':BASE+path,'image':BASE+'/'+app['icon'],'applicationCategory':'GameApplication' if category_group(app)=='games' else 'LifestyleApplication','inLanguage':list(app['locales']),'featureList':[f['title'] for f in d['features']]}
    live_stores=[app[k] for k in ('play','apple') if app[k]]
    if live_stores: schema['sameAs']=live_stores
    if app['play'] and app['apple']: schema['operatingSystem']='Android, iOS'
    elif app['play']: schema['operatingSystem']='Android'
    # Do not claim an unreleased listing, rating, price or store availability.
    return page(app['name']+' | '+d['title'],d['summary'],body,path,lang,app,extra_head='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script>')

def legal(kind):
    title='Privacy policy' if kind=='privacy' else 'Terms of use'
    cards=''.join(f'<a class="related-app" href="/{kind}?app={a["id"]}"><img src="/{a["icon"]}" width="44" height="44" alt=""><span>{E(a["name"])}</span><span aria-hidden="true">→</span></a>' for a in APPS)
    body=f'''<main id="main" class="wrap legal-main"><p class="eyebrow">RAPHELDOR SOFTWARE</p><h1>{title}</h1><p class="lead">Choose an app to read its {title.lower()}.</p><nav class="legal-app-picker" aria-label="Apps">{cards}</nav><article class="policy-text" id="policy" aria-live="polite"></article></main>'''
    html=page(title+' | Rapheldor Software','Privacy and terms for Rapheldor Software apps.',body,'/'+kind,'en')
    html=html.replace('<body>','<body data-legal="'+kind+'">')
    # Legal views use their own canonical address, rather than home alternates.
    html=re.sub(r'<link rel="alternate"[^>]+>','',html)
    (ROOT/(kind+'.html')).write_text(html+'\n',encoding='utf-8')

for lang in HOME: write(route(None,lang),home(lang))
for app in APPS:
    for lang in app['locales']: write(route(app,lang),product(app,lang))
for kind in ('privacy','terms'): legal(kind)

for app_id in ('booktou','speaktou'):
    app=next(a for a in APPS if a['id']==app_id)
    fragment=(ROOT/'content'/f'account-deletion-{app_id}.html').read_text(encoding='utf-8')
    body='<main id="main" class="wrap deletion-main">'+fragment+'</main>'
    html=page('Delete your '+app['name']+' account | Rapheldor Software','How to delete your '+app['name']+' account and associated data.',body,'/'+app_id+'/account-deletion/','en',app)
    html=re.sub(r'<link rel="alternate"[^>]+>','',html)
    write('/'+app_id+'/account-deletion/',html)

paths=[route(None,c) for c in HOME]+[route(a,c) for a in APPS for c in a['locales']]
paths += ['/privacy','/terms','/booktou/account-deletion/','/speaktou/account-deletion/']
entries=''.join(f'<url><loc>{BASE}{p}</loc></url>' for p in paths)
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+entries+'</urlset>\n',encoding='utf-8')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n',encoding='utf-8')
(ROOT/'content/route-manifest.json').write_text(json.dumps(paths,indent=2)+'\n',encoding='utf-8')
print('Built',len(paths),'public routes')
