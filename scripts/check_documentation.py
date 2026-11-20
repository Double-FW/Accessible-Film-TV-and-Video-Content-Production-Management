"""Check local navigation and documented source boundaries; no network or AV tests."""
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=('README.md','AGENTS.md','LICENSE','NOTICE.md','Terminology_Alignment.md','Public_Source_Routing.md','public-repository-links.json','Accessible_TV_Content_Guidance_for_Production_Teams.md','Production_Workflow_and_Handoff_Map.md','Production_and_Audio_Description_Mapping.md','Production_and_Captions_Mapping.md','CHANGELOG.md','REVIEW_2026-11-20.md')
PACK='Accessible-Film-TV-and-Video-Content-RAG-and-Prompts'

def anchors(text):
    result=set(re.findall(r'<a\s+id="([^"]+)"',text));seen={}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$',text,re.M):
        h=re.sub(r'\[([^]]+)\]\([^)]*\)',r'\1',heading).replace('`','').lower()
        h=''.join(c for c in h if c in '-_ ' or unicodedata.category(c)[0] in 'LN').replace(' ','-')
        n=seen.get(h,0);seen[h]=n+1;result.add(h+(f'-{n}' if n else ''))
    return result

def check(root=ROOT):
    root=Path(root).resolve();errors=[]
    for path in REQUIRED:
        if not (root/path).is_file():errors.append('Missing required file: '+path)
    docs=sorted(root.rglob('*.md'));files=[p for p in docs if '.git' not in p.parts]
    try:
        reg=json.loads((root/'public-repository-links.json').read_text());repos=reg['repositories']
        registered={x['repository'] for x in repos}
        if len(registered)!=len(repos):errors.append('Duplicate repository register entry.')
        for x in repos:
            if x['visibility']!='public' or x['url']!='https://github.com/'+x['repository'] or not x['checked_on']:errors.append('Invalid recorded public repository: '+x['repository'])
    except (OSError,ValueError,KeyError) as e:errors.append('Invalid repository register: '+type(e).__name__);registered=set()
    links=0
    for p in files:
        text=p.read_text();rel=p.relative_to(root).as_posix()
        if '\ufffd' in text:errors.append(rel+': replacement character')
        if re.search(r'\b(?:CC-BY|CC BY|Creative Commons|non-commercial only|all rights reserved)\b',text,re.I):errors.append(rel+': incompatible repository rights declaration')
        for val in re.findall(r'^license:\s*["\']?([^"\'\n]+)',text,re.M):
            if val.strip()!='MIT':errors.append(rel+': non-MIT licence metadata')
        fence=None
        for line in text.splitlines():
            m=re.match(r'^\s*(`{3,}|~{3,})',line)
            if m:
                token=m.group(1)
                if fence is None:fence=token
                elif token[0]==fence[0] and len(token)>=len(fence):fence=None
        if fence:errors.append(rel+': unclosed code fence')
        for target in re.findall(r'\[[^\]\n]+\]\(([^\n]+?)\)',text):
            target=target.strip().strip('<>');u=urlsplit(target)
            if u.scheme or u.netloc:continue
            links+=1;dest=(p.parent/unquote(u.path)).resolve() if u.path else p
            if not dest.is_relative_to(root) or not dest.is_file():errors.append(rel+': missing local target '+target);continue
            if u.fragment and unquote(u.fragment) not in anchors(dest.read_text()):errors.append(rel+': missing local fragment '+target)
        for name in re.findall(r'https://github.com/(Double-FW/[^/\s)#?`"<>]+)',text):
            if name not in registered:errors.append(rel+': unregistered repository '+name)
    for file in ('README.md','AGENTS.md'):
        t=(root/file).read_text()
        if not t.startswith('---\n') or not re.search(r'^license: "MIT"$',t,re.M):errors.append(file+': expected MIT front matter')
    agent=(root/'AGENTS.md').read_text()
    for token in ('approved_by: null','inspected_revision:','## 5. Retrieval, terminology and output contract','**unknown**','**not tested**'):
        if token not in agent:errors.append('AGENTS.md: missing documented boundary '+token)
    licence=(root/'LICENSE').read_text()
    if not licence.startswith('MIT License\n') or 'Copyright (c) 2026 Double FW Ltd' not in licence or 'Permission is hereby granted, free of charge' not in licence:errors.append('Expected MIT licence and company notice.')
    index=(root/PACK/'RAG_Reference.md').read_text();coverage=(root/PACK/'Source_Coverage.md').read_text();prompts=(root/PACK/'Content_Creation_and_Production_Activities_and_Prompts.md').read_text()
    for i in range(1,11):
        if f'id="s{i:03}"' not in index:errors.append('Missing RAG source anchor '+str(i))
    for text in (index,coverage):
        if '9f9a157270f9087c59b2ab17b54fc166a76d9d7e' in text or '6/6 tracked files' in text:errors.append('Obsolete snapshot claim in current retrieval navigation.')
    if len(re.findall(r'^## [1-8]\. ',prompts,re.M))!=8 or len(re.findall(r'^### Example prompt [12]$',prompts,re.M))!=16:errors.append('Expected eight activities and sixteen prompts.')
    ad=(root/'Production_and_Audio_Description_Mapping.md').read_text()
    if re.search(r'\b(?:PM\d{2}|R\d{2})\b',ad):errors.append('Undefined production identifier in AD crosswalk.')
    if '| CCS 13 |' in (root/'Production_and_Captions_Mapping.md').read_text():errors.append('Ambiguous caption section reference.')
    return {'status':'failed' if errors else 'passed','markdown_files':len(files),'local_links_checked':links,'registered_public_repositories':len(registered),'errors':errors,'scope':'Local navigation, metadata, declared MIT rights and known source/status invariants only. No AV evaluation, model testing, legal assessment or live external-link check.'}

if __name__=='__main__':
    try:report=check()
    except (OSError,ValueError) as e:report={'status':'failed','errors':[str(e)]}
    print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(0 if report['status']=='passed' else 1)
