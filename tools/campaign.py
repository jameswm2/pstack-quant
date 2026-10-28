#!/usr/bin/env python3
"""Durable campaign decisions for an existing host session; never launches research."""
from __future__ import annotations
import argparse
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
import sys
import evidence as e


class Kind(str, Enum):
    DIRECTION = 'direction'
    ASSIGN = 'assign'
    CLOSE = 'close'
    FRONTIER = 'frontier'
    TERMINAL = 'terminal'
    RESERVED = 'reserved'
    REGISTERED = 'registered'


@dataclass
class State:
    charter: dict
    head: str
    records: list = field(default_factory=list)
    directions: dict = field(default_factory=dict)
    assignments: dict = field(default_factory=dict)
    reservations: dict = field(default_factory=dict)
    status: str = 'open'
    current: str | None = None
    checkpoint: int = 0
    selected_direction: str | None = None


def utc() -> datetime:
    return datetime.now(timezone.utc)


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    e.require(result.tzinfo is not None and result.utcoffset() == timedelta(0), 'timestamp must be UTC')
    return result


def positive(value, label):
    e.require(type(value) is int and value > 0, f'{label} must be positive integer')
    return value


def texts(value, keys):
    for key in keys.split():
        e.text_value(value.get(key), key)


def charter(value):
    e.fields(value, 'schema mission scope completion resources coordinator wall_seconds trial_limit reserve_seconds reserve_trials triggers', 'charter')
    e.require(value['schema'] == 1, 'unsupported charter schema')
    texts(value, 'mission completion coordinator')
    e.strings(value['scope'], 'scope')
    e.require(bool(e.object_value(value['resources'], 'resources')), 'authorized resources required')
    for key in ('wall_seconds', 'trial_limit'):
        positive(value[key], key)
    for key, limit in [('reserve_seconds', 'wall_seconds'), ('reserve_trials', 'trial_limit')]:
        e.require(type(value[key]) is int and 0 <= value[key] < value[limit], 'invalid reserve')
    for key in ('units', 'same_family', 'no_information', 'failures', 'active_minutes'):
        positive(value['triggers'].get(key), key)
    return value


def refs(root, payload):
    for ref in payload.get('evidence', []):
        e.fields(ref, 'path sha256', 'evidence reference')
        path = e.safe_path(root / e.relative(ref['path']))
        e.require(path.is_file() and e.digest(path.read_bytes()) == e.sha(ref['sha256']), f'missing or changed evidence: {ref["path"]}')


def fold(state, record):
    p = record['payload']
    kind = Kind(p['kind'])
    if kind == Kind.DIRECTION:
        state.directions[p['id']] = p.copy()
    elif kind == Kind.ASSIGN:
        state.assignments[p['id']] = {**p, 'opened': record['at'], 'closed': None}
        state.current = p['id']
        state.selected_direction = None
    elif kind == Kind.CLOSE:
        state.assignments[p['assignment']]['closed'] = p
        state.current = None
    elif kind == Kind.FRONTIER:
        state.directions[p['direction']]['state'] = p['state']
        state.directions[p['direction']]['reopen'] = p['reopen']
        if p.get('review'):
            state.checkpoint = len(state.records) + 1
            state.selected_direction = p.get('selected_direction')
    elif kind == Kind.RESERVED:
        state.reservations[p['id']] = {**p, 'registered': False}
    elif kind == Kind.REGISTERED:
        state.reservations[p['id']]['registered'] = True
    elif kind == Kind.TERMINAL:
        state.status = 'open' if p['status'] == 'host_needs_continuation' else p['status']
    state.records.append(record)
    state.head = e.digest(e.canonical(record))


def replay(root: Path) -> State:
    frozen = e.load(root / 'charter/spec.json')
    charter(frozen['charter'])
    timestamp(frozen['started']); timestamp(frozen['deadline'])
    state = State(frozen, e.digest(e.canonical(frozen)))
    paths = sorted((root / 'events').glob('*')) if (root / 'events').exists() else []
    for index, path in enumerate([p for p in paths if not p.name.startswith('.pending-')], 1):
        e.require(path.name == f'{index:06d}', 'ledger sequence gap or unexpected entry')
        record = e.load(path / 'record.json')
        e.require(record['sequence'] == index and record['previous'] == state.head, 'ledger predecessor mismatch')
        e.require(record['payload_sha256'] == e.digest(e.canonical(record['payload'])), 'ledger payload mismatch')
        e.require(timestamp(record['at']) >= timestamp(state.records[-1]['at'] if state.records else frozen['started']), 'ledger clock regressed')
        e.require(not any(r['key'] == record['key'] for r in state.records), 'duplicate operation key')
        refs(root, record['payload'])
        if record['payload']['kind'] == 'reserved':
            p = record['payload']
            plan = e.parse_plan(e.load(root / 'plans' / p['id'] / 'plan.json'))
            e.require(e.digest(e.canonical(plan.value)) == p['plan_sha256'] and plan.id == p['trial'] and plan.value['study']['id'] == p['study'], 'reserved plan binding changed')
        fold(state, record)
    return state


