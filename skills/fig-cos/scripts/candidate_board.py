"""Render a visual candidate board instead of selecting the first name match."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
import cairosvg
import icon_library
import science_catalogs

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query');parser.add_argument('--per-provider',type=int,default=3)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    candidates=[];errors=[]
    for entry in icon_library.search(args.query,args.per_provider):
        try:
            candidate=icon_library.fetch(path=entry['path'])
            candidate['source_url']=candidate['url'];candidates.append(candidate)
        except Exception as exc:errors.append(dict(provider='Bioicons',name=entry['name'],error=str(exc)))
    for provider in ['reactome','scidraw']:
        try:
            for entry in science_catalogs.search(provider,args.query,args.per_provider):
                try:candidates.append(science_catalogs.fetch(entry,out/'source-assets'))
                except Exception as exc:errors.append(dict(provider=provider,name=entry['name'],error=str(exc)))
        except Exception as exc:errors.append(dict(provider=provider,error=str(exc)))
    if not candidates:raise ValueError('No verified vector candidates. Refine subtype terms or inspect the NIH catalog directly.')
    sheet=Image.new('RGB',(900,260*((len(candidates)+2)//3)),'#f3f5f7');draw=ImageDraw.Draw(sheet)
    rendered=[]
    for i,entry in enumerate(candidates):
        x=(i%3)*300;y=(i//3)*260
        try:
            preview=out/f'candidate-{i+1}.png'
            cairosvg.svg2png(url=entry['file'],write_to=str(preview),output_width=600)
            image=Image.open(preview).convert('RGBA');image.thumbnail((276,180))
            sheet.paste(image,(x+(300-image.width)//2,y+8),image)
            rendered.append(dict(entry,board_number=i+1,preview=str(preview)))
        except Exception as exc:errors.append(dict(provider=entry['provider'],name=entry['name'],error=str(exc)))
        draw.text((x+10,y+194),f'{i+1}. {entry["name"][:37]}',fill='#172e3e')
        draw.text((x+10,y+215),entry['provider']+' | '+entry['license'],fill='#506675')
        draw.text((x+10,y+236),entry['author'][:42],fill='#506675')
    sheet.save(out/'candidates.png')
    (out/'candidates.json').write_text(json.dumps(dict(query=args.query,candidates=rendered,rejected=errors,
        selection_required='Inspect scientific subtype, visual representation, orientation, composition, style and license. Search rank is not an acceptance score.'),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(board=str(out/'candidates.png'),verified_candidates=len(rendered),rejected=len(errors)),indent=2))

if __name__=='__main__':main()
