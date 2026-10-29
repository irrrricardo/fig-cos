"""Validate a clean public distribution without requiring a particular agent app."""
from pathlib import Path
import ast,hashlib,json,re,zipfile,tarfile
import yaml

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'src/fig_cos/skills/fig-cos'

def main():
    entry=(SKILL/'SKILL.md').read_text(encoding='utf-8')
    match=re.match(r'^---\n(.*?)\n---\n',entry,re.S);assert match,'Missing skill frontmatter'
    meta=yaml.safe_load(match[1]);assert meta['name']==SKILL.name=='fig-cos'
    assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',meta['name'])
    assert isinstance(meta['description'],str) and 0<len(meta['description'])<=1024
    assert 'Previous local tracing' in entry
    vendor=json.loads((SKILL/'references/vendor-sha256.json').read_text(encoding='utf-8'))
    for name,digest in vendor.items():assert hashlib.sha256((SKILL/'scripts/vendor'/name).read_bytes()).hexdigest()==digest,name
    for path in (ROOT/'src').rglob('*.py'):ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path))
    markdown=[*ROOT.glob('*.md'),*(ROOT/'docs').glob('*.md'),*SKILL.rglob('*.md')]
    for path in markdown:
        for link in re.findall(r'\]\(([^\s)]+)(?:\s+[^)]*)?\)',path.read_text(encoding='utf-8')):
            if not re.match('[a-zA-Z]+:',link) and not link.startswith('#'):
                assert (path.parent/link.split('#')[0]).exists(),f'{path}: {link}'
    # Distribution allowlist and privacy scan: no local project history or Windows user paths.
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(part in {'.git','.venv','build','dist','outputs','work','__pycache__'} or part.endswith('.egg-info') for part in path.relative_to(ROOT).parts):continue
        if path.suffix in {'.py','.md','.yaml','.yml','.json','.svg','.toml','.txt','.cff'}:
            text=path.read_text(encoding='utf-8-sig')
            assert not re.search(r'[A-Za-z]:[/\\](?:Users|creation_w_Codex)[/\\]',text),f'Local path in {path}'
            assert not re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9]{20,}',text),f'Possible credential in {path}'
        if path.suffix=='.pptx':
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    if name.endswith('.xml'):
                        assert not re.search(rb'[A-Za-z]:[/\\](?:Users|creation_w_Codex)[/\\]',archive.read(name)),f'Local path in {path}:{name}'
    for file in (SKILL/'assets').rglob('*.svg'):
        assert file.with_suffix('.attribution.json').exists(),f'Missing asset attribution: {file}'
    for wheel in (ROOT/'dist').glob('*.whl'):
        with zipfile.ZipFile(wheel) as archive:
            names=archive.namelist()
            assert not any('__pycache__' in n or n.endswith('.pyc') for n in names),'Bytecode leaked into wheel'
            for resource in ['SKILL.md','scripts/vendor/LICENSE','assets/templates/editable-components.json']:
                assert 'fig_cos/skills/fig-cos/'+resource in names,resource
    for source in (ROOT/'dist').glob('*.tar.gz'):
        with tarfile.open(source) as archive:
            names=archive.getnames()
            assert not any('__pycache__' in n or n.endswith('.pyc') for n in names),'Bytecode leaked into source archive'
            assert any(n.endswith('/docs/GALLERY.md') for n in names),'Gallery missing from source archive'
            assert any(n.endswith('/tools/validate_release.py') for n in names),'Validation tool missing from source archive'
    print(json.dumps({'skill_format':'passed','source_syntax':'passed','local_links':'passed','vendor_integrity':'passed','asset_attributions':'passed','privacy_scan':'passed'},indent=2))

if __name__=='__main__':main()