def now_check(state, now):
    e.require(now >= timestamp(state.records[-1]['at'] if state.records else state.charter['started']), 'clock moved backwards; wait for last observed UTC before spending')


def due(state):
    c = state.charter['charter']; t = c['triggers']
    recent = state.records[state.checkpoint:]
    closed = [r['payload'] for r in recent if r['payload']['kind'] == 'close']
    assigned = [r['payload'] for r in recent if r['payload']['kind'] == 'assign' and r['payload']['action'] not in {'synthesize', 'replicate'}]
    families = [state.directions[a['direction']]['family'] for a in assigned]
    reasons = []
    if len(closed) >= t['units']: reasons.append('units')
    if families and families.count(families[-1]) >= t['same_family']: reasons.append('same_family')
    if sum(not x['information_gain'] for x in closed) >= t['no_information']: reasons.append('no_information')
    if sum(x['execution'] != 'completed' for x in closed) >= t['failures']: reasons.append('failures')
    if sum(x['active_minutes'] for x in closed) >= t['active_minutes']: reasons.append('active_minutes')
    if any(x['material'] for x in closed): reasons.append('material_evidence')
    return reasons


def reconciliation(root, state):
    issues = []
    known = {}
    for reservation in state.reservations.values():
        known[(reservation['study'], reservation['trial'])] = reservation
    studies = root / 'studies'
    if studies.exists():
        for study_root in sorted(studies.iterdir()):
            e.identifier(study_root.name); e.safe_path(study_root)
            if not (study_root / 'study/spec.json').exists():
                if any(study_root.iterdir()): issues.append(f'unexplained study root: {study_root.name}')
                continue
            study = e.parse_study(e.load(study_root / 'study/spec.json'))
            e.require(study['id'] == study_root.name, 'study root identity mismatch')
            for plan, reg in e.registrations(study_root, study):
                reservation = known.get((study['id'], plan.id))
                if reservation is None: issues.append(f'unreserved trial: {study["id"]}/{plan.id}')
                elif reservation['plan_sha256'] != reg.value['plan_sha256']: issues.append('reserved plan changed')
    for reservation in state.reservations.values():
        path = root / 'studies' / reservation['study'] / 'trials' / reservation['trial'] / 'registration.json'
        if reservation['registered'] and not path.exists(): issues.append(f'missing registered trial: {reservation["id"]}')
    return issues


def review(root, state, p, required=False):
    r = p.get('review')
    e.require(not required or r is not None, 'fresh independent exact-head challenge required')
    if r is None: return
    e.fields(r, 'head reviewer rationale alternatives neglected_scope verdict', 'review')
    e.require(r['head'] == state.head, 'review binds a stale head')
    e.require(r['reviewer'] != state.charter['charter']['coordinator'], 'reviewer must be independent')
    texts(r, 'reviewer rationale alternatives neglected_scope')
    e.require(r['verdict'] == 'accept', 'review did not accept')
    e.require(any(e.digest(e.canonical(r)) == ref['sha256'] and e.load(root / ref['path']) == r for ref in p.get('evidence', []) if ref['sha256'] == e.digest(e.canonical(r))), 'exact review artifact reference required')


