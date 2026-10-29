"""Convert an inspected text-free raster component into approximate SVG paths."""
import argparse,hashlib,json,shutil
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
import vtracer
from rebuild import PRESETS,normalize_trace


def trace_asset(source,output,preset='detail',source_kind='reference-raster',original_size=None):
    if original_size and (len(original_size)!=2 or min(original_size)<=0):raise ValueError('Original pixel dimensions must be positive width and height')
    source=Path(source).resolve(strict=True);output=Path(output).resolve()
    if output.exists():raise ValueError('Choose a fresh component directory')
    with Image.open(source) as image:
        width,height=image.size
        if getattr(image,'n_frames',1)!=1:raise ValueError('Select one image frame')
    output.mkdir(parents=True)
    shutil.copy2(source,output/('source'+source.suffix.lower()))
    target=output/'component.svg'
    vtracer.convert_image_to_svg_py(str(source),str(target),colormode='color',hierarchical='stacked',mode='spline',
        corner_threshold=60,max_iterations=10,splice_threshold=45,path_precision=3,**PRESETS[preset])
    normalize_trace(target,width,height)
    count=sum(node.tag.rsplit('}',1)[-1]=='path' for node in E.parse(target).iter())
    report=dict(source_kind=source_kind,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        width=width,height=height,path_count=count,component='component.svg',method='local-vtracer',
        original_pixel_dimensions=list(original_size) if original_size else [width,height],
        input_resampled=bool(original_size and tuple(original_size)!=(width,height)),
        source_information_added_by_tracing=False,
        approximation=True,live_text=False,
        limitations='Color contours only; original semantic parts and alpha/gradient layers are not recovered. Verify science and geometry visually.')
    (output/'provenance.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return target,report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-image',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--preset',choices=PRESETS,default='detail')
    p.add_argument('--source-kind',choices=['reference-raster','ai-generated'],default='reference-raster')
    p.add_argument('--text-free',action='store_true',help='The caller has inspected this asset and verified no lettering remains')
    p.add_argument('--original-size',nargs=2,type=int,help='Native source pixels before any preprocessing enlargement')
    a=p.parse_args()
    if not a.text_free:p.error('Inspect the asset first; use --text-free only when no lettering remains')
    target,report=trace_asset(a.input_image,a.output_dir,a.preset,a.source_kind,a.original_size)
    print(json.dumps(dict(svg=str(target),**report),indent=2))
