"""Flatten SVG transforms, clips, CSS and strokes to editable vector paths."""
from __future__ import annotations
import argparse
import json
import re
import tempfile
from pathlib import Path
from lxml import etree
from picosvg.svg import SVG
import tinycss2
import cssselect2
import pathops
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen

NS='http://www.w3.org/2000/svg'


def expand_css(tree):
    matcher=cssselect2.Matcher()
    for style in tree.xpath('.//svg:style',namespaces={'svg':NS}):
        for rule in tinycss2.parse_stylesheet(style.text or '',skip_comments=True,skip_whitespace=True):
            if rule.type!='qualified-rule':
                raise ValueError('Unsupported SVG CSS rule')
            selector=tinycss2.serialize(rule.prelude)
            values=[(item.lower_name,tinycss2.serialize(item.value).strip())
                for item in tinycss2.parse_declaration_list(rule.content,skip_comments=True,skip_whitespace=True)
                if item.type=='declaration']
            for selection in cssselect2.compile_selector_list(selector):
                matcher.add_selector(selection,values)
    for wrapped in cssselect2.ElementWrapper.from_xml_root(tree).iter_subtree():
        node=wrapped.etree_element
        styles={}
        for specificity,order,pseudo,values in matcher.match(wrapped):
            styles.update(values)
        inline=tinycss2.parse_declaration_list(node.get('style',''),skip_comments=True,skip_whitespace=True)
        styles.update({item.lower_name:tinycss2.serialize(item.value).strip() for item in inline if item.type=='declaration'})
        for key,value in styles.items():
            if not key.startswith('-'): node.set(key,value)
        node.attrib.pop('style',None);node.attrib.pop('class',None)
        for key,value in list(node.attrib.items()):
            if key in {'stroke-width','stroke-dasharray','stroke-dashoffset','font-size'}:
                node.set(key,re.sub(r'(?<=[0-9.])px\b','',value))
    for style in tree.xpath('.//svg:style',namespaces={'svg':NS}):
        style.getparent().remove(style)


def normalize(source, target, color='#326784'):
    source,target=Path(source),Path(target)
    tree=etree.fromstring(source.read_bytes(),etree.XMLParser(resolve_entities=False,no_network=True))
    expand_css(tree)
    for node in list(tree.iter()):
        if not isinstance(node.tag,str):
            continue
        tag=etree.QName(node)
        if tag.localname in {'image','script','foreignObject','text','tspan','filter','mask'}:
            raise ValueError('Icon needs unsupported content: '+tag.localname)
        if tag.namespace!=NS or tag.localname in {'metadata','title','desc'}:
            parent=node.getparent()
            if parent is not None: parent.remove(node)
            continue
        for key,value in list(node.attrib.items()):
            if key.startswith('{'):
                if etree.QName(key).namespace not in {NS,'http://www.w3.org/1999/xlink'}:
                    del node.attrib[key]
            elif 'currentColor' in value:
                node.set(key,value.replace('currentColor',color))
    svg=SVG.fromstring(etree.tostring(tree).decode()).topicosvg(inplace=False)
    root=etree.fromstring(svg.tostring().encode())
    gradients=root.xpath('.//svg:linearGradient|.//svg:radialGradient',namespaces={'svg':NS})
    if gradients:
        raise ValueError('Gradient icon: choose a flat vector alternative; gradients are not silently flattened.')
    for node in list(root):
        if etree.QName(node).localname=='defs': root.remove(node)
    paths=0
    for node in root.iter():
        if not isinstance(node.tag,str) or etree.QName(node).localname!='path': continue
        if node.get('fill-rule')=='evenodd':
            path=pathops.Path();path.fillType=pathops.FillType.EVEN_ODD
            parse_path(node.get('d'),path.getPen());path.simplify()
            pen=SVGPathPen(None);path.draw(pen);node.set('d',pen.getCommands())
            node.set('fill-rule','nonzero')
        node.set('id','icon-path-'+str(paths));paths+=1
    if not paths: raise ValueError('No vector paths after normalization')
    # Many libraries retain large transparent margins. Fit paths rather than
    # the original editor page so icons can be placed by their visible bounds.
    from fontTools.pens.boundsPen import BoundsPen
    boxes=[]
    for node in root.iter():
        if isinstance(node.tag,str) and etree.QName(node).localname=='path':
            pen=BoundsPen(None);parse_path(node.get('d'),pen)
            if pen.bounds: boxes.append(pen.bounds)
    if boxes:
        x0=min(b[0] for b in boxes);y0=min(b[1] for b in boxes)
        x1=max(b[2] for b in boxes);y1=max(b[3] for b in boxes)
        pad=max(x1-x0,y1-y0)*.015
        root.set('viewBox',f'{x0-pad} {y0-pad} {x1-x0+2*pad} {y1-y0+2*pad}')
        root.attrib.pop('width',None);root.attrib.pop('height',None)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(etree.tostring(root,encoding='utf-8',xml_declaration=True))
    return dict(source=str(source),output=str(target),paths=paths,modified='CSS, transforms, clips and strokes normalized to paths; evenodd winding normalized when present')


def trace_fallback(source,target):
    """Explicit approximation for a verified library icon with gradients."""
    import cairosvg
    import vtracer
    from icon_library import validate_svg
    validate_svg(Path(source).read_bytes())
    with tempfile.TemporaryDirectory(prefix='fig_cos-icon-trace-') as temp:
        png=Path(temp)/'render.png';svg=Path(temp)/'traced.svg'
        cairosvg.svg2png(url=str(source),write_to=str(png),output_width=512)
        vtracer.convert_image_to_svg_py(str(png),str(svg),colormode='color',
            hierarchical='stacked',mode='spline',filter_speckle=2,color_precision=6,
            layer_difference=12,path_precision=3)
        result=normalize(svg,target)
    result['source']=str(source)
    result['modified']='Rendered at 512px then locally traced: approximate gradient and shape contours, not lossless source vectors'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--color',default='#326784')
    parser.add_argument('--trace-fallback',action='store_true',help='Explicit approximate tracing for gradient/unsupported verified icons')
    args=parser.parse_args()
    try:
        result=normalize(args.input,args.output,args.color)
    except ValueError:
        if not args.trace_fallback: raise
        result=trace_fallback(args.input,args.output)
    print(json.dumps(result,ensure_ascii=False,indent=2))
