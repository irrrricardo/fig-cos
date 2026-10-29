"""Read public Reactome/SciDraw catalogs and NIH BioArt entry previews."""
from __future__ import annotations
import argparse,hashlib,html,json,re,urllib.parse,urllib.request
from pathlib import Path
from icon_library import get,validate_svg,CACHE as ICON_CACHE
ROOT=Path(__file__).resolve().parents[1]
CACHE=ICON_CACHE.parent/'extended-catalogs'

def search(provider,query,limit=12):
    if provider=='reactome':
        url='https://reactome.org/ContentService/search/query?'+urllib.parse.urlencode(dict(query=query,types='Icon',cluster='true',rows=limit))
        response=json.loads(get(url));entries=[entry for group in response.get('results',[]) for entry in group.get('entries',[])]
        return [dict(provider='reactome',id=entry['stId'],name=entry.get('iconName') or re.sub('<[^>]+>','',entry['name']),
            author='Reactome / '+entry.get('iconDesignerName','CSHL, OICR and EBI'),
            description=re.sub('<[^>]+>','',entry.get('summation','')),categories=entry.get('iconCategories',[]),
            source_url='https://reactome.org/content/detail/'+entry['stId'],
            download_url='https://reactome.org/icon/'+entry['stId']+'.svg',
            preview_url='https://reactome.org/icon/'+entry['stId']+'.png',
            license='CC-BY-4.0',license_url='https://creativecommons.org/licenses/by/4.0/') for entry in entries[:limit]]
    if provider=='scidraw':
        url='https://scidraw.io/api/v1/drawings/?'+urllib.parse.urlencode(dict(search=query,is_vector='true'))
        data=json.loads(get(url))
        return [dict(provider='scidraw',id=entry['slug'],name=entry['name'],
            author=entry.get('primary_author',{}).get('full_name','Unknown'),description=entry.get('doi') or '',
            source_url='https://scidraw.io/drawing/'+entry['slug'],
            download_url=entry['image_url'].replace('http://scidraw.io/','https://scidraw.io/'),
            license=entry['license'],license_url={'cc-by':'https://creativecommons.org/licenses/by/4.0/','cc0':'https://creativecommons.org/publicdomain/zero/1.0/','cc-0':'https://creativecommons.org/publicdomain/zero/1.0/'}.get(entry['license'],'https://scidraw.io/drawing/'+entry['slug']))
            for entry in data.get('results',[])[:limit]]
    raise ValueError('Provider must be reactome or scidraw')

def nih_entry(identifier):
    if not str(identifier).isdigit():raise ValueError('NIH numeric entry ID required')
    url='https://bioart.niaid.nih.gov/bioart/'+str(identifier)
    page=get(url).decode('utf-8')
    pieces=[]
    for match in re.findall(r'self\.__next_f\.push\((\[1,.*?\])\)',page):
        record=json.loads(match)
        if len(record)==2 and isinstance(record[1],str):pieces.append(record[1])
    data='\n'.join(pieces);marker='"carouselItems":';start=data.find(marker)
    if start<0:raise ValueError('Entry preview data unavailable; use the official entry page')
    files,_=json.JSONDecoder().raw_decode(data[start+len(marker):])
    return dict(provider='nih-bioart',id=str(identifier),source_url=url,
        name=files[0].get('caption') if files else 'NIH BioArt entry',
        preview_files=[dict(name=item['name'],format=item['fileFormat'],url=item['s3Location'],caption=item.get('caption')) for item in files],
        license_note='Check this entry license and credit on the source page; preview PNGs are not proof of vector download availability.',
        terms_url='https://bioart.niaid.nih.gov/terms',
        vector_files_exposed_in_preview=[item for item in files if item['fileFormat'].lower()=='svg'])

def fetch(entry,folder):
    allowed={'reactome':'reactome.org','scidraw':'scidraw.io'}
    url=entry['download_url'];parsed=urllib.parse.urlparse(url)
    if entry['provider'] not in allowed or parsed.scheme!='https' or parsed.hostname!=allowed[entry['provider']]:
        raise ValueError('Use a record returned by the supported public catalog')
    payload=get(url,8_000_000);validate_svg(payload)
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    name=entry['provider']+'-'+re.sub('[^A-Za-z0-9_-]','-',entry['id'])
    path=folder/(name+'.svg');path.write_bytes(payload)
    result=dict(entry,file=str(path.resolve()),sha256=hashlib.sha256(payload).hexdigest(),modified=False)
    path.with_suffix('.attribution.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    finder=sub.add_parser('search');finder.add_argument('--provider',choices=['reactome','scidraw'],required=True);finder.add_argument('query');finder.add_argument('--limit',type=int,default=12);finder.add_argument('--output',type=Path)
    nih=sub.add_parser('nih-entry');nih.add_argument('id')
    downloader=sub.add_parser('fetch');downloader.add_argument('--results',type=Path,required=True);downloader.add_argument('--index',type=int,default=0);downloader.add_argument('--output-dir',type=Path,default=CACHE)
    args=parser.parse_args()
    if args.command=='search':
        result=search(args.provider,args.query,args.limit)
        if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    elif args.command=='nih-entry':result=nih_entry(args.id)
    else:result=fetch(json.loads(args.results.read_text(encoding='utf-8'))[args.index],args.output_dir)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
