import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import campaign as c
import evidence as e
sys.path.insert(0, str(ROOT / 'examples/synthetic'))
import run as example


def charter():
    return {'schema':1,'mission':'Compare timing and compensation mechanisms','scope':['timing','compensation'],'completion':'Discriminate plausible mechanisms and expose uncertainty','resources':{'data':'synthetic local only','compute':'local CPU'},'coordinator':'owner','wall_seconds':72000,'trial_limit':8,'reserve_seconds':7200,'reserve_trials':1,'triggers':{'units':3,'same_family':2,'no_information':2,'failures':2,'active_minutes':30}}


class Campaign(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'campaign'; self.now = datetime(2030,1,1,tzinfo=timezone.utc)
        c.start(self.root, charter(), self.now)

    def ref(self, name='evidence', content='Educational fixture, not a real independent review.'):
        path = self.root / 'work' / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
        return {'path':str(path.relative_to(self.root)), 'sha256':e.digest(path.read_bytes())}

    def review(self):
        return {'head':c.view(self.root,self.now)['head'],'reviewer':'independent-fixture','rationale':'Fixture challenge','alternatives':'Compare compensation diagnostic','neglected_scope':'Compensation remains unresolved','verdict':'accept'}

    def put(self,p):
        if p.get('review'):
            r=p['review']; ref=self.ref('review-'+str(len(c.replay(self.root).records)),e.canonical(r).decode())
            p.setdefault('evidence',[]).append(ref)
        p.setdefault('key', f'op{len(c.replay(self.root).records)}')
        return c.commit(self.root,p,c.view(self.root,self.now)['head'],self.now)

    def direction(self,id='d1',family='timing',parent=None):
        p={'kind':'direction','id':id,'family':family,'parent':parent,'claim':'Timing causes effect','predictions':'Timing separation removes effect','disconfirmers':'Effect persists','rationale':'Mission mechanism','scope':['timing'],'state':'unexplored','evidence':[self.ref(id)]}
        if not parent: p['review']=self.review()
        return self.put(p)

    def assign(self,id='a1',direction='d1',**extra):
        p={'kind':'assign','id':id,'direction':direction,'action':'deepen','seconds':3600,'trials':1,'question':'Does effect survive timing split?','evidence_needed':'Sealed diagnostic','stop':'Stop after one trial or failed input validation','decision_change':'Retire or refine timing account','alternative':'Compensation family, lower feasibility','diagnostic':'Input availability audit','synthesis':'Early synthesis leaves timing unanswered','rationale':'Discriminator is feasible','reversal':'Failed timing audit'}
        p.update(extra); return self.put(p)

    def close(self,**extra):
        p={'kind':'close','assignment':c.view(self.root,self.now)['current'],'execution':'completed','outcome':'inconclusive','summary':'Uncertain fixture finding','next':'Compare alternatives','information_gain':True,'material':False,'active_minutes':1,'evidence':[self.ref()]}
        p.update(extra); return self.put(p)

    def plan(self):
        plan=example.make_plan(e.digest(e.canonical({'rows':example.development_rows()})))
        path=self.root/'caller-plan.json'; path.write_bytes(e.canonical(plan)); return path

    def test_frozen_clock_budget_and_context_recovery(self):
        original=c.view(self.root,self.now)
        c.start(self.root,charter(),self.now+timedelta(hours=4))
        self.assertEqual(c.view(self.root,self.now)['charter'],original['charter'])
        self.direction(); self.assign(); self.now += timedelta(hours=2)
        self.assertTrue(c.view(self.root,self.now)['overrun']); self.close()
        self.now += timedelta(hours=17)
        with self.assertRaises(e.Invalid): self.assign('a2')
        self.assign('synthesis',action='synthesize',seconds=1800,trials=0)
        self.close(); self.now += timedelta(hours=2)
        self.assertEqual(c.view(self.root,self.now)['remaining_wall_seconds'],0)
        self.put({'kind':'terminal','status':'budget_exhausted','rationale':'Wall ceiling reached','unresolved':'Compensation','next':'Partial report'})
        self.assertEqual(c.view(self.root,self.now)['status'],'budget_exhausted')

    def test_expected_head_retry_and_conflict(self):
        old=c.view(self.root,self.now)['head']; self.direction()
        p=c.replay(self.root).records[-1]['payload']; head=c.view(self.root,self.now)['head']
        self.assertEqual(c.commit(self.root,p,old,self.now)['head'],head)
        p=copy.deepcopy(p); p['rationale']='changed'
        with self.assertRaises(e.Invalid): c.commit(self.root,p,head,self.now)
        with self.assertRaises(e.Invalid): c.commit(self.root,{'kind':'terminal','key':'new'},old,self.now)

    def test_changed_missing_evidence_and_ledger_gap(self):
        self.direction(); artifact=self.root/'work/d1'; artifact.write_text('changed')
        with self.assertRaises(e.Invalid): c.view(self.root,self.now)
        artifact.unlink()
        with self.assertRaises(e.Invalid): c.view(self.root,self.now)

    def test_backwards_clock_spending(self):
        self.direction(); self.now -= timedelta(seconds=1)
        self.assertTrue(c.view(self.root,self.now)['clock_backwards'])
        with self.assertRaises(e.Invalid): self.assign()

    def test_variant_inherits_family(self):
        self.direction()
        with self.assertRaises(e.Invalid): self.direction('variant','fake-new-family','d1')
        self.direction('variant','timing','d1')
        self.assertEqual(len({d['family'] for d in c.view(self.root,self.now)['frontier'].values()}),1)

    def test_repetition_gates_depth_and_new_material_renewal(self):
        self.direction(); self.assign(); self.close(information_gain=False)
        self.assign('a2'); self.close(information_gain=False)
        self.assertIn('same_family',c.view(self.root,self.now)['review_due'])
        with self.assertRaises(e.Invalid): self.assign('a3')
        ref=self.ref('depth','Fixture live discriminator')
        exception={'seconds':3600,'trials':1,'discriminator':'Timing falsifier','neglected_value':'Alternative lacks available inputs','reversal':'Null diagnostic'}
        self.assign('a3',review=self.review(),evidence=[ref],depth_exception=exception)
        self.close()
        with self.assertRaises(e.Invalid): self.assign('a4',review=self.review(),evidence=[ref],depth_exception=exception)
        new=self.ref('new','Material fixture observation changed discriminator')
        self.assign('a4',review=self.review(),evidence=[new],material_basis=new['sha256'],depth_exception=exception)

    def test_failure_not_negative_and_diagnostic_detour(self):
        self.direction(); self.assign()
        with self.assertRaises(e.Invalid): self.close(execution='failed',outcome='negative')
        self.close(execution='failed',outcome='not_evaluated',failure_signature='same-input')
        self.assign('a2'); self.close(execution='failed',outcome='not_evaluated',failure_signature='same-input')
        self.direction('d2','compensation')
        self.put({'kind':'frontier','selected_direction':'d2','direction':'d1','state':'active','reopen':'Fresh input','rationale':'Compare repair and alternate','reversal':'Repair fails','review':self.review(),'evidence':[self.ref('checkpoint')]})
        with self.assertRaises(e.Invalid): self.assign('a3')
        self.assign('diagnosis',direction='d2',action='diagnose',trials=0)

    def test_trial_recovery_before_and_after_registration(self):
        self.direction(); self.assign(); path=self.plan()
        def crash(): raise RuntimeError('simulated interruption')
        with self.assertRaises(RuntimeError): c.trial(self.root,'a1',path,self.now,_after_reserve=crash)
        self.assertEqual(c.view(self.root,self.now)['charged_trials'],1)
        with self.assertRaises(RuntimeError): c.trial(self.root,'a1',path,self.now,_after_register=crash)
        self.assertEqual(c.view(self.root,self.now)['charged_trials'],1)
        self.now += timedelta(hours=21)
        packet=c.trial(self.root,'a1',path,self.now)
        self.assertEqual(packet['charged_trials'],1); self.assertFalse(packet['pending_registrations'])
        self.assertFalse(packet['studies'][example.make_plan('a'*64)['study']['id']]['complete'])
        self.assertEqual(c.trial(self.root,'a1',path,self.now)['charged_trials'],1)

    def test_unreserved_child_and_no_scientific_override(self):
        self.direction(); self.assign(); path=self.plan(); plan=e.load(path)
        e.register(self.root/'studies'/plan['study']['id'],path)
        self.assertTrue(c.view(self.root,self.now)['reconciliation'])
        packet=c.trial(self.root,'a1',path,self.now)
        self.assertEqual(packet['charged_trials'],1); self.assertFalse(packet['reconciliation'])
        with self.assertRaises(e.Invalid): self.close(outcome='supported')

    def test_real_cli_reopen(self):
        path=self.root/'charter-input.json'; path.write_bytes(e.canonical(charter()))
        target=self.root/'cli'
        for args in [('start',str(target),'--charter',str(path)),('view',str(target),'--json')]:
            result=subprocess.run([sys.executable,str(ROOT/'tools/campaign.py'),*args],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            packet=json.loads(result.stdout)
            self.assertEqual(packet['charged_trials'],0)


if __name__ == '__main__': unittest.main()
