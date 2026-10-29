"""Portable fig-cos entry point. No model SDK or credentials are required."""
from __future__ import annotations
import argparse,importlib,importlib.metadata,json,os,platform,shutil,subprocess,sys
from pathlib import Path

VERSION='0.1.0'
TOOLS={'trace':'trace_asset.py','compose':'compose.py','export':'rebuild.py',
    'preview-ppt':'preview_ppt.py','check-preserved':'check_preserved.py',
    'quality':'asset_quality.py','search-icons':'icon_library.py',
    'catalog':'science_catalogs.py','candidates':'candidate_board.py',
    'pdf-region':'pdf_region_assets.py','normalize-svg':'normalize_icon.py',
    'validate-svg':'vendor/validate_vector_svg.py'}

def skill_root():
    portable=Path(__file__).resolve().parent/'skills'/'fig-cos'
    if portable.is_dir():return portable
    repository=Path(__file__).resolve().parents[2]/'skills'/'fig-cos'
    if repository.is_dir():return repository
    return Path(__file__).resolve().parents[1]

def doctor():
    modules={'vtracer':'vtracer','Pillow':'PIL','python-pptx':'pptx','fonttools':'fontTools',
        'picosvg':'picosvg','skia-pathops':'pathops','CairoSVG':'cairosvg'}
    checks={}
    for package,module in modules.items():
        try:
            importlib.import_module(module)
            checks[package]={'available':True,'version':importlib.metadata.version(package)}
        except Exception as exc:checks[package]={'available':False,'error':str(exc)}
    optional={}
    for name,module in [('pdf','pymupdf'),('powerpoint_com','win32com.client')]:
        try:importlib.import_module(module);optional[name]={'import_available':True}
        except Exception:optional[name]={'import_available':False}
    report={'version':VERSION,'python':platform.python_version(),'platform':platform.system(),
        'core_ready':all(c['available'] for c in checks.values()),'dependencies':checks,'optional':optional,
        'powerpoint_application_verified':False,'skill_directory':str(skill_root()),
        'default_reconstruction':'Previous local tracing','model_backend':'provided by the calling agent; not bundled',
        'cache':os.environ.get('FIG_COS_CACHE',str(Path(os.environ.get('XDG_CACHE_HOME',str(Path.home()/'.cache')))/'fig-cos'))}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['core_ready'] else 1

def run(script,args):
    return subprocess.run([sys.executable,'-X','utf8',str(skill_root()/'scripts'/script),*args]).returncode

def main(argv=None):
    args=list(sys.argv[1:] if argv is None else argv)
    parser=argparse.ArgumentParser(description=__doc__,epilog='Commands: doctor, install-skill, demo, '+', '.join(TOOLS))
    parser.add_argument('--version',action='version',version=VERSION)
    parser.add_argument('command',nargs='?')
    if not args or args[0] in ('-h','--help','--version'):
        parser.parse_args(args);parser.print_help();return 0
    command=args.pop(0)
    if command=='doctor':
        parser.parse_args([command,*args]);return doctor()
    if command=='install-skill':
        installer=argparse.ArgumentParser(prog='fig-cos install-skill')
        installer.add_argument('--target',type=Path,required=True,help='New skill directory; final directory name must be fig-cos')
        destination=installer.parse_args(args).target.expanduser().absolute()
        if destination.name!='fig-cos':installer.error('Target directory must be named fig-cos to match the portable skill identity')
        if destination.exists():installer.error('Target exists; choose a new location. Existing skills are never overwritten.')
        shutil.copytree(skill_root(),destination,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        entry=destination/'SKILL.md'
        entry.write_text(entry.read_text(encoding='utf-8').replace('\nname: fig_cos\n','\nname: fig-cos\n',1).replace('$fig_cos','$fig-cos'),encoding='utf-8')
        ui=destination/'agents/openai.yaml'
        if ui.exists():ui.write_text(ui.read_text(encoding='utf-8').replace('$fig_cos','$fig-cos'),encoding='utf-8')
        print(json.dumps({'installed':str(destination),'name':'fig-cos'},indent=2));return 0
    if command=='demo':
        demo=argparse.ArgumentParser(prog='fig-cos demo');demo.add_argument('--output-dir',type=Path,required=True)
        demo.add_argument('--render-ppt',action='store_true');options=demo.parse_args(args)
        call=['--scene',str(skill_root()/'assets/templates/editable-components.json'),'--output-dir',str(options.output_dir),'--export-pptx']
        if options.render_ppt:call.append('--render-ppt')
        return run('compose.py',call)
    if command in TOOLS:return run(TOOLS[command],args)
    parser.error('Unknown command: '+command)

if __name__=='__main__':raise SystemExit(main())
