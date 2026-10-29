"""Generic schematic design examples with native editable lighting.

These are schematic renderings, not recovered hidden pixels or exact molecular
structures. The wheeled-bin/protein examples failed reference-matching review;
do not substitute them for a specific reference component in restoration tasks.
"""
from __future__ import annotations
import argparse,math,json
from pathlib import Path
import xml.etree.ElementTree as E
NS='http://www.w3.org/2000/svg'
KINDS={'wheeled-bin','metal-bin','ribbon-protein','cell-aggregate'}


class Drawing:
    def __init__(self,w,h):
        self.root=E.Element('{'+NS+'}svg',{'viewBox':f'0 0 {w} {h}','width':str(w),'height':str(h)})
        self.defs=E.SubElement(self.root,'{'+NS+'}defs');self.current=self.root;self.count=0
    def node(self,tag,**attrs):
        self.count+=1
        return E.SubElement(self.current,'{'+NS+'}'+tag,{'id':f'part-{self.count}',**{k.replace('_','-'):str(v) for k,v in attrs.items()}})
    def gradient(self,key,stops,vertical=False):
        g=E.SubElement(self.defs,'{'+NS+'}linearGradient',{'id':key,'x1':'0','y1':'0','x2':'0' if vertical else '1','y2':'1' if vertical else '0'})
        for offset,color in stops:E.SubElement(g,'{'+NS+'}stop',{'offset':str(offset),'stop-color':color})
        return f'url(#{key})'
    def path(self,d,fill='none',stroke='none',sw=1,**attrs):
        return self.node('path',d=d,fill=fill,stroke=stroke,stroke_width=sw,stroke_linecap='round',stroke_linejoin='round',**attrs)
    def ellipse(self,x,y,rx,ry,fill,stroke='none',sw=1,**attrs):return self.node('ellipse',cx=x,cy=y,rx=rx,ry=ry,fill=fill,stroke=stroke,stroke_width=sw,**attrs)
    def poly(self,points,fill,stroke='none',sw=1):return self.node('polygon',points=' '.join(f'{x},{y}' for x,y in points),fill=fill,stroke=stroke,stroke_width=sw,stroke_linejoin='round')
    def group(self,key,transform=None):
        attrs={'id':key,'data-component-key':key}
        if transform:attrs['transform']=transform
        self.current=E.SubElement(self.root,'{'+NS+'}g',attrs);return self.current


def wheeled_bin(p):
    d=Drawing(240,320)
    front=d.gradient('front',[(0,'#438aa8'),(.32,'#277a9b'),(1,'#21627f')])
    side=d.gradient('side',[(0,'#235773'),(1,'#153f58')])
    lid=d.gradient('lid',[(0,'#508fa9'),(.6,'#2a6c8a'),(1,'#245773')],True)
    wheel=d.gradient('wheel',[(0,'#77838b'),(.3,'#4d5962'),(1,'#263641')])
    d.group('rear-wheels')
    d.ellipse(58,275,14,23,wheel,'#263541',1.6);d.ellipse(58,275,5,10,'#86949e')
    d.ellipse(179,274,13,22,wheel,'#20333f',1.6)
    d.group('bin-shell')
    d.path('M43 61 L168 82 L162 289 Q114 296 64 271 Z',front,'#1a526c',1.6)
    d.path('M168 82 L207 61 L195 265 L162 289 Z',side,'#194962',1.6)
    d.path('M53 88 L65 263 Q88 275 113 279',stroke='#80b5c5',sw=1.5,opacity=.65)
    d.path('M177 110 L192 103 L185 244 L174 253 Z','#17465f')
    d.path('M120 163 L151 163 L149 272 L118 278 Z','#1b5d7c',opacity=.6)
    d.path('M128 170 L146 168 L146 208 L128 212 Z','#154e6b',opacity=.5)
    d.path('M170 112 L168 263',stroke='#4d839a',sw=1)
    d.group('rim-and-lid')
    d.poly([(38,64),(79,39),(213,61),(171,88)],'#184e69','#1a4e68',1)
    d.path('M35 48 L81 28 L209 49 Q216 51 215 58 L173 79 L35 58 Z',lid,'#1a506b',1.5)
    d.path('M36 48 L173 69 L214 50',stroke='#73a8bc',sw=1.6)
    d.path('M35 57 L173 79 L173 86 L36 64 Z','#225d7b','#1a506b',1)
    d.path('M173 79 L215 58 L214 66 L173 86 Z','#184964')
    d.poly([(79,28),(89,23),(110,26),(101,31)],'#326e8b')
    d.path('M90 32 L160 43 Q165 44 163 49 L94 39 Z','#20536f','#173f56',.8)
    d.path('M95 33 L158 43',stroke='#6b9eb2',sw=1)
    d.group('recycling-mark')
    # Three consistent arrows around a triangular recycling loop.
    for angle in (0,120,240):
        g=d.node('g',transform=f'translate(99 153) rotate({angle})')
        parent=d.current;d.current=g
        d.path('M-3 -25 Q4 -30 9 -21 L17 -7 L23 -10 L20 4 L6 0 L11 -3 L3 -17 Q1 -21 -3 -17 L-9 -7 L-15 -11 Z','#f0f6f5')
        d.current=parent
    d.current=d.root
    return d


