"""Verify that an SVG edit changed only explicitly selected components."""
import argparse,copy,json
from pathlib import Path
import xml.etree.ElementTree as E


def check(before,after,keys=(),all_icon_groups=False):
    def stripped(path):
        root=copy.deepcopy(E.parse(path).getroot());removed=[]
        for parent in list(root.iter()):
            for node in list(parent):
                key=node.get('data-component-key') or node.get('data-icon-key') or node.get('id')
                if key in keys or (all_icon_groups and node.get('data-icon-key')):
                    parent.remove(node);removed.append(key)
        return root,removed
    left,lremoved=stripped(before);right,rremoved=stripped(after)
    def canonical(node):
        text=node.text if node.text and node.text.strip() else ''
        tail=node.tail if node.tail and node.tail.strip() else ''
        return (node.tag,tuple(sorted(node.attrib.items())),text,tuple(canonical(c) for c in node),tail)
    missing={key for key in keys if key not in lremoved or key not in rremoved}
    equal=canonical(left)==canonical(right) and not missing
    return dict(unchanged_outside_components=equal,ignored_before=lremoved,ignored_after=rremoved,
                missing_requested_components=sorted(missing),scope='DOM text, geometry, attributes and ordering; visual rendering still needs inspection')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before',required=True,type=Path);p.add_argument('--after',required=True,type=Path)
    p.add_argument('--editable-component',action='append',default=[]);p.add_argument('--all-icon-groups',action='store_true')
    p.add_argument('--report',type=Path)
    a=p.parse_args();result=check(a.before,a.after,a.editable_component,a.all_icon_groups)
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2));raise SystemExit(0 if result['unchanged_outside_components'] else 1)