def validate(root, state, p, now):
    kind = Kind(p['kind']); c = state.charter['charter']
    e.identifier(p['key']); refs(root, p)
    now_check(state, now)
    e.require(state.status == 'open', 'campaign is terminal')
    if kind in {Kind.RESERVED, Kind.REGISTERED}: raise e.Invalid('internal trial operations are not commit proposals')
    if kind == Kind.DIRECTION:
        e.identifier(p['id']); e.identifier(p['family'])
        e.require(p['id'] not in state.directions, 'direction already exists')
        texts(p, 'claim predictions disconfirmers rationale')
        e.require(set(p['scope']) <= set(c['scope']) and bool(p['scope']), 'invalid scope links')
        parent = p.get('parent')
        if parent:
            e.require(parent in state.directions and p['family'] == state.directions[parent]['family'], 'variants inherit family')
        else:
            review(root, state, p, True)
        e.require(p['state'] == 'unexplored', 'new direction must be unexplored')
    elif kind == Kind.ASSIGN:
        e.identifier(p['id'])
        e.require(state.current is None and p['id'] not in state.assignments, 'assignment conflict')
        e.require(p['direction'] in state.directions, 'unknown direction')
        e.require(state.selected_direction is None or p['direction'] == state.selected_direction or p['action'] in {'synthesize','replicate'}, 'follow reviewed frontier choice')
        e.require(state.directions[p['direction']]['state'] not in {'parked', 'retired'}, 'direction requires explicit reopening')
        e.require(p['action'] in {'deepen', 'refine', 'expand', 'pivot', 'diagnose', 'replicate', 'synthesize'}, 'unknown action')
        texts(p, 'question evidence_needed stop decision_change alternative diagnostic synthesis rationale reversal')
        positive(p['seconds'], 'seconds')
        e.require(type(p['trials']) is int and p['trials'] >= 0, 'invalid trial cap')
        end = now + timedelta(seconds=p['seconds'])
        reserve = p['action'] in {'synthesize', 'replicate'}
        e.require(end <= timestamp(state.charter['deadline']) - timedelta(seconds=0 if reserve else c['reserve_seconds']), 'assignment enters protected reserve or exceeds deadline')
        e.require(len(state.reservations) + p['trials'] <= c['trial_limit'] - (0 if reserve else c['reserve_trials']), 'assignment exceeds trial capacity or reserve')
        e.require(not reconciliation(root, state), 'unreconciled child registrations block spending')
        e.require(not any(not r['registered'] for r in state.reservations.values()), 'pending registration must be recovered first')
        if due(state) and not reserve:
            review(root, state, p, True)
            x = p.get('depth_exception')
            e.require(x is not None, 'breadth review must choose another family via frontier checkpoint or grant bounded depth exception')
            texts(x, 'discriminator neglected_value reversal')
            e.require(p['seconds'] <= positive(x['seconds'], 'exception seconds') and p['trials'] <= x['trials'], 'depth exception cap exceeded')
            old = [r['payload'] for r in state.records if r['payload'].get('depth_exception')]
            if old:
                previous = {v['sha256'] for r in old for v in r.get('evidence', [])}
                e.require(any(v['sha256'] not in previous for v in p.get('evidence', [])), 'depth renewal requires fresh material evidence')
                e.require(p.get('material_basis') in {v['sha256'] for v in p.get('evidence', []) if v['sha256'] not in previous and v['sha256'] != e.digest(e.canonical(p['review']))}, 'name new material basis distinct from review')
        failures = [a['closed'] for a in state.assignments.values() if a['direction'] == p['direction'] and a['closed'] and a['closed']['execution'] != 'completed']
        if len(failures) >= c['triggers']['failures']:
            e.require(p['action'] == 'diagnose' or p.get('repair_basis') not in {None, *[x.get('failure_signature') for x in failures]}, 'unchanged execution failure requires diagnosis or new repair basis')
    elif kind == Kind.CLOSE:
        e.require(p['assignment'] == state.current, 'not the active assignment')
        texts(p, 'summary next')
        e.require(p['execution'] in {'completed', 'failed', 'abandoned'}, 'invalid execution')
        e.require(p['outcome'] in e.OUTCOMES, 'invalid outcome')
        e.require(p['execution'] == 'completed' or p['outcome'] == 'not_evaluated', 'execution failure is not negative science')
        for key in ('information_gain', 'material'): e.require(type(p[key]) is bool, 'invalid information metadata')
        e.require(type(p['active_minutes']) is int and p['active_minutes'] >= 0, 'invalid reported active minutes')
        if p['execution'] != 'completed': texts(p, 'failure_signature')
        e.require(bool(p.get('evidence')), 'closure requires evidence')
        for reservation in state.reservations.values():
            if reservation['assignment'] == state.current and reservation['registered']:
                inspection = e.inspect(root / 'studies' / reservation['study'])
                if p['outcome'] in {'supported', 'negative'}:
                    trial = next(t for t in inspection['trials'] if t['id'] == reservation['trial'])
                    e.require(not trial['blockers'] and trial['financial_outcome'] == p['outcome'], 'study scientific gates remain blocked or outcome differs')
        if p['outcome'] in {'supported', 'negative'}:
            e.require(any(r['assignment'] == state.current and r['registered'] for r in state.reservations.values()), 'scientific outcome requires registered study evidence')
    elif kind == Kind.FRONTIER:
        e.require(state.current is None and p['direction'] in state.directions, 'frontier requires closed assignment and known direction')
        e.require(p['state'] in {'unexplored', 'active', 'parked', 'retired', 'replication_candidate'}, 'unknown direction state')
        texts(p, 'rationale reopen reversal')
        review(root, state, p, bool(p.get('coverage')) or bool(due(state)))
        if due(state):
            choice = p.get('selected_direction')
            e.require(choice in state.directions, 'breadth checkpoint must select an existing alternative direction')
            assigned = list(state.assignments.values())
            if assigned and any(trigger in due(state) for trigger in ('same_family','no_information')):
                previous_family = state.directions[assigned[-1]['direction']]['family']
                e.require(state.directions[choice]['family'] != previous_family, 'same-family continuation requires bounded depth exception on assignment')
        if p.get('coverage'):
            e.require(set(p['coverage']) <= set(c['scope']), 'unknown coverage')
    elif kind == Kind.TERMINAL:
        e.require(state.current is None, 'close active assignment before terminal decision')
        e.require(p['status'] in {'complete', 'budget_exhausted', 'externally_blocked', 'host_needs_continuation'}, 'unknown terminal status')
        texts(p, 'rationale unresolved next')
        if p['status'] == 'complete': review(root, state, p, True)
        if p['status'] == 'externally_blocked': texts(p, 'unblock routes_considered')