def metal_bin(p):
    d=Drawing(180,240)
    body=d.gradient('metal',[(0,'#979ba8'),(.16,'#e2e3e9'),(.42,'#c1c2ce'),(.7,'#eeeef2'),(1,'#969aa8')])
    lid=d.gradient('metal-lid',[(0,'#a4a7b4'),(.4,'#ececf2'),(1,'#b1b3bf')],True)
    d.group('body')
    d.path('M28 48 L153 48 L140 211 Q91 229 42 211 Z',body,'#9296a5',1.3)
    for i in range(21):
        x=34+i*5.65;bottom=46+(x-34)*.77
        d.path(f'M{x:.2f} 60 L{bottom:.2f} 208',stroke='#8e93a3',sw=.7,opacity=.7)
        d.path(f'M{x+1.4:.2f} 60 L{bottom+1.0:.2f} 208',stroke='#f6f6fa',sw=.8,opacity=.8)
    d.ellipse(91,211,49,11,'#c1c3cd','#979ca8',1)
    d.path('M44 211 Q91 225 139 211',stroke='#f0f0f5',sw=1)
    d.group('rolled-rim-and-lid')
    d.ellipse(91,48,65,21,lid,'#969ba9',1.2)
    d.ellipse(91,43,57,16,'#d4d6e0','#a1a6b4',1)
    d.ellipse(91,40,49,12,lid,'#b3b7c4',.8)
    d.ellipse(91,38,13,4,'#eff0f5','#a5aab8',.7)
    d.current=d.root;return d


def ribbon_protein(p):
    d=Drawing(240,240)
    d.group('backbone-loops')
    loops=['M105 36 C90 10 119 -1 125 18 C134 43 103 41 111 61',
           'M112 55 C153 31 167 54 152 72 C141 86 173 88 185 73 C195 58 220 75 206 90 C184 105 225 125 204 145',
           'M75 83 C48 60 51 90 62 101 C76 117 35 135 47 157 C61 178 90 153 107 173',
           'M155 125 C179 145 160 169 179 181 C200 193 199 163 183 159',
           'M83 166 C61 190 39 184 44 206 C53 227 82 191 92 207 C112 228 129 198 121 185',
           'M116 99 C126 80 96 75 89 91 C79 106 107 130 127 115 C148 100 159 108 153 127',
           'M62 144 C41 158 55 177 73 163 C89 150 101 166 93 179']
    for path in loops:d.path(path,stroke='#497e99',sw=1.2)
    # Helices use analytic ribbon faces and ordered overlap, not a sequence or
    # atomistic fold inferred from the thumbnail.
    helices=[(82,128,68,-32,8),(118,101,79,34,10),(126,151,81,40,10),(71,173,56,-32,7),(99,65,52,24,7)]
    for index,(cx,cy,length,angle,turns) in enumerate(helices):
        d.group('helix-'+str(index),f'translate({cx} {cy}) rotate({angle})')
        step=length/turns
        for i in range(turns):
            x=-length/2+i*step
            d.path(f'M{x} -7 C{x+step*.2} -13 {x+step*.8} -13 {x+step} -7 L{x+step} 5 C{x+step*.6} 9 {x+step*.3} 9 {x} 5 Z','#26779f','#1f5f82',.6)
            d.path(f'M{x} -7 C{x+step*.22} -10 {x+step*.7} -10 {x+step} -7 L{x+step} -1 C{x+step*.6} -4 {x+step*.3} -4 {x} -1 Z','#87bfd8')
            d.path(f'M{x} 5 Q{x+step*.5} 8 {x+step} 5',stroke='#174f75',sw=.7)
        d.current=d.root
    d.group('beta-ribbon')
    d.poly([(139,131),(156,143),(173,130),(171,137),(190,130),(178,151),(180,143),(157,159),(131,143)],'#4a9bc1','#2b6d93',.8)
    d.poly([(139,131),(156,143),(173,130),(171,137),(156,151),(135,138)],'#90c4dc')
    d.path('M106 179 C131 186 150 165 145 148',stroke='#497e99',sw=1.1)
    d.current=d.root;return d


