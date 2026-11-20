import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from export_huggingface import build
from publish_huggingface import publish
from media_hf_common import MANAGED,SOURCE,TARGET
from huggingface_hub.errors import EntryNotFoundError

class FakeHub:
    def __init__(self,root):self.files={'.gitattributes':b'preserve me','unrelated.md':b'preserve me too'};self.parent='destination-parent';self.commits=[];self.root=root;self.reject_concurrent=False
    def repo_info(self,**kwargs):return SimpleNamespace(sha=self.parent)
    def download(self,filename,**kwargs):
        if filename not in self.files:raise EntryNotFoundError('Missing test file')
        path=self.root/'old'/filename;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(self.files[filename]);return str(path)
    def create_commit(self,**kwargs):
        if self.reject_concurrent or kwargs['parent_commit']!=self.parent:raise RuntimeError('Concurrent destination change')
        self.commits.append(kwargs)
        for op in kwargs['operations']:self.files[op.path_in_repo]=op.path_or_fileobj
        self.parent='next-destination-parent'

class MediaExport(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.work=Path(self.tmp.name);self.root=self.work/'source';self.output=self.work/'export'
        subprocess.run(['git','clone','--quiet','--no-hardlinks',str(ROOT),str(self.root)],check=True)
    def tearDown(self):self.tmp.cleanup()
    def rows(self,name):return [json.loads(l) for l in (self.output/name).read_text().splitlines()]
    def preview(self):return build(self.root,self.output)
    def publish(self,hub,**kw):return publish(self.output,'test-token-not-a-real-credential',source_root=self.root,api=hub,download=hub.download,check_public=lambda:None,**kw)
    def commit(self):
        subprocess.run(['git','-C',str(self.root),'-c','user.name=Test','-c','user.email=test@example.invalid','add','-A'],check=True)
        subprocess.run(['git','-C',str(self.root),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','Fixture change'],check=True)
    def test_documents_are_exact_and_keep_authority_context(self):
        report=self.preview();self.assertEqual(9,report['record_counts']['documents'])
        for r in self.rows('documents.jsonl'):
            self.assertEqual((self.root/r['source_path']).read_text(),r['text']);ctx=json.loads(r['authority_context_json']);self.assertIn('draft',ctx['qualification'].lower());self.assertIn('Unknown',ctx['terminology_alignment'])
    def test_all_activities_and_prompts_preserved_without_execution_claim(self):
        report=self.preview();self.assertEqual(8,report['record_counts']['activities']);self.assertEqual(16,report['record_counts']['illustrative_prompts'])
        for r in self.rows('activities.jsonl'):
            self.assertIn('### Example prompt 1',r['text']);self.assertIn('### Example prompt 2',r['text']);self.assertTrue(r['prompt_1']);self.assertTrue(r['prompt_2']);self.assertFalse(r['observed_production_evidence']);self.assertEqual('not_executed_example',r['execution_status']);self.assertIn('Editorial and production decision record',r['shared_activity_context'])
    def test_recorded_source_dates_are_not_replaced(self):
        self.preview();self.assertEqual((self.root/'public-repository-links.json').read_bytes(),(self.output/'source_register.json').read_bytes())
        paths={r['source_path'] for r in self.rows('documents.jsonl')};self.assertFalse(any('/RAG_Reference' in p or 'CHANGELOG' in p for p in paths))
    def test_deleted_review_report_is_not_required_or_restored(self):
        self.preview();self.assertFalse((self.root/'REVIEW_2026-11-20.md').exists())
    def test_missing_owning_source_fails_documentation_check(self):
        p=self.root/'Production_and_Captions_Mapping.md';p.unlink();self.commit()
        with self.assertRaisesRegex(ValueError,'committed regular file'):self.preview()
    def test_same_revision_is_deterministic(self):
        self.preview();other=self.work/'second';build(self.root,other)
        for n in MANAGED:self.assertEqual((self.output/n).read_bytes(),(other/n).read_bytes())
    def test_dirty_canonical_source_stops_export(self):
        p=self.root/'Accessible_TV_Content_Guidance_for_Production_Teams.md';p.write_text(p.read_text()+'\n')
        with self.assertRaisesRegex(ValueError,'Working source differs'):self.preview()
    def test_missing_committed_required_source_stops_export(self):
        (self.root/'Accessible_TV_Content_Guidance_for_Production_Teams.md').unlink();self.commit()
        with self.assertRaisesRegex(ValueError,'committed regular file'):self.preview()
    def test_changed_licence_stops_export(self):
        p=self.root/'LICENSE';p.write_text(p.read_text()+'\nChanged licence.\n');self.commit()
        with self.assertRaisesRegex(ValueError,'Licence bytes changed'):self.preview()
    def test_wrong_destination_stops_before_publish(self):
        self.preview();hub=FakeHub(self.work)
        with self.assertRaisesRegex(ValueError,'HF_DATASET_ID'):self.publish(hub,dataset_id='GarethFW/wrong')
        self.assertEqual([],hub.commits)
    def test_modified_export_cannot_publish_even_if_report_is_present(self):
        self.preview();p=self.output/'documents.jsonl';p.write_text(p.read_text()+'\n');hub=FakeHub(self.work)
        with self.assertRaisesRegex(ValueError,'Export bytes differ'):self.publish(hub)
        self.assertEqual([],hub.commits)
    def test_first_publish_is_atomic_and_preserves_other_files(self):
        self.preview();hub=FakeHub(self.work);self.publish(hub)
        self.assertEqual(1,len(hub.commits));self.assertEqual('destination-parent',hub.commits[0]['parent_commit'])
        self.assertEqual(set(MANAGED),{o.path_in_repo for o in hub.commits[0]['operations']});self.assertEqual(b'preserve me',hub.files['.gitattributes'])
    def test_repeat_publish_does_not_clear_historical_report_with_extra_commit(self):
        self.preview();hub=FakeHub(self.work);self.publish(hub);result=self.publish(hub)
        self.assertIn('No changes',result);self.assertEqual(1,len(hub.commits))
    def test_foreign_destination_provenance_is_not_overwritten(self):
        self.preview();hub=FakeHub(self.work);hub.files['provenance.json']=b'{"source_repository":"another/source"}'
        with self.assertRaisesRegex(ValueError,'different source'):self.publish(hub)
        self.assertEqual([],hub.commits)
    def test_concurrent_destination_change_is_not_blindly_retried(self):
        self.preview();hub=FakeHub(self.work);hub.reject_concurrent=True
        with self.assertRaisesRegex(RuntimeError,'Concurrent'):self.publish(hub)
        self.assertEqual([],hub.commits)
    def test_private_source_failure_prevents_destination_write(self):
        self.preview();hub=FakeHub(self.work)
        def private():raise ValueError('Source is private')
        with self.assertRaisesRegex(ValueError,'private'):publish(self.output,'test-token',source_root=self.root,api=hub,download=hub.download,check_public=private)
        self.assertEqual([],hub.commits)
    def test_whitespace_token_is_rejected_without_echoing_it(self):
        self.preview();token=' accidental-sensitive-token\n'
        with self.assertRaises(ValueError) as raised:publish(self.output,token,source_root=self.root,check_public=lambda:None)
        self.assertNotIn(token.strip(),str(raised.exception))

class PublicSourceCheck(unittest.TestCase):
    def test_uses_workflow_github_token_for_github_request(self):
        from unittest.mock import patch
        from io import BytesIO
        from media_hf_common import public_source
        info={'full_name':SOURCE,'private':False,'visibility':'public'}
        with patch.dict('os.environ',{'GITHUB_TOKEN':'synthetic-github-token'}),patch('urllib.request.urlopen',return_value=BytesIO(json.dumps(info).encode())) as call:
            public_source()
            request=call.call_args.args[0]
            self.assertEqual('https://api.github.com/repos/'+SOURCE,request.full_url)
            self.assertEqual('Bearer synthetic-github-token',request.get_header('Authorization'))
    def test_http_error_identifies_source_check_without_sensitive_body(self):
        from unittest.mock import patch
        from io import BytesIO
        from urllib.error import HTTPError
        from media_hf_common import public_source
        failure=HTTPError('https://api.github.com/repos/'+SOURCE,403,'sensitive response detail',{},BytesIO(b'private response body'))
        with patch('urllib.request.urlopen',side_effect=failure):
            with self.assertRaisesRegex(ValueError,r'Public GitHub source verification failed \(HTTP 403\)') as raised:public_source()
        self.assertNotIn('sensitive',str(raised.exception));self.assertNotIn('private response body',str(raised.exception))
    def test_authenticated_private_source_is_still_blocked(self):
        from unittest.mock import patch
        from io import BytesIO
        from media_hf_common import public_source
        info={'full_name':SOURCE,'private':True,'visibility':'private'}
        with patch.dict('os.environ',{'GITHUB_TOKEN':'synthetic-github-token'}),patch('urllib.request.urlopen',return_value=BytesIO(json.dumps(info).encode())):
            with self.assertRaisesRegex(ValueError,'approved public'):public_source()

if __name__=='__main__':unittest.main()
