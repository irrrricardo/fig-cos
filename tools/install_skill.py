"""Copy the fig-cos Skill to Codex, Claude Code or DeepSeek Harness (stdlib only)."""
from pathlib import Path
import argparse,json,os,shutil

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--agent',choices=['codex','claude','deepseek-harness'],required=True)
    p.add_argument('--scope',choices=['user','project'],default='user')
    p.add_argument('--project-dir',type=Path,help='Project root for project-scoped installation; defaults to current directory')
    p.add_argument('--target',type=Path,help='Explicit new destination ending in fig-cos; overrides scope defaults')
    a=p.parse_args();source=ROOT/'skills/fig-cos'
    if not (source/'SKILL.md').exists():p.error('Run this installer from a complete fig-cos repository checkout')
    names={'codex':'.agents','claude':'.claude','deepseek-harness':'.dsh'}
    if a.scope=='project':base=(a.project_dir or Path.cwd()).expanduser().resolve()/names[a.agent]
    else:
        base=Path(os.environ.get('DSH_HOME',str(Path.home()/'.dsh'))).expanduser() if a.agent=='deepseek-harness' else Path.home()/names[a.agent]
    target=(a.target.expanduser() if a.target else base/'skills/fig-cos').absolute()
    if target.name!='fig-cos':p.error('Destination directory must be named fig-cos')
    if target.exists():p.error('Destination exists; refusing to overwrite. Keep your current skill or choose a new target.')
    if target.is_relative_to(source.resolve()):p.error('Destination cannot be inside the source skill')
    shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    print(json.dumps({'skill':'fig-cos','agent':a.agent,'installed':str(target),
        'invocation':{'codex':'$fig-cos','claude':'/fig-cos','deepseek-harness':'Ask the agent to load and use the fig-cos skill'}[a.agent],
        'dependencies':'Bundled Python helper requirements are not installed by this copy operation; let the agent prepare its environment when needed.'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