def append(root, state, payload, now):
    record = {'sequence': len(state.records)+1, 'previous': state.head, 'key': payload['key'], 'at': now.isoformat(), 'payload_sha256': e.digest(e.canonical(payload)), 'payload': payload}
    e.publish(root / 'events' / f'{record["sequence"]:06d}', {'record.json': e.canonical(record)})
    fold(state, record)
    return state


def start(root: Path, specification: dict, now=None):
    now = now or utc(); root = e.canonical_root(root)
    charter(specification); root.mkdir(parents=True, exist_ok=True)
    with e.register_lock(root):
        path = root / 'charter/spec.json'
        if path.exists():
            e.require(e.load(path)['charter'] == specification, 'charter is frozen')
        else:
            e.publish(root / 'charter', {'spec.json': e.canonical({'charter': specification, 'started': now.isoformat(), 'deadline': (now+timedelta(seconds=specification['wall_seconds'])).isoformat()})})
    return view(root, now)


def commit(root: Path, proposal: dict, expected: str, now=None):
    now = now or utc(); root = e.canonical_root(root)
    with e.register_lock(root):
        state = replay(root)
        matches = [r for r in state.records if r['key'] == proposal['key']]
        if matches:
            e.require(matches[0]['payload'] == proposal, 'conflicting idempotency key')
        else:
            e.require(expected == state.head, 'stale expected head')
            validate(root, state, proposal, now)
            append(root, state, proposal, now)
    return view(root, now)


