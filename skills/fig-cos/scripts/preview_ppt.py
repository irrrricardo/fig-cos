"""Render a generated PPTX in isolated PowerPoint, read-only."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pptx', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--width',type=int,default=2000)
    args = parser.parse_args()
    source = args.pptx.resolve(strict=True)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    app = deck = None
    try:
        app = win32com.client.DispatchEx('PowerPoint.Application')
        deck = app.Presentations.Open(str(source), ReadOnly=True, Untitled=False, WithWindow=False)
        slide = deck.Slides.Item(1)
        width = args.width
        if not 256<=width<=8192:raise ValueError('Preview width must be 256 to 8192')
        height = round(width * deck.PageSetup.SlideHeight / deck.PageSetup.SlideWidth)
        preview = output / 'powerpoint-preview.png'
        slide.Export(str(preview), 'PNG', width, height)
        def leaves(shapes):
            for shape in shapes:
                if shape.Type==6:yield from leaves(shape.GroupItems)
                else:yield shape
        shapes=list(leaves(slide.Shapes))
        labels = [shape.TextFrame.TextRange.Text for shape in shapes
                  if shape.HasTextFrame and shape.TextFrame.HasText]
        report = dict(pptx=str(source), preview=str(preview), width=width, height=height,
            pptx_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            top_level_object_count=slide.Shapes.Count,native_object_count=len(shapes),native_text=labels,
            rendered_in='Microsoft PowerPoint',ppt_rendered=True,visually_reviewed=False)
        (output / 'powerpoint-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        if deck is not None:
            deck.Close()
        if app is not None and app.Presentations.Count == 0:
            app.Quit()
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    main()
