"""Search Bioicons metadata and fetch verified SVG assets with attribution."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(os.environ.get('FIG_COS_CACHE',str(Path(os.environ.get('XDG_CACHE_HOME',str(Path.home()/'.cache')))/'fig-cos'))) / 'icon-library'
INDEX = CACHE / 'bioicons-index.json'
BUNDLED_INDEX = ROOT / 'assets' / 'icon-library' / 'bioicons-index.json'
ALIASES = {'细胞':'cell','细菌':'bacteria','微生物':'bacteria','神经元':'neuron',
    '骨骼':'skeleton','药物':'pill','蛋白':'protein','抗体':'antibody','移液器':'pipette',
    '双螺旋':'dna','显微镜':'microscope','科学家':'scientist','神经网络':'neural network'}


def get(url, limit=8_000_000):
    req=urllib.request.Request(url,headers={'User-Agent':'fig_cos-icons/1.0'})
    with urllib.request.urlopen(req,timeout=35) as response:
        data=response.read(limit+1)
    if len(data)>limit:
        raise ValueError('Asset exceeds download size limit')
    return data


def refresh():
    result=json.loads(get('https://api.github.com/repos/duerrsimon/bioicons/git/trees/main?recursive=1'))
    if result.get('truncated'):
        raise ValueError('Incomplete catalog response')
    entries=[]
    for item in result['tree']:
        path=item['path']
        parts=path.split('/')
        if path.startswith('static/icons/') and path.endswith('.svg') and len(parts)>=6:
            entries.append(dict(path=path,license=parts[2],category=parts[3],
                author=parts[4],name=Path(path).stem,sha=item['sha'],size=item.get('size')))
    if not entries:
        raise ValueError('Catalog contained no SVG icons')
    CACHE.mkdir(parents=True,exist_ok=True)
    INDEX.write_text(json.dumps(dict(repository='duerrsimon/bioicons',revision=result['sha'],
        entries=entries),ensure_ascii=False,indent=2),encoding='utf-8')
    return entries


def catalog():
    index=INDEX if INDEX.exists() else BUNDLED_INDEX
    return json.loads(index.read_text(encoding='utf-8'))['entries'] if index.exists() else refresh()


def search(query, limit=12, license=None):
    words=re.findall(r'[a-z0-9]+',ALIASES.get(query,query).lower())
    if not words:
        raise ValueError('Use an English term or a supported Chinese synonym')
    hits=[]
    for entry in catalog():
        if license and entry['license']!=license:
            continue
        name=entry['name'].lower().replace('_',' ').replace('-',' ')
        text=(name+' '+entry['category']).lower()
        score=sum(4 if word in name else 1 for word in words if word in text)
        if all(word in text for word in words):
            score+=10
        if score:
            hits.append((score,entry))
    return [entry for _,entry in sorted(hits,key=lambda hit:(-hit[0],hit[1].get('size') or 0))[:limit]]


def validate_svg(data):
    root=ET.fromstring(data)
    if root.tag.rsplit('}',1)[-1]!='svg':
        raise ValueError('Not an SVG asset')
    for node in root.iter():
        if node.tag.rsplit('}',1)[-1] in {'image','script','foreignObject'}:
            raise ValueError('Asset contains raster or executable content')
        for key,value in node.attrib.items():
            if node.tag.rsplit('}',1)[-1]=='use' and key.rsplit('}',1)[-1]=='href' and not value.startswith('#'):
                raise ValueError('Asset contains an external resource')
            if re.search(r'url\(\s*[\x27\x22]?(?:https?:|file:)',value,re.I):
                raise ValueError('Asset contains external paint content')
        if node.tag.rsplit('}',1)[-1]=='style' and re.search(r'@import|url\(\s*[\x27\x22]?(?:https?:|file:)',node.text or '',re.I):
            raise ValueError('Asset contains external CSS content')
    return root


def fetch(path=None,lucide=None):
    if lucide:
        if not re.fullmatch(r'[a-z0-9-]+',lucide):
            raise ValueError('Invalid Lucide icon name')
        url=f'https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{lucide}.svg'
        entry=dict(provider='Lucide',name=lucide,author='Lucide contributors; Feather where applicable',
                   license='ISC; derived Feather icons MIT',license_url='https://lucide.dev/license')
        stem='lucide-'+lucide
    else:
        entry=next((dict(item) for item in catalog() if item['path']==path),None)
        if entry is None:
            raise ValueError('Select an exact path returned by search')
        data=json.loads((INDEX if INDEX.exists() else BUNDLED_INDEX).read_text(encoding='utf-8'))
        url='https://raw.githubusercontent.com/duerrsimon/bioicons/'+data['revision']+'/'+urllib.parse.quote(path,safe='/')
        stem='bioicons-'+hashlib.sha256(path.encode()).hexdigest()[:10]+'-'+entry['name']
        entry['provider']='Bioicons'
        entry['license_url']={
            'cc-0':'https://creativecommons.org/publicdomain/zero/1.0/',
            'cc-by-3.0':'https://creativecommons.org/licenses/by/3.0/',
            'cc-by-4.0':'https://creativecommons.org/licenses/by/4.0/',
            'cc-by-sa-3.0':'https://creativecommons.org/licenses/by-sa/3.0/',
            'cc-by-sa-4.0':'https://creativecommons.org/licenses/by-sa/4.0/',
        }.get(entry['license'],'https://github.com/duerrsimon/bioicons/tree/main/static/icons/'+entry['license'])
    CACHE.mkdir(parents=True,exist_ok=True)
    target=CACHE/(stem+'.svg')
    if target.exists():
        payload=target.read_bytes()
    else:
        payload=get(url,3_000_000)
    validate_svg(payload)
    if not lucide:
        git_sha=hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
        if git_sha!=entry['sha']:
            raise ValueError('Downloaded SVG differs from indexed Git blob')
    target.write_bytes(payload)
    entry.update(url=url,file=str(target),sha256=hashlib.sha256(payload).hexdigest(),
                 modified=False)
    target.with_suffix('.attribution.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2),encoding='utf-8')
    return entry


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('refresh')
    finder=sub.add_parser('search'); finder.add_argument('query'); finder.add_argument('--limit',type=int,default=12); finder.add_argument('--license')
    fetcher=sub.add_parser('fetch'); choice=fetcher.add_mutually_exclusive_group(required=True); choice.add_argument('--path'); choice.add_argument('--lucide')
    args=parser.parse_args()
    if args.command=='refresh': result={'indexed':len(refresh()),'index':str(INDEX)}
    elif args.command=='search': result=search(args.query,args.limit,args.license)
    else: result=fetch(getattr(args,'path',None),getattr(args,'lucide',None))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