def trial(root: Path, assignment: str, plan_file: Path, now=None, _after_reserve=None, _after_register=None):
    now = now or utc(); root = e.canonical_root(root)
    plan = e.parse_plan(e.load(plan_file)); study = plan.value['study']['id']
    slot = f'{study}--{plan.id}'; plan_hash = e.digest(e.canonical(plan.value))
    with e.register_lock(root):
        state = replay(root)
        r = state.reservations.get(slot)
        if r:
            e.require(r['plan_sha256'] == plan_hash and r['assignment'] == assignment, 'conflicting trial retry')
        else:
            now_check(state, now)
            e.require(state.status == 'open' and state.current == assignment, 'trial requires active assignment')
            a = state.assignments[assignment]; c = state.charter['charter']
            e.require(now < timestamp(a['opened'])+timedelta(seconds=a['seconds']) and now < timestamp(state.charter['deadline']), 'assignment expired')
            issues = reconciliation(root, state)
            own_unreserved = f'unreserved trial: {study}/{plan.id}'
            e.require(not [issue for issue in issues if issue != own_unreserved], 'unreserved child registration blocks spending')
            e.require(len([v for v in state.reservations.values() if v['assignment'] == assignment]) < a['trials'], 'assignment trial cap exhausted')
            e.require(len(state.reservations) < c['trial_limit']-(0 if a['action'] in {'synthesize','replicate'} else c['reserve_trials']), 'global trial reserve exhausted')
            r = {'kind':'reserved','key':f'reserve-{slot}','id':slot,'assignment':assignment,'study':study,'trial':plan.id,'plan_sha256':plan_hash}
            # The plan is frozen alongside the reservation, so recovery needs no mutable caller file.
            e.publish(root / 'plans' / slot, {'plan.json': e.canonical(plan.value)})
            append(root, state, r, now)
        if _after_reserve: _after_reserve()
        reg = e.register(root / 'studies' / study, root / 'plans' / slot / 'plan.json')
        if _after_register: _after_register()
        if not state.reservations[slot]['registered']:
            # Recovery records the existing charge even after its spending window closes.
            append(root, state, {'kind':'registered','key':f'register-{slot}','id':slot,'registration':reg.value}, max(now, timestamp(state.records[-1]['at'])))
    return view(root, now)


def view(root: Path, now=None):
    now = now or utc(); root = e.canonical_root(root); state = replay(root)
    c = state.charter['charter']; issues = reconciliation(root, state)
    pending = [r['id'] for r in state.reservations.values() if not r['registered']]
    backwards = now < timestamp(state.records[-1]['at'] if state.records else state.charter['started'])
    remaining = max(0, int((timestamp(state.charter['deadline'])-now).total_seconds()))
    current = state.assignments.get(state.current)
    overrun = bool(current and now > timestamp(current['opened'])+timedelta(seconds=current['seconds']))
    if state.status != 'open': action = 'report terminal decision'
    elif pending: action = 'retry trial with frozen reserved plan'
    elif issues: action = 'reconcile unreserved trials before spending'
    elif backwards: action = 'wait for last observed UTC before spending'
    elif current: action = 'close active assignment at safe boundary' if overrun or not remaining else 'execute bounded assignment then close'
    elif not remaining: action = 'final accounting and budget_exhausted decision'
    elif remaining <= c['reserve_seconds']: action = 'synthesize or replicate within remaining budget'
    elif due(state): action = 'independent frontier challenge before routine research'
    else: action = 'compare alternatives and commit bounded assignment'
    inspections = {}
    for study in {r['study'] for r in state.reservations.values() if r['registered']}:
        inspections[study] = e.inspect(root / 'studies' / study)
    return {'schema':1, 'head':state.head, 'charter':state.charter, 'status':state.status,'frontier':state.directions,'assignments':state.assignments,'current':state.current,'charged_trials':len(state.reservations),'remaining_trials':c['trial_limit']-len(state.reservations),'remaining_wall_seconds':remaining,'pending_registrations':pending,'reconciliation':issues,'review_due':due(state),'selected_direction':state.selected_direction,'overrun':overrun,'clock_backwards':backwards,'next_action':action,'studies':inspections,'staging':[str(p.relative_to(root)) for p in root.rglob('.pending-*')],'limitations':['Durable state does not provide host liveness.','Reported information gain, materiality and reviewer independence require qualitative judgment.','Campaign decisions cannot override study evidence gates.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='verb', required=True)
    for verb in ('start','view','commit','trial'):
        p = commands.add_parser(verb); p.add_argument('root', type=Path)
        if verb == 'start': p.add_argument('--charter', type=Path, required=True)
        elif verb == 'view': p.add_argument('--json', action='store_true')
        elif verb == 'commit':
            p.add_argument('--proposal', type=Path, required=True); p.add_argument('--expect', required=True)
        else:
            p.add_argument('--assignment', required=True); p.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.verb == 'start': result = start(args.root, e.load(args.charter))
        elif args.verb == 'commit': result = commit(args.root, e.load(args.proposal), args.expect)
        elif args.verb == 'trial': result = trial(args.root, args.assignment, args.plan)
        else: result = view(args.root)
        print(e.canonical(result).decode(), end=''); return 0
    except (e.Invalid, OSError, ValueError, TypeError, KeyError) as exc:
        print(f'INVALID: {exc}', file=sys.stderr); return 2


if __name__ == '__main__':
    raise SystemExit(main())
