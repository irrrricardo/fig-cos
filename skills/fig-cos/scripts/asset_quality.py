"""Report source-information limits; vector storage alone is not a detail grade."""
import argparse,json
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image


def inspect(source,placed_width,canvas_width,preview_width,original_size=None,provenance=None):
    source=Path(source)
    if min(placed_width,canvas_width,preview_width)<=0:raise ValueError('Positive placement and canvas dimensions required')
    vector=source.suffix.lower()=='.svg';record=dict(file=str(source.resolve()),format='svg' if vector else 'raster',
        target_component_preview_width_px=placed_width*preview_width/canvas_width,
        detail_verdict='requires visual and structural inspection',recommendations=[])
    metadata=json.loads(Path(provenance).read_text(encoding='utf-8')) if provenance else {}
    if not isinstance(metadata,dict):raise ValueError('Pass a single component provenance object, not an aggregate list')
    if vector:
        root=E.parse(source).getroot();record['embedded_images']=sum(n.tag.rsplit('}',1)[-1]=='image' for n in root.iter())
        record['path_count']=sum(n.tag.rsplit('}',1)[-1]=='path' for n in root.iter())
        record['recommendations'].append('Check semantic parts, contour continuity and visual evidence; path count is not a sharpness score.')
        pixels=original_size or metadata.get('original_pixel_dimensions')
    else:
        with Image.open(source) as image:record['file_pixel_dimensions']=list(image.size)
        pixels=original_size or metadata.get('original_pixel_dimensions') or record['file_pixel_dimensions']
    if pixels:
        if min(pixels)<=0:raise ValueError('Original pixel dimensions must be positive')
        record['original_pixel_dimensions']=list(pixels)
        scale=record['target_component_preview_width_px']/pixels[0]
        record['preview_pixels_per_original_pixel']=round(scale,4)
        record['resampling_does_not_add_source_information']=True
        if scale>1.5:record['recommendations'].append('Use structure-based redraw or an independently validated better asset; do not treat enlargement as recovered detail.')
    record['precision_limit']='Unobserved scientific details require evidence or an explicit schematic assumption, even when the rendering is crisp.'
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True,type=Path)
    p.add_argument('--placed-width',required=True,type=float);p.add_argument('--canvas-width',required=True,type=float)
    p.add_argument('--preview-width',type=float,default=3200);p.add_argument('--original-size',nargs=2,type=int)
    p.add_argument('--provenance',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    result=inspect(a.source,a.placed_width,a.canvas_width,a.preview_width,a.original_size,a.provenance)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
