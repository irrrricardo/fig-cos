"""Place normalized SVG library components in an editable scene."""
import copy
import re
import xml.etree.ElementTree as ET
from pathlib import Path
NS='http://www.w3.org/2000/svg'


def place_component(parent,file,*,key,x,y,width,height,rotation=0,source_url=None):
    """Place vector shapes/live text and supported local gradient definitions."""
    if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]*',key):raise ValueError('XML-friendly component key required')
    if any(node.get('id')==key for node in parent.iter()):raise ValueError('Duplicate component key: '+key)
    root=ET.parse(Path(file)).getroot()
    allowed={'svg','g','path','rect','ellipse','circle','line','polyline','polygon','text','defs','linearGradient','stop'}
    gradient_ids={n.get('id') for n in root.iter() if n.tag.rsplit('}',1)[-1]=='linearGradient'}
    for node in root.iter():
        tag=node.tag.rsplit('}',1)[-1]
        if tag not in allowed:raise ValueError('Normalize or rebuild unsupported component tag: '+tag)
        for name,value in node.attrib.items():
            if name.lower().startswith('on') or name.rsplit('}',1)[-1]=='href':raise ValueError('Component must contain local vector geometry')
            if 'url(' in value:
                match=re.fullmatch(r'url\(\s*#([^\s)]+)\s*\)',value)
                if name!='fill' or not match or match[1] not in gradient_ids:raise ValueError('Only supported local fill gradients may be referenced')
    vx,vy,vw,vh=map(float,root.get('viewBox','').replace(',',' ').split())
    if min(vw,vh,width,height)<=0:raise ValueError('Positive component dimensions required')
    if rotation%90:raise ValueError('Use orthogonal rotation or prepare a rotated SVG')
    scale=min(width/vh,height/vw) if rotation%180 else min(width/vw,height/vh)
    group=ET.SubElement(parent,'{'+NS+'}g',{'id':key,'data-component-key':key,
        'transform':f'translate({x+width/2} {y+height/2}) rotate({rotation}) scale({scale}) translate({-vx-vw/2} {-vy-vh/2})'})
    if source_url:group.set('data-source',source_url)
    inherited=ET.SubElement(group,'{'+NS+'}g',{'id':key+'-root-style',**{name:value for name,value in root.attrib.items()
        if name in {'fill','fill-rule','fill-opacity','stroke','stroke-width','stroke-opacity','stroke-linejoin','stroke-linecap','opacity','transform','font-family','font-size','font-weight','font-style','text-anchor'}}})
    children=[copy.deepcopy(child) for child in root];id_map={}
    for i,child in enumerate(children):
        for j,node in enumerate(child.iter()):
            new_id=f'{key}-part-{i}-{j}'
            if node.get('id'):id_map[node.get('id')]=new_id
            node.set('id',new_id)
            for name in ('data-icon-key','data-component-key'):
                if node.get(name):node.set(name,key+'-'+node.get(name))
    for child in children:
        for node in child.iter():
            for name,value in list(node.attrib.items()):
                if 'url(' in value:
                    node.set(name,re.sub(r'url\(\s*#([^\s)]+)\s*\)',lambda m:'url(#'+id_map[m[1]]+')',value))
        inherited.append(child)
    if 'url(' in inherited.get('fill',''):
        inherited.set('fill',re.sub(r'url\(\s*#([^\s)]+)\s*\)',lambda m:'url(#'+id_map[m[1]]+')',inherited.get('fill')))
    return group

def place_icon(parent, file, *, key, x, y, width, height=None, rotation=0, source_url=None):
    """Preserve aspect ratio, prefix IDs and retain the semantic icon group."""
    if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]*',key):
        raise ValueError('Use a unique XML-friendly icon instance key')
    if any(element.get('id')==key for element in parent.iter()):
        raise ValueError('Duplicate icon instance key')
    root=ET.parse(Path(file)).getroot()
    vx,vy,vw,vh=map(float,root.get('viewBox').replace(',',' ').split())
    height=height if height is not None else width
    if vw<=0 or vh<=0 or width<=0 or height<=0:
        raise ValueError('Positive icon dimensions required')
    if rotation%90:
        raise ValueError('Use orthogonal rotation or prepare a rotated SVG explicitly')
    scale=min(width/vh,height/vw) if rotation%180 else min(width/vw,height/vh)
    group=ET.SubElement(parent,'{'+NS+'}g',{'id':key,'data-icon-key':key,
        'transform':f'translate({x+width/2} {y+height/2}) rotate({rotation}) scale({scale}) translate({-vx-vw/2} {-vy-vh/2})'})
    if source_url: group.set('data-source',source_url)
    for i,child in enumerate(root):
        if child.tag.rsplit('}',1)[-1] not in {'path','g'}:
            raise ValueError('Run normalize_icon.py first; only paths/groups may be placed')
        child=copy.deepcopy(child)
        for j,element in enumerate(child.iter()): element.set('id',f'{key}-path-{i}-{j}')
        group.append(child)
    return group
