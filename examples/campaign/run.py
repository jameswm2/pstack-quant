#!/usr/bin/env python3
"""Accelerated educational campaign. Every review is an explicit fixture, not model validation."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys

PLUGIN = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PLUGIN / 'tools'))
import campaign as c
import evidence as e
sys.path.insert(0, str(PLUGIN / 'examples/synthetic'))
import run as synthetic


def simulate(root):
    now = datetime(2000, 1, 1, tzinfo=timezone.utc)
    charter = e.load(Path(__file__).with_name('charter.json'))
    c.start(root, charter, now)
    number = 0

    def artifact(name, value):
        path = root / 'work' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(e.canonical(value))
        return {'path':str(path.relative_to(root)), 'sha256':e.digest(path.read_bytes())}

    def put(p, reviewed=False):
        nonlocal number
        number += 1
        p['key'] = f'example-{number}'
        if reviewed:
            review = {'head':c.view(root,now)['head'],'reviewer':'EDUCATIONAL-FIXTURE-NOT-AN-AGENT','verdict':'accept','rationale':'Fixture tests ledger mechanics only','alternatives':'Timing falsification, compensation audit, synthesis','neglected_scope':'Compensation remains open'}
            p['review'] = review
            p.setdefault('evidence',[]).append(artifact(f'review-{number}.json',review))
        return c.commit(root,p,c.view(root,now)['head'],now)

    def direction(id, family):
        put({'kind':'direction','id':id,'family':family,'parent':None,'claim':f'{family} mechanism','predictions':'A discriminating observation changes interpretation','disconfirmers':'Prediction absent under valid test','rationale':'Educational mission coverage','scope':[family],'state':'unexplored'},True)

    def assign(id, direction, seconds, trials=0, action='deepen', **extra):
        p={'kind':'assign','id':id,'direction':direction,'action':action,'seconds':seconds,'trials':trials,'question':'Which mechanism explains the fixture?','evidence_needed':'Private fixture diagnostic and study inspection','stop':'One bounded diagnostic or cap','decision_change':'Retire, refine, or preserve uncertainty','alternative':'Other family with lower current feasibility','diagnostic':'Check input availability','synthesis':'Would leave an important discriminator unresolved','rationale':'Chosen observation can change interpretation','reversal':'Invalid diagnostic or stronger alternative'}
        p.update(extra); put(p, bool(p.get('depth_exception')))

    def close(execution='completed', outcome='inconclusive', information=True, material=False, **extra):
        p={'kind':'close','assignment':c.view(root,now)['current'],'execution':execution,'outcome':outcome,'summary':'Educational fixture result; no real market inference','next':'Compare frontier against original mission','information_gain':information,'material':material,'active_minutes':1,'evidence':[artifact(f'closure-{number}.json',{'fixture':True,'execution':execution,'outcome':outcome})]}
        p.update(extra); put(p)

    direction('timing','timing'); direction('compensation','compensation')
    assign('timing-test','timing',7200,1)
    plan=synthetic.make_plan(e.digest(e.canonical({'rows':synthetic.development_rows()})))
    plan_ref=artifact('plan.json',plan)
    c.trial(root,'timing-test',root/plan_ref['path'],now)
    now += timedelta(hours=2)
    close(information=False)
    assign('repair-attempt','timing',1800,action='diagnose')
    now += timedelta(minutes=30)
    close(execution='failed',outcome='not_evaluated',information=False,failure_signature='fixture missing input')
    put({'kind':'frontier','direction':'timing','state':'parked','selected_direction':'compensation','rationale':'Unchanged execution problem; useful alternative exists','reopen':'New validated fixture input','reversal':'Alternative infeasible'},True)
    assign('compensation-audit','compensation',900)
    now += timedelta(minutes=15)
    close()
    put({'kind':'frontier','direction':'compensation','state':'retired','rationale':'Educational negative diagnostic rejects its premise; this is not a scientific financial outcome','reopen':'New mechanism or changed evidence','reversal':'Valid contradictory observation','coverage':['compensation'],'coverage_status':'unsupported','evidence':[artifact('negative-diagnostic.json',{'fixture':True,'negative_diagnostic':'Compensation prediction absent in educational dossier'})]},True)
    put({'kind':'frontier','direction':'timing','state':'active','rationale':'Fixture repaired inputs permit falsification','reopen':'Validated input available','reversal':'Input validation fails'})
    # Two routine same-family commitments trigger a real gate; this exception grants one bounded unit.
    assign('short-check','timing',1800); now += timedelta(minutes=30); close(information=False)
    assign('short-check-2','timing',600); now += timedelta(minutes=10); close(information=False)
    basis=artifact('live-discriminator.json',{'fixture':True,'new_observation':'Repair creates an identifiable timing discriminator'})
    assign('depth-test','timing',14400,depth_exception={'seconds':14400,'trials':0,'discriminator':'Repaired timing falsifier','neglected_value':'Compensation premise retired in fixture','reversal':'No separating observation'},evidence=[basis])
    now += timedelta(hours=4); close()
    now = datetime(2000,1,1,tzinfo=timezone.utc)+timedelta(hours=19)
    try:
        assign('too-late','timing',3600)
        raise AssertionError('protected reserve was spent')
    except e.Invalid:
        pass
    assign('synthesis','timing',3600,action='synthesize')
    now += timedelta(hours=1); close()
    put({'kind':'terminal','status':'budget_exhausted','rationale':'Simulated twenty-hour wall ceiling includes host downtime','unresolved':'Timing claim lacks real independent scientific review','next':'Partial educational report'})
    packet=c.view(root,now)
    assert packet['remaining_wall_seconds']==0 and packet['charged_trials']==1
    assert not next(iter(packet['studies'].values()))['complete']
    return {'simulation':True,'reviews':'EDUCATIONAL FIXTURES ONLY','host_uptime_validated':False,'head':packet['head'],'charged_trials':packet['charged_trials'],'remaining_wall_seconds':packet['remaining_wall_seconds'],'status':packet['status'],'scientific_gates':'blocked; no real reviewers or market finding','coverage':packet['coverage']}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: python3 examples/campaign/run.py NEW_OUTPUT_ROOT')
    output=Path(sys.argv[1]).absolute()
    if output.exists(): raise SystemExit('choose a new output root; simulation preserves its immutable history')
    print(json.dumps(simulate(output),indent=2))
