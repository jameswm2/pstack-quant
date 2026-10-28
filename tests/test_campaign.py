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

    def test_null_close_rejected_without_publication(self):
        head=c.view(self.root,self.now)['head']
        with self.assertRaises(e.Invalid): self.close(assignment=None)
        self.assertEqual(c.view(self.root,self.now)['head'],head)

    def test_internal_keys_are_disjoint_from_public_keys(self):
        self.direction(); self.assign(); path=self.plan(); plan=e.load(path)
        for prefix in ('reserve-', 'register-'):
            self.put({'kind':'direction','key':prefix+plan['study']['id']+'--'+plan['id'],
                      'id':prefix+'variant','family':'timing','parent':'d1','claim':'Variant','predictions':'Test',
                      'disconfirmers':'Null','rationale':'Refine','scope':['timing'],'state':'unexplored'})
        packet=c.trial(self.root,'a1',path,self.now)
        self.assertEqual(packet['charged_trials'],1)
        self.assertFalse(packet['pending_registrations'])

    def test_compound_trial_identity(self):
        self.direction(); self.assign(trials=2); path=self.plan(); plan=e.load(path)
        for study, trial in [('alpha--beta','gamma'),('alpha','beta--gamma')]:
            plan['study']['id']=study; plan['id']=trial; path.write_bytes(e.canonical(plan))
            c.trial(self.root,'a1',path,self.now)
            c.trial(self.root,'a1',path,self.now)
        self.assertEqual(c.view(self.root,self.now)['charged_trials'],2)

    def test_child_preflight_rejections_do_not_charge_or_freeze(self):
        self.direction(); self.assign(trials=3); path=self.plan(); plan=e.load(path)
        plan['study']['budget']['max_trials']=1; path.write_bytes(e.canonical(plan))
        c.trial(self.root,'a1',path,self.now)
        original=copy.deepcopy(plan)
        for change in ('protocol','slots','trial'):
            plan=copy.deepcopy(original)
            if change == 'protocol': plan['study']['question']='Incompatible question'; plan['id']='other'
            elif change == 'slots': plan['id']='other'
            else: plan['hypothesis']='Incompatible same-ID hypothesis'
            path.write_bytes(e.canonical(plan)); head=c.view(self.root,self.now)['head']
            with self.assertRaises(e.Invalid): c.trial(self.root,'a1',path,self.now)
            packet=c.view(self.root,self.now)
            self.assertEqual(packet['head'],head)
            self.assertEqual(packet['charged_trials'],1)
            self.assertFalse(packet['pending_registrations'])
            self.assertEqual(len(list((self.root/'plans').iterdir())),1)

    def test_child_slot_preflight_leaves_no_reservation(self):
        self.direction(); self.assign(trials=2); path=self.plan(); plan=e.load(path)
        plan['study']['budget']['max_trials']=1; path.write_bytes(e.canonical(plan))
        c.trial(self.root,'a1',path,self.now)
        plan['id']='extra'; path.write_bytes(e.canonical(plan)); before=c.view(self.root,self.now)
        with self.assertRaisesRegex(e.Invalid,'trial budget exhausted'):
            c.trial(self.root,'a1',path,self.now)
        self.assertEqual(c.view(self.root,self.now)['head'],before['head'])
        self.assertEqual(len(list((self.root/'plans').iterdir())),1)

    def test_existing_unreserved_trial_preflight_rejects_changed_plan(self):
        self.direction(); self.assign(); path=self.plan(); plan=e.load(path)
        e.register(self.root/'studies'/plan['study']['id'],path)
        plan['hypothesis']='Changed same-ID hypothesis'; path.write_bytes(e.canonical(plan))
        before=c.view(self.root,self.now)
        with self.assertRaises(e.Invalid): c.trial(self.root,'a1',path,self.now)
        packet=c.view(self.root,self.now)
        self.assertEqual(packet['head'],before['head'])
        self.assertEqual(packet['charged_trials'],0)
        self.assertFalse((self.root/'plans').exists())

    def test_abandoned_registration_retains_charge_and_allows_other_work(self):
        self.direction(); self.assign(); path=self.plan()
        def crash(): raise RuntimeError('registration unavailable after reservation')
        with self.assertRaisesRegex(RuntimeError,'registration unavailable'):
            c.trial(self.root,'a1',path,self.now,_after_reserve=crash)
        packet=c.view(self.root,self.now); slot=packet['pending_registrations'][0]
        proposal={'kind':'abandon_registration','reservation':slot,'reason':'Unexecuted interrupted registration',
                  'evidence':[self.ref('failure','Observed post-reservation interruption; no child registration exists.')]}
        for bad in ({**proposal,'reservation':'unknown'}, {**proposal,'evidence':[]}):
            with self.assertRaises(e.Invalid): self.put(bad)
        settled=self.put(proposal)
        self.assertEqual(settled['reservations'][slot]['registration_state'],'abandoned')
        self.assertTrue((self.root/'plans'/slot/'plan.json').exists())
        self.assertEqual(c.view(self.root,self.now)['charged_trials'],1)
        self.assertFalse(c.view(self.root,self.now)['pending_registrations'])
        with self.assertRaises(e.Invalid): c.trial(self.root,'a1',path,self.now)
        self.close(execution='abandoned',outcome='not_evaluated',failure_signature='registration unavailable')
        self.assign('a2'); plan=e.load(path); plan['id']='unrelated'; path.write_bytes(e.canonical(plan))
        packet=c.trial(self.root,'a2',path,self.now)
        self.assertEqual(packet['charged_trials'],2)
        self.assertEqual(len(packet['reservations']),2)

    def test_registered_pending_reservation_cannot_be_abandoned(self):
        self.direction(); self.assign(); path=self.plan()
        def crash(): raise RuntimeError('receipt interrupted')
        with self.assertRaises(RuntimeError): c.trial(self.root,'a1',path,self.now,_after_register=crash)
        slot=c.view(self.root,self.now)['pending_registrations'][0]; head=c.view(self.root,self.now)['head']
        with self.assertRaises(e.Invalid):
            self.put({'kind':'abandon_registration','reservation':slot,'reason':'Do not erase work','evidence':[self.ref('failure')]})
        self.assertEqual(c.view(self.root,self.now)['head'],head)
        self.assertFalse(c.trial(self.root,'a1',path,self.now)['pending_registrations'])

    def test_free_text_unblock_is_rejected_before_publication(self):
        self.direction()
        self.put({'kind':'terminal','status':'externally_blocked','rationale':'No input','unresolved':'Input',
                  'next':'Await authorization','unblock':'Input authorized','routes_considered':'No useful permitted route'})
        before=c.view(self.root,self.now)
        with self.assertRaises(e.Invalid):
            self.put({'kind':'frontier','direction':'d1','state':'active','rationale':'Claimed access change',
                      'reopen':'Authorization','reversal':'Revoked','review':self.review(),'unblock_basis':'Uncited assertion'})
        self.assertEqual(c.view(self.root,self.now)['head'],before['head'])

    def test_reviewed_unblock_requires_cited_nonreview_basis(self):
        self.direction()
        self.put({'kind':'terminal','status':'externally_blocked','rationale':'No input','unresolved':'Input',
                  'next':'Await authorization','unblock':'Input authorized','routes_considered':'No useful permitted route'})
        packet=c.view(self.root,self.now)
        self.assertIn('reviewed',packet['next_action'])
        proposal={'kind':'frontier','direction':'d1','state':'active','rationale':'Access changed','reopen':'Authorization',
                  'reversal':'Access revoked','review':self.review(),'unblock_basis':'Free text assertion'}
        with self.assertRaises(e.Invalid): self.put(proposal)
        proposal.pop('key'); proposal['unblock_basis']=e.digest(e.canonical(proposal['review']))
        with self.assertRaises(e.Invalid): self.put(proposal)
        proposal.pop('key'); basis=self.ref('authorization','Fixture permission changed')
        proposal['evidence'].append(basis); proposal['unblock_basis']=basis['sha256']
        reopened=self.put(proposal)
        self.assertEqual(reopened['status'],'open')
        self.assertEqual(reopened['charter'],packet['charter'])
        self.assertEqual(reopened['charged_trials'],packet['charged_trials'])

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

    def test_same_family_checkpoint_cannot_launder_fixation(self):
        self.direction(); self.assign(); self.close(information_gain=False)
        self.assign('a2'); self.close(information_gain=False)
        with self.assertRaises(e.Invalid):
            self.put({'kind':'frontier','direction':'d1','selected_direction':'d1','state':'active','reopen':'New evidence','rationale':'Continue','reversal':'Failure','review':self.review(),'evidence':[self.ref('launder')]})
        self.assertIn('no_information',c.view(self.root,self.now)['review_due'])

    def test_early_checkpoint_cannot_reset_family_run(self):
        self.direction(); self.assign(); self.close()
        self.put({'kind':'frontier','direction':'d1','state':'active','rationale':'Premature routine checkpoint','reopen':'New evidence','reversal':'Confound','review':self.review(),'evidence':[self.ref('early-checkpoint')]})
        self.assign('a2'); self.close()
        self.assertIn('same_family',c.view(self.root,self.now)['review_due'])
        with self.assertRaises(e.Invalid): self.assign('a3')

    def test_diagnosis_failure_tracks_family_and_needs_material_repair(self):
        spec=charter(); spec['triggers']={k:100 for k in spec['triggers']}; spec['triggers']['failures']=2
        other=self.root/'diagnostic'; c.start(other,spec,self.now)
        self.root=other
        self.direction(); self.direction('variant','timing','d1')
        self.assign(); self.close(execution='failed',outcome='not_evaluated',failure_signature='input')
        self.assign('a2',direction='variant'); self.close(execution='failed',outcome='not_evaluated',failure_signature='input')
        exception={'seconds':3600,'trials':1,'discriminator':'Input health','neglected_value':'Other family infeasible','reversal':'Diagnostic fails'}
        self.assign('diag',action='diagnose',trials=0,review=self.review(),depth_exception=exception,evidence=[self.ref('diag')])
        self.close(execution='failed',outcome='not_evaluated',failure_signature='input')
        for kwargs in ({'action':'diagnose'},{'action':'refine','repair_basis':'renamed'}):
            with self.assertRaises(e.Invalid): self.assign('again',direction='variant',review=self.review(),depth_exception=exception,material_basis='a'*64,evidence=[self.ref('same')],**kwargs)
        basis=self.ref('repair','Fixture changed parser demonstrated against failed input')
        self.assign('repaired',direction='variant',action='refine',review=self.review(),depth_exception=exception,material_basis=basis['sha256'],repair_basis=basis['sha256'],evidence=[basis])

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

    def test_budget_status_requires_actual_boundary(self):
        with self.assertRaises(e.Invalid):
            self.put({'kind':'terminal','status':'budget_exhausted','rationale':'Arbitrary stop','unresolved':'Everything','next':'Report'})
        self.assertEqual(c.view(self.root,self.now)['status'],'open')

    def test_global_trial_reserve_and_failed_charges(self):
        spec=charter(); spec['trial_limit']=3
        other=self.root/'small'; c.start(other,spec,self.now); self.root=other
        self.direction(); self.assign(trials=2)
        path=self.plan(); c.trial(self.root,'a1',path,self.now)
        plan=e.load(path); plan['id']='t002'; path.write_bytes(e.canonical(plan)); c.trial(self.root,'a1',path,self.now)
        self.close(execution='abandoned',outcome='not_evaluated',failure_signature='fixture stop')
        self.assertEqual(c.view(self.root,self.now)['charged_trials'],2)
        with self.assertRaises(e.Invalid): self.assign('a2',trials=1)
        self.assign('replication',action='replicate',trials=1)
        plan['id']='t003'; path.write_bytes(e.canonical(plan)); packet=c.trial(self.root,'replication',path,self.now)
        self.assertEqual(packet['charged_trials'],3); self.assertEqual(packet['remaining_trials'],0)

    def test_sequence_gap_is_not_truncated(self):
        self.direction()
        (self.root/'events/000001').rename(self.root/'events/000002')
        with self.assertRaises(e.Invalid): c.view(self.root,self.now)

    def test_concurrent_expected_head_writers(self):
        root=self.root/'concurrent'; c.start(root,charter())
        head=c.view(root)['head']; paths=[]
        for i in range(2):
            p={'kind':'terminal','key':f'handoff{i}','status':'host_needs_continuation','rationale':'Host boundary','unresolved':'Research pending','next':'Resume same ledger'}
            path=self.root/f'writer{i}.json'; path.write_bytes(e.canonical(p)); paths.append(path)
        processes=[subprocess.Popen([sys.executable,str(ROOT/'tools/campaign.py'),'commit',str(root),'--proposal',str(path),'--expect',head],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for path in paths]
        codes=[]
        for process in processes:
            process.communicate(); codes.append(process.returncode)
        self.assertEqual(sorted(codes),[0,2]); self.assertEqual(len(c.replay(root).records),1)

    def test_early_synthesis_and_adequacy_requires_review(self):
        self.direction(); self.assign(action='synthesize',trials=0); self.close()
        proposal={'kind':'terminal','status':'complete','rationale':'Adequate fixture synthesis','unresolved':'Explicit fixture limits','next':'Report'}
        with self.assertRaises(e.Invalid): self.put(proposal)
        proposal.pop('key'); proposal['review']=self.review()
        with self.assertRaises(e.Invalid): self.put(proposal)
        proposal.pop('key')
        self.put({'kind':'frontier','direction':'d1','state':'active','rationale':'All original fixture questions adjudicated','reopen':'New evidence','reversal':'Contradiction','coverage':['timing','compensation'],'coverage_status':'resolved','review':self.review(),'evidence':[self.ref('adequacy')]})
        proposal['review']=self.review(); proposal['completion_assessment']='Explicit assessment against frozen completion question'; proposal['evidence']=[self.ref('synthesis')]
        self.put(proposal)
        self.assertEqual(c.view(self.root,self.now)['status'],'complete')
        self.assertGreater(c.view(self.root,self.now)['remaining_wall_seconds'],0)

    def test_blocked_direction_allows_alternative_and_coverage_survives(self):
        self.direction(); self.direction('d2','compensation')
        self.put({'kind':'frontier','direction':'d1','state':'parked','rationale':'Reviewer unavailable','reopen':'Independent reviewer becomes available','reversal':'Different test possible'})
        self.assign(direction='d2'); self.close()
        self.put({'kind':'frontier','direction':'d2','state':'active','rationale':'Fixture scope challenged','reopen':'New evidence','reversal':'Confound discovered','coverage':['compensation'],'coverage_status':'contested','review':self.review(),'evidence':[self.ref('scope')]})
        packet=c.view(self.root,self.now)
        self.assertEqual(packet['coverage']['compensation']['status'],'contested')
        self.assertTrue(packet['decisions']); self.assertIn(str(self.root),packet['continuation_prompt'])

    def test_reservation_plan_corruption_and_pending_resume_command(self):
        self.direction(); self.assign(); path=self.plan()
        def crash(): raise RuntimeError('fixture crash')
        with self.assertRaises(RuntimeError): c.trial(self.root,'a1',path,self.now,_after_reserve=crash)
        packet=c.view(self.root,self.now); self.assertIn('trial',packet['next_command'])
        frozen=next((self.root/'plans').glob('*/plan.json')); frozen.write_text('{}')
        with self.assertRaises(e.Invalid): c.view(self.root,self.now)

    def test_real_cli_reopen(self):
        path=self.root/'charter-input.json'; path.write_bytes(e.canonical(charter()))
        target=self.root/'cli'
        for args in [('start',str(target),'--charter',str(path)),('view',str(target),'--json')]:
            result=subprocess.run([sys.executable,str(ROOT/'tools/campaign.py'),*args],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            packet=json.loads(result.stdout)
            self.assertEqual(packet['charged_trials'],0)


if __name__ == '__main__': unittest.main()
