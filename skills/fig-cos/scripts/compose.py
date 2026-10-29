"""Assemble reusable vector, traced-raster and procedural components from JSON."""
from __future__ import annotations
import argparse,copy,hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
import xml.etree.ElementTree as E
from normalize_icon import normalize,trace_fallback
from svg_assets import place_component
from trace_asset import trace_asset
from parametric import draw_component

NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
SCRIPTS=Path(__file__).resolve().parent
TAGS={'rect','ellipse','circle','line','polyline','polygon','path'}
ATTRS={'x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','width','height','points','d','fill','fill-rule',
       'stroke','stroke-width','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity',
       'font-family','font-size','font-weight','font-style','text-anchor','transform'}


def assemble(spec_path,output,export_pptx=False,render_ppt=False):
    spec_path=Path(spec_path).resolve(strict=True);output=Path(output).resolve()
    spec=json.loads(spec_path.read_text(encoding='utf-8-sig'))
    if spec.get('schema_version')!=1:raise ValueError('Expected scene schema_version 1')
    if spec.get('mode') not in {'reconstruct','design','ai-assisted'}:raise ValueError('Choose reconstruct, design, or ai-assisted mode')
    canvas=spec['canvas'];w=float(canvas['width']);h=float(canvas['height'])
    if min(w,h)<=0:raise ValueError('Positive canvas dimensions required')
    if output.exists():raise ValueError('Choose a fresh job directory')
    output.mkdir(parents=True)
    scene=E.Element('{'+NS+'}svg',{'id':'fig-scene','viewBox':f'0 0 {w} {h}','width':str(w),'height':str(h)})
    if canvas.get('background'):
        E.SubElement(scene,'{'+NS+'}rect',{'id':'canvas-background','x':'0','y':'0','width':str(w),'height':str(h),'fill':canvas['background']})
    records=[];keys={'fig-scene','canvas-background'};resolved=copy.deepcopy(spec)
    def attrs(values):
        unknown=set(values)-ATTRS
        if unknown:raise ValueError('Unsupported attributes: '+str(sorted(unknown)))
        if any('url(' in str(v) for v in values.values()):raise ValueError('Resolve paint servers before composition')
        return {k:str(v) for k,v in values.items()}
    def add(node,parent,resolved_node):
        key=node['id'];kind=node['kind']
        if not re.fullmatch('[a-zA-Z][a-zA-Z0-9_-]*',key) or key in keys:raise ValueError('Unique XML-friendly component ids required: '+key)
        keys.add(key)
        source=copy.deepcopy(node.get('source',{}));record=dict(id=key,kind=kind,source=source,approximation=bool(source.get('approximation',False)))
        if kind in {'svg','trace','parametric'}:
            folder=output/'components'/key;folder.mkdir(parents=True)
            if kind=='parametric':
                raw=draw_component(node['generator'],node.get('parameters',{}),folder/'source.svg')
                target=folder/'component.svg'
                from refined_components import KINDS
                if node['generator'] in KINDS:shutil.copy2(raw,target)
                else:normalize(raw,target)
                record['schematic']=True;record['generator']=node['generator']
                record['source'].update(origin_kind='parametric',schematic=True,generator=node['generator'])
                if node['generator'] in KINDS:
                    record['source'].update(representation='generic schematic design; not a reference-matched restoration',
                        scientific_identity='Schematic object representation; hidden source detail or exact molecular identity is not inferred')
            else:
                raw=(spec_path.parent/node['file']).resolve(strict=True)
                record['source_sha256']=hashlib.sha256(raw.read_bytes()).hexdigest()
                cached_credit=raw.with_suffix('.attribution.json')
                if cached_credit.exists():
                    credit=json.loads(cached_credit.read_text(encoding='utf-8'))
                    record['source']={**{k:v for k,v in credit.items() if k not in {'file','normalized_file'}},**source}
                if kind=='trace':
                    if not node.get('text_free'):raise ValueError('Inspect and confirm text-free raster component: '+key)
                    target,trace_report=trace_asset(raw,folder/'trace',node.get('preset','detail'),node.get('source_kind','reference-raster'),node.get('original_pixel_dimensions'))
                    record.update(approximation=True,trace=trace_report)
                    record['source'].update(origin_kind='traced-raster',source_kind=node.get('source_kind','reference-raster'),
                        original_source_sha256=record['source_sha256'],method='local-vtracer',original_pixel_dimensions=trace_report['original_pixel_dimensions'])
                else:
                    shutil.copy2(raw,folder/'source.svg');target=folder/'component.svg'
                    if node.get('normalize'):
                        try:normalize(raw,target)
                        except ValueError:
                            if not node.get('trace_fallback'):raise
                            trace_fallback(raw,target);record['approximation']=True
                        record['source'].update(modified=True,modification='Normalized vector geometry; see approximation flag for explicit trace fallback')
                    else:shutil.copy2(raw,target)
            record['source']['approximation']=record['approximation']
            record['component_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
            x,y,bw,bh=map(float,node['box'])
            place_component(parent,target,key=key,x=x,y=y,width=bw,height=bh,
                            rotation=float(node.get('rotation',0)),source_url=record['source'].get('url'))
            record['component']=target.relative_to(output).as_posix()
            resolved_node.clear();resolved_node.update(id=key,kind='svg',file=record['component'],box=node['box'],
                rotation=node.get('rotation',0),source=record['source'])
        else:
            group=E.SubElement(parent,'{'+NS+'}g',{'id':key,'data-component-key':key})
            if kind=='group':
                group.attrib.update(attrs(node.get('attrs',{})))
                for child,child_resolved in zip(node['children'],resolved_node['children']):add(child,group,child_resolved)
            elif kind=='shape':
                if node['tag'] not in TAGS:raise ValueError('Unsupported primitive tag: '+node['tag'])
                E.SubElement(group,'{'+NS+'}'+node['tag'],{'id':key+'-shape',**attrs(node['attrs'])})
            elif kind=='text':
                values=attrs(node['attrs']);size=float(values.get('font-size',20));x=values.get('x','0');y=float(values.get('y',0))
                for i,line in enumerate(str(node['content']).split('\n')):
                    child=E.SubElement(group,'{'+NS+'}text',{'id':key+'-line-'+str(i),**values,'x':x,'y':str(y+i*float(node.get('line_height',size*1.2)))})
                    child.text=line
            else:raise ValueError('Unsupported component kind: '+kind)
        records.append(record)
    for node,resolved_node in zip(spec['components'],resolved['components']):add(node,scene,resolved_node)
    existing_ids=[n.get('id') for n in scene.iter() if n.get('id')]
    if len(existing_ids)!=len(set(existing_ids)):raise ValueError('Component IDs collide with generated child IDs; rename the component')
    ids=set(existing_ids)
    for i,node in enumerate(scene.iter()):
        if not node.get('id'):
            candidate='fig-atom-'+str(i)
            while candidate in ids:candidate+='-x'
            ids.add(candidate);node.set('id',candidate)
    svg=output/'scene.svg';E.ElementTree(scene).write(svg,encoding='utf-8',xml_declaration=True)
    for filename,data in [('scene-input.json',spec),('scene.json',resolved),('provenance.json',records)]:
        (output/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    import cairosvg
    cairosvg.svg2png(url=str(svg),write_to=str(output/'svg-preview.png'),output_width=1600)
    def run(script,*args):
        result=subprocess.run([sys.executable,'-X','utf8',str(SCRIPTS/script),*map(str,args)],capture_output=True,text=True,encoding='utf-8')
        if result.returncode:raise RuntimeError(result.stderr+'\n'+result.stdout)
    if export_pptx or render_ppt:
        run('rebuild.py','--input-svg',svg,'--output-dir',output/'export')
    if render_ppt:
        run('preview_ppt.py','--pptx',output/'export'/'editable.pptx','--output-dir',output/'powerpoint')
    report=dict(mode=spec['mode'],svg='scene.svg',scene='scene.json',provenance='provenance.json',components=len(records),
        approximated_components=[r['id'] for r in records if r['approximation']],
        pptx='export/editable.pptx' if export_pptx or render_ppt else None,
        qa_status='rendered-awaiting-visual-review' if render_ppt else 'awaiting-visual-review')
    (output/'job-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scene',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--export-pptx',action='store_true');p.add_argument('--render-ppt',action='store_true')
    a=p.parse_args()
    print(json.dumps(assemble(a.scene,a.output_dir,a.export_pptx,a.render_ppt),indent=2))
