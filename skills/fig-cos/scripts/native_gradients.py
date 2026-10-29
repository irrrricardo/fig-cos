"""Preserve supported SVG linear gradients as editable native PowerPoint fills.

Only axis-aligned objectBoundingBox gradients with explicit hex stops are
supported. Unsupported geometry is rejected, never silently flattened.
"""
from __future__ import annotations
import math,re
from pathlib import Path
import xml.etree.ElementTree as E
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls,qn
from fontTools.misc.transform import Transform
from vendor.prepare_geometry_cache import parse_transform

PAINTED={'path','rect','circle','ellipse','polygon','polyline','line'}


def number(value):
    value=str(value).strip()
    result=float(value[:-1])/100 if value.endswith('%') else float(value)
    if not math.isfinite(result):raise ValueError('Non-finite gradient value')
    return result


def parse_gradient(node):
    if node.get('gradientUnits','objectBoundingBox')!='objectBoundingBox':raise ValueError('Native gradient requires objectBoundingBox units')
    if node.get('gradientTransform') or any(k.rsplit('}',1)[-1]=='href' for k in node.attrib):raise ValueError('Resolve gradient transforms/inheritance first')
    if node.get('spreadMethod','pad')!='pad':raise ValueError('Native gradient requires pad spread')
    x1,y1,x2,y2=[number(node.get(k,default)) for k,default in [('x1','0'),('y1','0'),('x2','1'),('y2','0')]]
    if (x1,y1,x2,y2) not in [(0,0,1,0),(1,0,0,0),(0,0,0,1),(0,1,0,0)]:
        raise ValueError('Native gradients currently support full horizontal or vertical directions')
    angle={(0,0,1,0):0,(1,0,0,0):180,(0,0,0,1):90,(0,1,0,0):270}[(x1,y1,x2,y2)]
    stops=[]
    for child in node:
        if child.tag.rsplit('}',1)[-1]!='stop':raise ValueError('Unsupported gradient child')
        attrs=dict(child.attrib)
        for term in attrs.get('style','').split(';'):
            if ':' in term:
                k,v=term.split(':',1);attrs[k.strip()]=v.strip()
        color=attrs.get('stop-color','#000000')
        if re.fullmatch('#[0-9a-fA-F]{3}',color):color='#'+''.join(v*2 for v in color[1:])
        if not re.fullmatch('#[0-9a-fA-F]{6}',color):raise ValueError('Native gradients need explicit hex stop colors')
        offset=number(attrs.get('offset','0'));alpha=number(attrs.get('stop-opacity','1'))
        if not 0<=offset<=1 or not 0<=alpha<=1:raise ValueError('Gradient stop outside 0..1')
        stops.append(dict(offset=offset,color=color[1:].upper(),alpha=alpha))
    if len(stops)<2 or [v['offset'] for v in stops]!=sorted(v['offset'] for v in stops):raise ValueError('Use at least two ordered gradient stops')
    if stops[0]['offset']!=0:stops.insert(0,dict(stops[0],offset=0))
    if stops[-1]['offset']!=1:stops.append(dict(stops[-1],offset=1))
    return dict(angle=angle,stops=stops)


def prepare(source,target):
    """Build flat geometry input while retaining fill bindings by stable ID."""
    tree=E.parse(source);root=tree.getroot();gradients={};bindings={}
    for node in root.iter():
        tag=node.tag.rsplit('}',1)[-1]
        if tag=='radialGradient':raise ValueError('Radial gradients need a separately verified conversion; no silent flattening')
        if tag=='linearGradient':
            if not node.get('id'):raise ValueError('Stable gradient ID required')
            gradients[node.get('id')]=parse_gradient(node)
    if not gradients:return Path(source),bindings
    def walk(node,inherited_fill='black',hidden_definition=False,transform=Transform()):
        tag=node.tag.rsplit('}',1)[-1]
        current=transform.transform(parse_transform(node.get('transform')))
        definition=hidden_definition or tag=='defs'
        fill=node.get('fill',inherited_fill)
        if 'url(' in node.get('stroke',''):raise ValueError('Gradient strokes require vector outline reconstruction')
        if 'url(' in node.get('style',''):raise ValueError('Resolve gradient CSS to fill attributes first')
        if 'url(' in fill:
            match=re.fullmatch(r'url\(\s*#([^\s)]+)\s*\)',fill)
            if not match or match[1] not in gradients:raise ValueError('Unknown or unsupported local gradient')
            spec=gradients[match[1]]
            if tag=='text':raise ValueError('Gradient text is outside native fill support')
            if tag in PAINTED and not definition:
                if not node.get('id'):raise ValueError('Gradient-bearing shape needs a stable ID')
                angle=math.radians(spec['angle']);dx,dy=math.cos(angle),math.sin(angle)
                vx=current.xx*dx+current.yx*dy;vy=current.xy*dx+current.yy*dy
                world=(math.degrees(math.atan2(vy,vx))+360)%360
                if abs(world/90-round(world/90))>1e-7:raise ValueError('Native fill gradients require orthogonal transforms')
                bindings[node.get('id')]=dict(spec,angle=round(world/90)*90%360)
            node.set('fill','#'+spec['stops'][0]['color'])
        for child in node:walk(child,fill,definition,current)
    walk(root)
    for parent in list(root.iter()):
        for child in list(parent):
            if child.tag.rsplit('}',1)[-1]=='linearGradient':parent.remove(child)
    target=Path(target);tree.write(target,encoding='utf-8',xml_declaration=True)
    return target,bindings


def apply(slide,cache,bindings):
    atoms={a['objectName']:a for a in cache['atoms']};count=0;opacities={}
    for atom in cache['atoms']:
        for paint in atom.get('paintParts',[]):
            if paint.get('filled'):opacities.setdefault(atom['objectName'],float(paint.get('opacity',100))/100)
    for shape in slide.shapes:
        atom=atoms.get(shape.name.split('_PAINT_',1)[0])
        if not atom or atom['sourceId'] not in bindings:continue
        fill=shape._element.spPr.find(qn('a:solidFill'))
        if fill is None:continue # open-stroke paint copy has no filled face
        # A shared SVG atom may be split into a fill and a stroke paint. Use the
        # filled paint opacity rather than a stroke-only paint's opacity.
        opacity=opacities.get(atom['objectName'],1)
        gradient=bindings[atom['sourceId']]
        stops=''.join('<a:gs pos="'+str(round(s['offset']*100000))+'"><a:srgbClr val="'+s['color']+'"><a:alpha val="'+str(round(s['alpha']*opacity*100000))+'"/></a:srgbClr></a:gs>' for s in gradient['stops'])
        xml=f'<a:gradFill {nsdecls("a")} rotWithShape="1"><a:gsLst>{stops}</a:gsLst><a:lin ang="{gradient["angle"]*60000}" scaled="1"/><a:tileRect/></a:gradFill>'
        shape._element.spPr.replace(fill,parse_xml(xml));count+=1
    return count
