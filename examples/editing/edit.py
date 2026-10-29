from pathlib import Path
import argparse,xml.etree.ElementTree as E
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():p.error('Choose a new output file')
E.register_namespace('','http://www.w3.org/2000/svg')
root=E.parse(Path(__file__).with_name('before.svg')).getroot()
next(n for n in root.iter() if n.get('id')=='cell-heading-line-0').text='Study group A'
colors={'#edb1b0':'#f0c374','#d77f83':'#c69340','#bd4857':'#df826e','#156f8d':'#278b90'}
for node in root.iter():
    for name in ('fill','stroke'):
        if node.get(name,'').lower() in colors:node.set(name,colors[node.get(name).lower()])
cells=next(n for n in root.iter() if n.get('id')=='cells')
cells.set('transform','translate(22 -10) '+cells.get('transform',''))
a.output.parent.mkdir(parents=True,exist_ok=True)
E.ElementTree(root).write(a.output,encoding='utf-8',xml_declaration=True)
