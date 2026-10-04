"""Check the generated route graph, metadata, localization and local assets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, urljoin
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'content'))
from ui import UI, NAMES
from home import HOME

ROOT=Path(__file__).resolve().parents[1]
BASE='https://www.rapheldorsoftware.com'
APPS=json.loads((ROOT/'content/apps.json').read_text(encoding='utf-8'))
ROUTES=json.loads((ROOT/'content/route-manifest.json').read_text())

def file_for(path):
    dest=ROOT/path.lstrip('/')
    if path.endswith('/'): return dest/'index.html'
    return dest if dest.suffix else dest.with_suffix('.html')

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.tags=[];self.h1=0;self.ids=set();self.script=None;self.json=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        data=dict(attrs);self.tags.append((tag,data))
        if tag=='h1':self.h1+=1
        if 'id' in data:
            assert data['id'] not in self.ids, 'Duplicate id'
            self.ids.add(data['id'])
        if tag=='script' and data.get('type')=='application/ld+json':self.script=''
    def handle_data(self,data):
        if self.script is not None:self.script+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.script is not None:
            self.json.append(json.loads(self.script));self.script=None

checks=0
for route in ROUTES:
    path=file_for(route);assert path.exists(),route
    text=path.read_text(encoding='utf-8');p=Page(text)
    assert p.h1==1,(route,'h1',p.h1)
    assert any(t=='main' and a.get('id')=='main' for t,a in p.tags),route
    assert any(t=='meta' and a.get('name')=='description' and a.get('content') for t,a in p.tags),route
    assert any(t=='link' and a.get('rel')=='canonical' and a.get('href')==BASE+route for t,a in p.tags),route
    for tag,a in p.tags:
        for attr in ('href','src'):
            if not a.get(attr):continue
            url=urlsplit(urljoin(BASE+route,a[attr]))
            if url.netloc not in ('www.rapheldorsoftware.com','rapheldorsoftware.com'):continue
            target=file_for(unquote(url.path))
            assert target.exists(),(route,a[attr])
            if url.fragment and attr=='href':
                ids=p.ids if target==path else Page(target.read_text(encoding='utf-8')).ids
                assert unquote(url.fragment) in ids,(route,'anchor',a[attr])
            checks+=1
    for tag,a in p.tags:
        if tag=='img' and a.get('src'):assert 'alt' in a and a.get('width') and a.get('height'),(route,'image attributes')

expected={'booktou':25,'speaktou':17,'notero':14,'lessonta':19,'doitly':8,'dictiony':2,'beanjup':8,'wordballoonpop':2,'streaktou':14}
assert set(HOME)==set().union(*(set(a['locales']) for a in APPS))
for lang,copy in HOME.items():
    route='/' if lang=='en' else '/'+lang+'/'
    text=file_for(route).read_text(encoding='utf-8');p=Page(text)
    assert 'about-section' not in text and '#about' not in text
    assert p.json[0]['@type']=='CollectionPage'
    html=next(a for t,a in p.tags if t=='html')
    assert html['lang']==lang and html['dir']==('rtl' if lang=='ar' else 'ltr')
    assert {a.get('hreflang') for t,a in p.tags if t=='link' and a.get('rel')=='alternate'}==set(HOME)|{'x-default'}
    assert all(copy.values())
for app in APPS:
    assert len(app['locales'])==expected[app['id']]
    for kind in ('privacy','terms'):
        assert (ROOT/'assets'/kind/app['id']/(kind+'-en.txt')).exists(),(app['id'],kind)
    for lang,copy in app['locales'].items():
        assert lang in UI and lang in NAMES
        assert set(UI[lang])==set(UI['en'])
        assert all(UI[lang].values())
        assert copy['title'] and copy['summary'] and len(copy['features'])>=2
        assert not any(c in json.dumps(copy,ensure_ascii=False) for c in ('—','–'))
        route='/'+app['id']+'/'+('' if lang=='en' else lang+'/')
        p=Page(file_for(route).read_text(encoding='utf-8'))
        html=next(a for t,a in p.tags if t=='html')
        assert html['lang']==lang and html['dir']==('rtl' if lang=='ar' else 'ltr')
        alternatives={a.get('hreflang'):a.get('href') for t,a in p.tags if t=='link' and a.get('rel')=='alternate'}
        assert set(alternatives)==set(app['locales'])|{'x-default'}
        assert p.json[0]['name']==app['name']

def lum(colour):
    rgb=[int(colour[i:i+2],16)/255 for i in (1,3,5)]
    rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return sum(v*w for v,w in zip(rgb,(.2126,.7152,.0722)))
def contrast(a,b):
    hi,lo=sorted((lum(a),lum(b)),reverse=True);return (hi+.05)/(lo+.05)
ratios={a['id']:round(contrast(a['accent'],'#ffffff'),2) for a in APPS}
ratios['brand']=round(contrast('#69418e','#ffffff'),2)
ratios['body']=round(contrast('#62616a','#faf9f6'),2)
assert min(ratios.values())>=4.5,ratios
print(f'PASS: {len(ROUTES)} routes, 109 app locales, {checks} local links/assets, 18 policy files, metadata and RTL.')
print('Text/button contrast:',ratios)
