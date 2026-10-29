"""Recover a reference icon from a PDF region; trace only embedded rasters."""
from __future__ import annotations
import argparse,base64,copy,json,math,re
from pathlib import Path
import xml.etree.ElementTree as E
import pymupdf
import vtracer
import pathops
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen
NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)

def color(rgb):
    return 'none' if rgb is None else '#'+''.join(f'{max(0,min(255,round(v*255))):02x}' for v in rgb)

def path_data(record):
    chunks=[];last=None
    def start(point):
        nonlocal last
        p=(point.x,point.y)
        if last is None or math.dist(p,last)>1e-5:chunks.append(f'M{p[0]} {p[1]}')
        last=p
    for item in record['items']:
        if item[0]=='l':
            start(item[1]);p=item[2];chunks.append(f'L{p.x} {p.y}');last=(p.x,p.y)
        elif item[0]=='c':
            start(item[1]);a,b,c=item[2:];chunks.append(f'C{a.x} {a.y} {b.x} {b.y} {c.x} {c.y}');last=(c.x,c.y)
        elif item[0]=='re':
            r=item[1]
            if item[2]==1:chunks.append(f'M{r.x0} {r.y0}H{r.x1}V{r.y1}H{r.x0}Z')
            else:chunks.append(f'M{r.x0} {r.y0}V{r.y1}H{r.x1}V{r.y0}Z')
            last=None
        elif item[0]=='qu':
            q=item[1];chunks.append(f'M{q.ul.x} {q.ul.y}L{q.ur.x} {q.ur.y}L{q.lr.x} {q.lr.y}L{q.ll.x} {q.ll.y}Z');last=None
        else:raise ValueError('Unsupported PDF path item '+item[0])
    if record.get('closePath'):chunks.append('Z')
    return ' '.join(chunks)

