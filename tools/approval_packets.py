"""Apply a human's approval file on a branch, after validating the complete result.

The file is a request, not proof of identity. The owner identifies its human
author, registers that reviewer and reviews the resulting pull request.
"""

import copy
import datetime
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

from tools import check, review_hash, review_rules, writing

PACKET_FIELDS = {'version', 'commit', 'reviewer', 'on', 'decisions'}
DECISION_FIELDS = {'thing', 'field', 'seen', 'verdict', 'cuisine', 'sources', 'note', 'attested'}


def exact_fields(value, fields, label):
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError('%s has missing or unknown fields' % label)


def promote(data):
    """A whole-card review covers its statements, never its safety record."""
    if isinstance(data, dict):
        if 'tier' in data and review_rules.rank(data['tier']) < review_rules.rank('reviewed'):
            data['tier'] = 'reviewed'
        for field, value in data.items():
            if field != 'safety':
                promote(value)
    elif isinstance(data, list):
        for value in data:
            promote(value)


def validate_decision(things, decision, approved):
    exact_fields(decision, DECISION_FIELDS, 'decision')
    if not isinstance(decision['thing'], str):
        raise ValueError('decision must name a graph record')
    thing = things.get(decision['thing'])
    if thing is None or not thing.path.startswith('graph/') or 'tier' not in thing.data:
        raise ValueError('decision names no reviewable graph record')
    field = decision['field']
    if field not in (None, 'safety') or (field == 'safety' and thing.kind != 'ingredient'):
        raise ValueError('only whole content or ingredient safety can be approved')
    if decision['seen'] != review_hash.seen(thing.data, field):
        raise ValueError('%s has changed since it was read' % decision['thing'])
    if decision['attested'] is not True:
        raise ValueError('a human must personally attest to each decision')
    if decision['verdict'] not in ('approved', 'rejected') or not isinstance(decision['note'], str) or not decision['note'].strip():
        raise ValueError('each decision needs a verdict and an evidence or correction note')
    if field == 'safety' and decision['cuisine'] is not None:
        raise ValueError('safety approval is separate from cuisine approval')
    if field is None and (not isinstance(decision['cuisine'], str) or decision['cuisine'] not in things or things[decision['cuisine']].kind != 'cuisine'):
        raise ValueError('content approval needs a cuisine')
    if not isinstance(decision['sources'], list) or any(not isinstance(source, str) or source not in things or things[source].kind != 'source' for source in decision['sources']):
        raise ValueError('evidence must name recorded sources')
    unit = (decision['thing'], field, None)
    if approved.get(unit):
        raise ValueError('this unit has a live approval; replacing it needs an explicit superseding review')
    return thing, unit


def plan(root, packet, reviewer_id=None):
    exact_fields(packet, PACKET_FIELDS, 'approval file')
    if type(packet['version']) is not int or packet['version'] != 1:
        raise ValueError('unknown approval file version')
    if not isinstance(packet['commit'], str) or not re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}', packet['commit']):
        raise ValueError('approval file must identify its source commit')
    try:
        datetime.date.fromisoformat(packet['on'])
    except (TypeError, ValueError):
        raise ValueError('approval date must be a calendar day')
    things, issues = check.read_repository(root)
    if issues:
        raise ValueError('repository has %d issues; run ./check first' % len(issues))
    who = reviewer_id or packet['reviewer']
    if reviewer_id and packet['reviewer'] and reviewer_id != packet['reviewer']:
        raise ValueError('reviewer does not match the approval file')
    reviewer = things.get(who) if isinstance(who, str) else None
    if reviewer is None or reviewer.kind != 'reviewer':
        raise ValueError('this reviewer must first be registered by the owner')
    if reviewer.data['kind'] != 'person':
        raise ValueError('only a registered person can submit these approvals')
    if not isinstance(packet['decisions'], list) or not packet['decisions']:
        raise ValueError('approval file has no decisions')
    approved = review_rules.backing(things)
    digest = hashlib.sha256(json.dumps(packet, sort_keys=True).encode('utf-8')).hexdigest()[:12]
    seen = set()
    records = {}
    changes = {}
    for decision in packet['decisions']:
        thing, unit = validate_decision(things, decision, approved)
        if unit in seen:
            raise ValueError('the approval file repeats a unit')
        seen.add(unit)
        safety = decision['field'] == 'safety'
        if safety and decision['verdict'] == 'approved' and not decision['sources'] and not reviewer.data['safety_authority']:
            raise ValueError('each safety approval needs its own source evidence or owner-granted safety authority')
        grants = 'verified' if safety else 'reviewed'
        cuisine = None if safety else decision['cuisine']
        key = (grants, cuisine)
        if key not in records:
            topic = 'safety' if safety else cuisine.split('/')[1]
            identifier = 'review/%s-%s-%s-%s' % (who.split('/')[1], grants, topic, digest)
            if identifier in things:
                raise ValueError('this approval session is already recorded')
            records[key] = dict(id=identifier, reviewer=who, on=packet['on'], grants=grants, cuisine=cuisine,
                                mode='rows', sample=None, against=[], covers=[], rulings=[], supersedes=[],
                                note='Human approval file for source commit ' + packet['commit'])
        record = records[key]
        sources = decision['sources'] or [None]
        for source in sources:
            evidence = dict(how='source' if source else 'own-knowledge', source=source, note=decision['note'])
            if evidence not in record['against']:
                record['against'].append(evidence)
        note = decision['note']
        if decision['sources']:
            note += '\nSource records checked for this unit: ' + ', '.join(decision['sources'])
        record['covers'].append(dict(thing=decision['thing'], field=decision['field'], target=None,
                                     seen=decision['seen'], verdict=decision['verdict'], note=note))
        if decision['verdict'] == 'approved':
            data = changes.setdefault(thing.path, copy.deepcopy(thing.data))
            if safety:
                data['safety']['state'] = 'verified'
            else:
                promote(data)
    for record in records.values():
        changes['graph/' + record['id'] + '.json'] = record
    validate_result(root, changes)
    return changes


def validate_result(root, changes):
    """Run the existing repository checker before changing the real checkout."""
    with tempfile.TemporaryDirectory(prefix='approval-preview-') as temporary:
        for name in ('graph', 'schema', 'probes', 'docs'):
            source = Path(root, name)
            if source.exists():
                shutil.copytree(source, Path(temporary, name))
        for path, data in changes.items():
            destination = Path(temporary, path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(writing.as_text(data), encoding='utf-8')
        _, issues = check.read_repository(temporary)
        if issues:
            detail = '; '.join('%s: %s (%s)' % (issue.path, issue.message, issue.rule) for issue in issues[:3])
            raise ValueError('approval result fails the checker: ' + detail)


def write_file(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def apply(root, packet, reviewer_id=None):
    changes = plan(root, packet, reviewer_id)
    before = {path: Path(root, path).read_bytes() if Path(root, path).exists() else None for path in changes}
    try:
        for path, data in changes.items():
            write_file(Path(root, path), writing.as_text(data))
    except BaseException:
        for path, original in before.items():
            destination = Path(root, path)
            if original is None:
                if destination.exists():
                    destination.unlink()
            else:
                destination.write_bytes(original)
        raise
    return sorted(changes)
