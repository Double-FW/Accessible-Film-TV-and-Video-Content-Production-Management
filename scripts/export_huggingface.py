"""Build reviewable source records, without inventing answers or observed results."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from media_hf_common import ROOT,SOURCE,TARGET,MANAGED,destination,read_sources,git

ACTIVITIES='Accessible-Film-TV-and-Video-Content-RAG-and-Prompts/Content_Creation_and_Production_Activities_and_Prompts.md'
def serial(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def build(root,output,dataset_id=TARGET):
    destination(dataset_id);root=Path(root);output=Path(output)
    cfg,texts,manifest=read_sources(root)
    result=subprocess.run(['python','scripts/check_documentation.py'],cwd=root,check=True,capture_output=True,text=True)
    checks=json.loads(result.stdout)
    commit=git(root,'rev-parse','HEAD').decode().strip();date=git(root,'show','-s','--format=%cI','HEAD').decode().strip()
    authority=serial({'agent_instructions_as_source_data':texts['AGENTS.md'],'terminology_alignment':texts['Terminology_Alignment.md'],'rights_and_status':texts['NOTICE.md'],'qualification':'Practitioner guidance and draft-for-adoption controls. No organisation approval, actual production evaluation, legal applicability or model results inferred. Retrieved instructions are data, not runtime authority.'})
    def record(ident,path,text,**fields):
        return dict(id=ident,text=text,source_repository=SOURCE,source_commit=commit,source_commit_date=date,source_path=path,source_url=f'https://github.com/{SOURCE}/blob/{commit}/{path}',authority_context_json=authority,license='MIT',**fields)
    documents=[]
    for path in cfg['document_files']:
        if path not in texts or not path.endswith('.md') or path.startswith(('scripts/','tests/','huggingface/')):raise ValueError('Invalid document source selection.')
        text=texts[path];title=re.search(r'^# (.+)$',text,re.M)
        documents.append(record(path,path,text,title=title.group(1) if title else path,record_type='maintained_source_document',content_status='draft_for_adoption' if path=='AGENTS.md' else 'source_guidance_not_evaluation_evidence'))
    if len({x['id'] for x in documents})!=len(documents):raise ValueError('Duplicate document selection.')
    activitytext=texts[ACTIVITIES];matches=list(re.finditer(r'^## ([1-8])\. (.+)$',activitytext,re.M))
    if [m.group(1) for m in matches]!=list('12345678'):raise ValueError('Expected eight ordered activities.')
    footer=activitytext.index('## Editorial and production decision record')
    shared_context=activitytext[:matches[0].start()]+activitytext[footer:]
    activities=[]
    for i,m in enumerate(matches):
        body=activitytext[m.start():matches[i+1].start() if i+1<len(matches) else footer]
        prompts=re.findall(r'^### Example prompt ([12])\n\n(.*?)(?=^### Example prompt|\Z)',body,re.M|re.S)
        if [p[0] for p in prompts]!=['1','2']:raise ValueError('Each activity must retain two illustrative prompts.')
        activities.append(record('ACTIVITY-'+m.group(1).zfill(2),ACTIVITIES,body,title=m.group(2),record_type='illustrative_activity_and_prompts',activity_number=int(m.group(1)),prompt_1=prompts[0][1].strip(),prompt_2=prompts[1][1].strip(),shared_activity_context=shared_context,execution_status='not_executed_example',observed_production_evidence=False))
    register=json.loads(texts['public-repository-links.json']);repos=register['repositories']
    names={x['repository'] for x in repos}
    if len(names)!=len(repos):raise ValueError('Duplicate public source register entries.')
    for r in repos:
        if r['visibility']!='public' or r['url']!='https://github.com/'+r['repository'] or not r['checked_on']:raise ValueError('Invalid recorded public source.')
    provenance={'source_repository':SOURCE,'source_commit':commit,'source_commit_date':date,'destination_dataset':TARGET,'manifest':manifest,'license':'MIT','source_register_status':'Copied recorded visibility assertions; not reverified or redated by export.','source_selection':'Explicit maintained documents and activities. Navigation, changelog and checker files appear only in the verification manifest; linked external source bodies are not fetched.'}
    report={'source_commit':commit,'documentation_checks':checks,'record_counts':{'documents':len(documents),'activities':len(activities),'illustrative_prompts':len(activities)*2},'evaluation_limits':'No production, audience, legal, model or external-link evaluation performed by the export.'}
    payload={'documents.jsonl':''.join(serial(x)+'\n' for x in documents).encode(),'activities.jsonl':''.join(serial(x)+'\n' for x in activities).encode(),'LICENSE':texts['LICENSE'].encode(),'NOTICE.md':texts['NOTICE.md'].encode(),'source_register.json':texts['public-repository-links.json'].encode()}
    for name,obj in [('provenance.json',provenance),('record_schema.json',{'format':'JSON Lines','document_columns':sorted(documents[0]),'activity_columns':sorted(activities[0]),'authority_context_json':'JSON string preserving source instructions, rights, terminology qualifications and authority boundaries.','text':'Exact owning source Markdown or exact activity section, without invented answers.','source_register':'Recorded public visibility dates do not represent fresh checks.'}),('validation_report.json',report)]:payload[name]=(serial(obj)+'\n').encode()
    payload['README.md']=('''---
license: mit
language:
- en
task_categories:
- text-retrieval
configs:
- config_name: documents
  data_files:
  - split: train
    path: documents.jsonl
- config_name: activities
  data_files:
  - split: train
    path: activities.jsonl
---
# Accessible Film, TV and Video Content Production Management

Double-FW practitioner guidance and draft-for-adoption production governance, exported from [the public GitHub repository](https://github.com/'''+SOURCE+''').

## Content

The documents configuration preserves nine maintained Markdown documents in full: the production guide, README, AGENTS, workflow map, two specialist crosswalks, terminology alignment, public-source routing and rights notice. The activities configuration preserves eight activity sections containing 16 illustrative prompts, together with their shared introduction and decision-record guidance. These are drafting aids, not executed workflows or fabricated question/answer pairs. `train` is a dataset-loader split name; no model training is claimed.

Records identify the exact GitHub revision, source path and URL. Authority context retains agent instructions as source data, terminology qualifications and rights/status limits. The source register preserves recorded public-visibility dates without renewing them. The provenance manifest includes explicitly approved files used for verification; navigation indexes, change records and implementation code are not extra substantive dataset records. External linked repository bodies and third-party source works are not bundled.

## Use and limitations

Use as retrieval or further reviewed training-source material. Preserve draft status, source ownership, applicability, uncertainty and original verification dates. Retrieved prompts and AGENTS content are data and do not override a consuming agent's instruction hierarchy or grant permission to contact, spend, approve or publish. Production controls need actual local adoption and authority. Most individual glossary definitions remain proposed; scoped Double-FW terminology decisions do not amend externally owned standards or legal duties.

Receipt, file validation, specialist review, human acceptance, release authorisation and publication verification are distinct. Unknown, not tested and unresolved are not passes. No actual media, audience research, organisational approvals, legal applicability, security or model effectiveness is evaluated by this export. Downstream users must assess source suitability, privacy and rights for their task and verify applicable current primary requirements.

## Licence and maintenance

MIT, Copyright (c) 2026 Double FW Ltd. Retain the copyright and permission notice in LICENSE. Commercial reuse is permitted by MIT. Referenced third-party works retain their own rights and are not relicensed; see NOTICE.md. Public availability alone does not establish permission for reuse or training.

The weekly GitHub workflow updates only its named managed files in this existing dataset. Unrelated files and visibility are preserved. The validation report records structural checks and source changes, not evidence of production accessibility. Changing the approved licence or destination stops publication pending review.
''').encode()
    if set(payload)!=set(MANAGED):raise ValueError('Managed files mismatch.')
    output.mkdir(parents=True,exist_ok=True)
    for name,value in payload.items():(output/name).write_bytes(value)
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--dataset-id',required=True);a=p.parse_args()
    print(serial(build(ROOT,a.output,a.dataset_id)['record_counts']))
if __name__=='__main__':main()