def recover(pdf,page_number,box,output,exclude_xrefs=(),exclude_seqnos=(),composite=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('Choose a fresh output directory')
    doc=pymupdf.open(pdf);page=doc[page_number-1];clip=pymupdf.Rect(box)
    root=E.Element('{'+NS+'}svg',dict(viewBox=f'0 0 {clip.width} {clip.height}',width=str(clip.width),height=str(clip.height)))
    scene=E.SubElement(root,'{'+NS+'}g',dict(transform=f'translate({-clip.x0} {-clip.y0})'))
    layers=[];source_layers=[];rasters=0;vectors=0;seq=page.get_bboxlog()
    image_seq={i:item[1] for i,item in enumerate(seq) if item[0]=='fill-image'}
    images=page.get_image_info(xrefs=True)
    used_seq=set()
    for info in images:
        rect=pymupdf.Rect(info['bbox']);xref=info['xref']
        if xref in exclude_xrefs or not clip.contains(rect):continue
        choices=[(max(abs(a-b) for a,b in zip(info['bbox'],bounds)),i)
                 for i,bounds in image_seq.items() if i not in used_seq]
        error,order=min(choices)
        if error>.01:raise ValueError('PDF image paint order cannot be reconciled')
        used_seq.add(order)
        if not xref:raise ValueError('Inline PDF image requires a separately verified rendering')
        image=output/f'original-{xref}.png';traced=output/f'traced-{xref}.svg'
        if not image.exists():
            pix=pymupdf.Pixmap(doc,xref)
            smask=next((row[1] for row in page.get_images(full=True) if row[0]==xref),0)
            if smask:pix=pymupdf.Pixmap(pix,pymupdf.Pixmap(doc,smask))
            pix.save(image)
            vtracer.convert_image_to_svg_py(str(image),str(traced),colormode='color',hierarchical='stacked',
                mode='spline',filter_speckle=1,color_precision=8,layer_difference=4,
                corner_threshold=60,length_threshold=2.0,max_iterations=10,path_precision=3)
        a,b,c,d,e,f=info['transform'];w,h=info['width'],info['height']
        group=E.Element('{'+NS+'}g',dict(transform=f'matrix({a/w} {b/w} {c/h} {d/h} {e} {f})'))
        for child in E.parse(traced).getroot():group.append(copy.deepcopy(child))
        layers.append((order,group));rasters+=1
        original=E.Element('{'+NS+'}g',dict(transform=group.get('transform')))
        E.SubElement(original,'{'+NS+'}image',dict(width=str(w),height=str(h),
            href='data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode()))
        source_layers.append((order,original))
    for record in page.get_drawings():
        rect=record['rect']
        if record['seqno'] in exclude_seqnos or not clip.contains(rect):continue
        d=path_data(record)
        fill=record.get('fill');stroke=record.get('color')
        if record.get('even_odd') and fill is not None:
            sk=pathops.Path();sk.fillType=pathops.FillType.EVEN_ODD;parse_path(d,sk.getPen());sk.simplify()
            pen=SVGPathPen(None);sk.draw(pen);d=pen.getCommands()
        attrs={'d':d,'fill':color(fill),'stroke':color(stroke),'stroke-width':str(record.get('width') or 0),
            'fill-opacity':str(1 if record.get('fill_opacity') is None else record['fill_opacity']),
            'stroke-opacity':str(1 if record.get('stroke_opacity') is None else record['stroke_opacity'])}
        # join and cap are retained from the PDF path representation.
        attrs['stroke-linejoin']={0:'miter',1:'round',2:'bevel'}.get(round(record.get('lineJoin') or 0),'miter')
        caps=record.get('lineCap') or (0,0,0);attrs['stroke-linecap']={0:'butt',1:'round',2:'square'}.get(max(caps),'butt')
        element=E.Element('{'+NS+'}path',attrs)
        layers.append((record['seqno'],element));source_layers.append((record['seqno'],copy.deepcopy(element)));vectors+=1
    for _,layer in sorted(layers,key=lambda item:item[0]):scene.append(layer)
    background_removed=False
    if composite:
        import cairosvg
        original_root=E.Element('{'+NS+'}svg',dict(viewBox=f'{clip.x0} {clip.y0} {clip.width} {clip.height}',width=str(clip.width),height=str(clip.height)))
        for _,layer in sorted(source_layers,key=lambda item:item[0]):original_root.append(layer)
        png=output/'composited-source.png';svg=output/'composited-trace.svg'
        cairosvg.svg2png(bytestring=E.tostring(original_root),write_to=str(png),output_width=768,background_color='white')
        vtracer.convert_image_to_svg_py(str(png),str(svg),colormode='color',hierarchical='stacked',
            mode='spline',filter_speckle=1,color_precision=8,layer_difference=4,length_threshold=2.0,path_precision=3)
        from PIL import Image
        width,height=Image.open(png).size
        root=E.Element('{'+NS+'}svg',dict(viewBox=f'0 0 {width} {height}',width=str(width),height=str(height)))
        for child in E.parse(svg).getroot():root.append(copy.deepcopy(child))
        # VTracer adds a full-canvas white plate after compositing. Leaving it
        # in an icon would cover nearby text when its visible bounds are fitted.
        if len(root):
            first=root[0];fill=first.get('fill','')
            if re.fullmatch(r'#[0-9a-fA-F]{6}',fill) and min(int(fill[i:i+2],16) for i in (1,3,5))>=245:
                from fontTools.pens.boundsPen import BoundsPen
                pen=BoundsPen(None);parse_path(first.get('d',''),pen)
                if pen.bounds and pen.bounds[0]<=0 and pen.bounds[1]<=0 and pen.bounds[2]>=width and pen.bounds[3]>=height:
                    root.remove(first);background_removed=True
    else:
        # Keep short labels that are integral to an icon, e.g. phosphate P
        # and AI inside a network diagram. Surrounding panel text is excluded.
        for block in page.get_text('dict')['blocks']:
            if block['type']!=0:continue
            for line in block['lines']:
                for span in line['spans']:
                    content=span['text'].strip()
                    if content not in {'P','AI'} or not clip.contains(pymupdf.Rect(span['bbox'])):continue
                    x,y=span['origin'];text=E.SubElement(scene,'{'+NS+'}text',{
                        'x':str(x),'y':str(y),'font-family':'Arial','font-size':str(span['size']),
                        'fill':f'#{span["color"]:06x}'})
                    text.text=content
    for i,element in enumerate(root.iter()):element.set('id',f'pdf-asset-{i}')
    target=output/'component.svg';E.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
    page.get_pixmap(matrix=pymupdf.Matrix(8,8),clip=clip,alpha=False).save(output/'reference-region.png')
    result=dict(pdf=str(Path(pdf).resolve()),page=page_number,box=list(box),component=str(target.resolve()),
        original_vector_paths=vectors,traced_image_occurrences=rasters,excluded_xrefs=list(exclude_xrefs),
        excluded_vector_seqnos=list(exclude_seqnos),alpha_composited_before_tracing=composite,
        composite_white_background_removed=background_removed,
        limitation='Embedded raster contours are approximated, not original semantic source paths; only integral P/AI labels are retained as text.')
    (output/'provenance.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',required=True,type=Path);parser.add_argument('--page',required=True,type=int)
    parser.add_argument('--box',required=True,type=float,nargs=4);parser.add_argument('--output-dir',required=True,type=Path)
    parser.add_argument('--exclude-xref',type=int,action='append',default=[])
    parser.add_argument('--exclude-vector-seqno',type=int,action='append',default=[])
    parser.add_argument('--composite-raster-layer',action='store_true')
    args=parser.parse_args();print(json.dumps(recover(args.pdf,args.page,args.box,args.output_dir,args.exclude_xref,args.exclude_vector_seqno,args.composite_raster_layer),indent=2))
