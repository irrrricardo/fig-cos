"""Small editable schematic components, not empirical molecular structures."""
import math
import xml.etree.ElementTree as E
from pathlib import Path
NS='http://www.w3.org/2000/svg'


def draw_component(kind,parameters,target):
    from refined_components import KINDS,draw
    if kind in KINDS:return draw(kind,parameters,target)
    p=parameters
    root=E.Element('{'+NS+'}svg',{'viewBox':'0 0 400 240'})
    def add(tag,**attrs):return E.SubElement(root,'{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
    if kind=='dna':
        turns=float(p.get('turns',2));amplitude=float(p.get('amplitude',55));weight=float(p.get('stroke_width',9))
        if not 0.5<=turns<=8 or not 5<=amplitude<=85 or not 1<=weight<=20:raise ValueError('DNA parameters outside supported drawing bounds')
        colors=p.get('strand_colors',['#196b8a','#b63b50'])
        if len(colors)!=2:raise ValueError('Two strand colors required')
        def y(t,strand):return 120+(1 if strand==0 else -1)*amplitude*math.sin(t*2*math.pi*turns)
        for n in range(1,round(turns*12)):
            t=n/(turns*12);x=20+360*t
            add('line',x1=x,y1=y(t,0),x2=x,y2=y(t,1),stroke=p.get('rung_color','#85a6b2'),stroke_width=4)
        count=math.ceil(turns*2)
        for section in range(count):
            lo=section/(turns*2);hi=min(1,(section+1)/(turns*2))
            # Alternate which strand is in front at successive crossings.
            for strand in ([0,1] if section%2==0 else [1,0]):
                points=[(20+360*t,y(t,strand)) for t in [lo+(hi-lo)*i/32 for i in range(33)]]
                d='M'+' L'.join(f'{x:.5f} {v:.5f}' for x,v in points)
                add('path',d=d,fill='none',stroke=colors[strand],stroke_width=weight,stroke_linecap='round')
    elif kind=='cell-cluster':
        positions=p.get('positions',[[165,68],[225,79],[119,119],[187,122],[250,137],[149,180],[214,184]])
        if not 1<=len(positions)<=40:raise ValueError('Use 1 to 40 cell positions')
        abnormal=p.get('highlight_index',4);radius=float(p.get('radius',42))
        if not 5<=radius<=65:raise ValueError('Cell radius outside supported drawing bounds')
        for index,(x,y) in enumerate(positions):
            color=p.get('highlight_fill','#edb1b0') if index==abnormal else p.get('cell_fill','#d8eef5')
            add('ellipse',cx=x,cy=y,rx=radius,ry=radius*.92,fill=color,stroke=p.get('membrane_color','#88b6c5'),stroke_width=2)
            add('ellipse',cx=x,cy=y,rx=radius*.35,ry=radius*.32,
                fill=p.get('highlight_nucleus','#d77f83') if index==abnormal else p.get('nucleus_fill','#aad4e0'))
    else:raise ValueError('Available parametric components: dna, cell-cluster, '+', '.join(sorted(KINDS)))
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    E.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
    return target