def cell_aggregate(p):
    d=Drawing(240,240)
    fill=d.gradient('cytoplasm',[(0,'#fff0df'),(.44,'#ffd5bd'),(1,'#ec9e81')],True)
    nucleus=d.gradient('nucleus',[(0,'#e6a088'),(1,'#c77464')],True)
    if p.get('palette')=='blue':
        d.defs.clear();fill=d.gradient('cytoplasm',[(0,'#effaff'),(.44,'#bce3f3'),(1,'#75b3d5')],True)
        nucleus=d.gradient('nucleus',[(0,'#7eb9d5'),(1,'#347fa9')],True)
    positions=p.get('positions',[[71,62,38],[125,52,37],[173,83,36],[171,137,38],[127,177,38],[75,168,37],[55,113,37],[114,112,39]])
    membrane='#d88870' if p.get('palette')!='blue' else '#4e96b8'
    for i,(x,y,r) in enumerate(positions):
        d.group('cell-'+str(i))
        # Continuous cubic membrane with gentle asymmetry, smooth at any scale.
        path=f'M{x-r*.25} {y-r} C{x+r*.55} {y-r*1.06} {x+r*1.04} {y-r*.45} {x+r} {y+r*.07} C{x+r*.96} {y+r*.79} {x+r*.41} {y+r*1.03} {x-r*.21} {y+r*.94} C{x-r*.91} {y+r*.83} {x-r*1.09} {y+r*.14} {x-r*.95} {y-r*.35} C{x-r*.8} {y-r*.8} {x-r*.5} {y-r*1.02} {x-r*.25} {y-r} Z'
        d.path(path,fill,membrane,1.5)
        d.path(f'M{x-r*.63} {y-r*.34} C{x-r*.43} {y-r*.78} {x+r*.1} {y-r*.85} {x+r*.37} {y-r*.57}',stroke='#fff6e9' if p.get('palette')!='blue' else '#f6fcff',sw=2.4,opacity=.7)
        d.ellipse(x+r*.02,y+r*.07,r*.41,r*.36,nucleus,membrane,.55,opacity=.83)
        d.ellipse(x-r*.06,y-r*.02,r*.13,r*.1,'#f8c4ae' if p.get('palette')!='blue' else '#a4d4e8',opacity=.8)
        for j,(dx,dy) in enumerate([(-.56,.17),(.48,-.3),(.39,.46)]):
            d.ellipse(x+r*dx,y+r*dy,r*.055,r*.037,'#d38d77' if p.get('palette')!='blue' else '#6daac5',opacity=.65)
    d.current=d.root;return d


def draw(kind,parameters,target):
    if kind not in KINDS:raise ValueError('Unknown refined component: '+kind)
    supported={'cell-aggregate':{'palette','positions'}}.get(kind,set())
    if set(parameters)-supported:raise ValueError('Unsupported refinement parameters: '+str(sorted(set(parameters)-supported)))
    if kind=='cell-aggregate' and parameters.get('palette','orange') not in {'orange','blue'}:raise ValueError('Cell palette must be orange or blue')
    if kind=='cell-aggregate' and 'positions' in parameters:
        if not parameters['positions'] or any(len(v)!=3 or v[2]<=0 for v in parameters['positions']):raise ValueError('Cell positions are nonempty x,y,positive-radius triples')
    builder={'wheeled-bin':wheeled_bin,'metal-bin':metal_bin,'ribbon-protein':ribbon_protein,'cell-aggregate':cell_aggregate}[kind](parameters)
    builder.root.set('viewBox',{'wheeled-bin':'27 17 194 286','metal-bin':'20 20 142 208',
        'ribbon-protein':'35 0 195 232','cell-aggregate':'10 10 210 210'}[kind])
    if kind=='cell-aggregate' and parameters.get('positions'):
        points=parameters['positions'];x0=min(x-r*1.15 for x,y,r in points);y0=min(y-r*1.15 for x,y,r in points)
        x1=max(x+r*1.15 for x,y,r in points);y1=max(y+r*1.15 for x,y,r in points)
        builder.root.set('viewBox',f'{x0} {y0} {x1-x0} {y1-y0}')
    for i,node in enumerate(builder.root.iter()):
        if not node.get('id'):node.set('id','refined-node-'+str(i))
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    E.ElementTree(builder.root).write(target,encoding='utf-8',xml_declaration=True)
    return target


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('kind',choices=sorted(KINDS));p.add_argument('--output',type=Path,required=True)
    p.add_argument('--parameters',type=Path);a=p.parse_args()
    print(draw(a.kind,json.loads(a.parameters.read_text()) if a.parameters else {},a.output))
