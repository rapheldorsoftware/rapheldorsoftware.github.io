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
# Scripts are versioned by content too, so returning visitors never run a stale copy.
JS_VERSION = hashlib.sha256((ROOT/'assets/site.js').read_bytes()+(ROOT/'assets/language.js').read_bytes()).hexdigest()[:12]
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
<a class="brand" href="{home}"><img src="/assets/brand-mark.webp" width="28" height="28" alt=""><span>Rapheldor Software</span></a>
<nav aria-label="Rapheldor Software"><a href="{home}#apps">{E(u['apps'])}</a><a href="{home}#contact">{E(u['support'])}</a></nav>
{languages(app,lang)}</div></header>'''

def footer(lang,app=None):
    u=UI[lang]; query='?app='+app['id'] if app else ''
    html = f'''<footer class="site-footer"><div class="wrap footer-inner"><span>© 2026 Rapheldor Software</span><nav aria-label="{E(u['support'])}"><a href="/privacy{query}">Privacy policy</a><a href="/terms{query}">Terms of use</a><a href="mailto:rapheldorsoftware@gmail.com">{E(u['support'])}</a></nav></div></footer>'''
    return html.replace('/privacy?app=sleeptou','/sleeptou/privacy.html').replace('/terms?app=sleeptou','/sleeptou/terms.html')

def page(title,description,body,path,lang,app=None,extra_head=''):
    image='/'+(app['images'][0] if app else 'assets/social-preview.png')
    locales=app['locales'] if app else HOME
    alternatives=''.join(f'<link rel="alternate" hreflang="{c}" href="{BASE}{route(app,c)}">' for c in locales)
    alternatives+=f'<link rel="alternate" hreflang="x-default" href="{BASE}{route(app)}">'
    style=f' style="--accent:{app["accent"]};--tint:{app["tint"]}"' if app else ''
    return f'''<!doctype html><html lang="{lang}" dir="{'rtl' if lang=='ar' else 'ltr'}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(description)}"><meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{BASE}{path}">{alternatives}<link rel="icon" href="/assets/favicon.ico">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}{image}"><meta name="twitter:card" content="summary_large_image">
<script src="/assets/language.js?v={JS_VERSION}"></script><link rel="stylesheet" href="/assets/site.css?v={CSS_VERSION}">{extra_head}<script src="/assets/site.js?v={JS_VERSION}" defer></script></head>
<body{style}>{header(app,lang)}{body}{footer(lang,app)}</body></html>'''

def write(path,html):
    dest=ROOT/(path.strip('/')+'/index.html' if path!='/' else 'index.html')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(html+'\n',encoding='utf-8')

def category_group(app):
    return 'games' if app['category'] in ('arcade','voicegame','puzzle') else 'learn' if app['category'] in ('speaking','diction') else 'tools'

def available(app,u):
    # Plain availability line; never claims a store that has no verified listing.
    stores=[name for key,name in (('apple','App Store'),('play','Google Play')) if app[key]]
    return ' / '.join(stores) if stores else u['comingSoon']

def tile(app,lang,c,u,small=False):
    app_lang=lang if lang in app['locales'] else 'en'
    size=64 if small else 96
    extra='' if small else f'<span class="tile-sub">{E(c[app["category"]])}</span><span class="tile-note">{E(available(app,u))}</span>'
    return f'<a class="tile" href="{route(app,app_lang)}"><img class="icon" src="/{app["icon"]}" alt="" width="{size}" height="{size}" loading="lazy" style="background:{app['tint']}"><span class="tile-name">{E(app["name"])}</span>{extra}</a>'

def home(lang):
    c=HOME[lang];u=UI[lang]
    groups=''
    for key in ('tools','learn','games'):
        apps=[a for a in APPS if category_group(a)==key]
        groups+=f'<section class="group" aria-labelledby="group-{key}"><h2 id="group-{key}">{E(c[key])}</h2><div class="tiles">{"".join(tile(a,lang,c,u) for a in apps)}</div></section>'
    body=f'''<main id="main"><section class="wrap intro"><h1>{c['title']}</h1><p class="lead">{E(c['intro'])}</p></section>
<div class="wrap catalogue" id="apps">{groups}</div>
<section class="wrap contact" id="contact"><h2>{E(u['support'])}</h2><p>{E(c['contactBody'])}</p><a class="mail" href="mailto:rapheldorsoftware@gmail.com">rapheldorsoftware@gmail.com</a></section></main>'''
    structured={'@context':'https://schema.org','@type':'CollectionPage','name':'Rapheldor Software | '+u['apps'],'url':BASE+route(None,lang),'description':c['intro'],'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'name':a['name'],'url':BASE+route(a,lang if lang in a['locales'] else 'en')} for i,a in enumerate(APPS,1)]}}
    return page('Rapheldor Software | '+u['apps'],c['intro'],body,route(None,lang),lang,extra_head='<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False)+'</script>')

def stores(app,u):
    links=[]
    for key,label in [('apple','App Store'),('play','Google Play')]:
        if app[key]: links.append(f'<a class="store" href="{E(app[key])}">{label}</a>')
    return ''.join(links) if links else f'<p class="release-note">{E(u["comingSoon"])}</p>'

def product(app,lang):
    d=app['locales'][lang];u=UI[lang];c=HOME[lang];path=route(app,lang)
    features=''.join(f'<div class="feature"><h3>{E(f["title"])}</h3>'+(f'<p>{E(f["body"])}</p>' if f['body'] else '')+'</div>' for f in d['features'])
    gallery=''.join(f'<button class="shot" type="button" data-shot="/{img}" aria-label="{E(app["name"])}: {E(u["screens"])} {i}"><img src="/{img}" alt="{E(app["name"])}: {E(u["screens"])} {i}" width="{app["imageSizes"][img][0]}" height="{app["imageSizes"][img][1]}"'+(' fetchpriority="high"' if i==1 else ' loading="lazy"')+'></button>' for i,img in enumerate(app['images'],1))
    related=''.join(tile(a,lang,c,u,small=True) for a in APPS if a['id']!=app['id'])
    body=f'''<main id="main"><section class="wrap product-head"><a class="back-link" href="{route(None,home_lang(lang))}#apps">{E(u['back'])}</a>
<div class="product-grid"><img class="icon product-icon" src="/{app['icon']}" width="128" height="128" alt="" style="background:{app['tint']}"><div class="product-copy"><p class="product-name">{E(app['name'])} <span>{E(c[app['category']])}</span></p><h1>{E(d['title'])}</h1><p class="lead">{E(d['summary'])}</p><div class="store-links">{stores(app,u)}</div></div></div></section>
<section class="screens" aria-label="{E(u['screens'])}"><div class="wrap"><div class="screens-row">{gallery}</div><p class="note">{E(u['imageNote'])}</p></div></section>
<section class="wrap features" id="features"><h2>{E(u['features'])}</h2><div class="feature-list">{features}</div></section>
<section class="wrap download" id="download"><div class="download-inner"><img class="icon" src="/{app['icon']}" width="72" height="72" alt="" loading="lazy" style="background:{app['tint']}"><h2>{E(u['getApp'])}</h2><div class="store-links">{stores(app,u)}</div></div></section>
<section class="wrap product-support"><div><h2>{E(u['support'])}</h2><a href="mailto:rapheldorsoftware@gmail.com">rapheldorsoftware@gmail.com</a></div><div class="legal-links"><a href="/privacy?app={app['id']}">Privacy policy</a><a href="/terms?app={app['id']}">Terms of use</a><small>{E(u['englishLegal'])}</small></div></section>
<section class="wrap more-apps"><h2>{E(u['moreApps'])}</h2><div class="tiles small">{related}</div></section></main>
<dialog class="image-dialog" aria-label="{E(u['screens'])}"><div class="dialog-tools"><span aria-live="polite" data-position></span><button type="button" data-close>{E(u['close'])}</button></div><img alt=""><div class="dialog-navigation"><button type="button" data-previous>{E(u['previous'])}</button><button type="button" data-next>{E(u['next'])}</button></div></dialog>'''
    schema={'@context':'https://schema.org','@type':'MobileApplication','name':app['name'],'description':d['summary'],'url':BASE+path,'image':BASE+'/'+app['icon'],'applicationCategory':'GameApplication' if category_group(app)=='games' else 'LifestyleApplication','inLanguage':list(app['locales']),'featureList':[f['title'] for f in d['features']]}
    live_stores=[app[k] for k in ('play','apple') if app[k]]
    if live_stores: schema['sameAs']=live_stores
    if app['play'] and app['apple']: schema['operatingSystem']='Android, iOS'
    elif app['play']: schema['operatingSystem']='Android'
    elif app['apple']: schema['operatingSystem']='iOS'
    # Do not claim an unreleased listing, rating, price or store availability.
    if app['id']=='sleeptou':
        body=body.replace('/privacy?app=sleeptou','/sleeptou/privacy.html').replace('/terms?app=sleeptou','/sleeptou/terms.html')
        body = body.replace('</main>', (ROOT/'content/sleeptou-support.html').read_text(encoding='utf-8')+'</main>')
    return page(app['name']+' | '+d['title'],d['summary'],body,path,lang,app,extra_head='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script>')

def legal(kind):
    title='Privacy policy' if kind=='privacy' else 'Terms of use'
    cards=''.join(f'<a class="related-app" href="{('/sleeptou/'+kind+'.html') if a['id']=='sleeptou' else ('/'+kind+'?app='+a['id'])}"><img src="/{a["icon"]}" width="44" height="44" alt=""><span>{E(a["name"])}</span></a>' for a in APPS)
    cards += f'<a class="related-app" href="/{kind}?app=carsurf"><span>CarSurf</span></a>'
    cards += f'<a class="related-app" href="/{kind}?app=bumperpop"><img src="/assets/bumperpop/icon.webp" width="44" height="44" alt=""><span>Bumper Pop!</span></a>'
    body=f'''<main id="main" class="wrap legal-main"><h1>{title}</h1><p class="lead">Choose an app to read its {title.lower()}.</p><nav class="legal-app-picker" aria-label="Apps">{cards}</nav><article class="policy-text" id="policy" aria-live="polite"></article></main>'''
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
    noun='data' if app_id=='speaktou' else 'account'
    description='How to delete your '+app['name']+' '+noun+' and associated '+('records.' if app_id=='speaktou' else 'data.')
    html=page('Delete your '+app['name']+' '+noun+' | Rapheldor Software',description,body,'/'+app_id+'/account-deletion/','en',app)
    html=re.sub(r'<link rel="alternate"[^>]+>','',html)
    write('/'+app_id+'/account-deletion/',html)

paths=[route(None,c) for c in HOME]+[route(a,c) for a in APPS for c in a['locales']]
paths += ['/privacy','/terms','/booktou/account-deletion/','/speaktou/account-deletion/']
entries=''.join(f'<url><loc>{BASE}{p}</loc></url>' for p in paths)
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+entries+'</urlset>\n',encoding='utf-8')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n',encoding='utf-8')
(ROOT/'content/route-manifest.json').write_text(json.dumps(paths,indent=2)+'\n',encoding='utf-8')
print('Built',len(paths),'public routes')
