"""Build the human approval page, including ingredient safety assertions as unverified evidence."""

import json
from pathlib import Path

from tools import review_hash


def payload(things, commit):
    graph = {identifier: thing for identifier, thing in sorted(things.items()) if thing.path.startswith('graph/')}
    units = {}
    for identifier, thing in graph.items():
        data = thing.data
        if 'tier' not in data:
            continue
        name = data.get('names', {}).get('en', data.get('title', identifier))
        cuisines = [row['thing'] for row in data.get('belongs_to', []) + data.get('in_pantry_of', [])]
        for field in (None, 'safety') if thing.kind == 'ingredient' else (None,):
            unit_id = identifier + ('#safety' if field else '#content')
            units[unit_id] = dict(id=unit_id, thing=identifier, kind=thing.kind, field=field, name=name,
                                  status=data['safety']['state'] if field else data['tier'],
                                  seen=review_hash.seen(data, field), cuisines=cuisines,
                                  raw=review_hash.unit(data, field))
    return dict(units=units, commit=commit, repository='mrspacerobot/cooking-graph',
                names={identifier: thing.data.get('names', {}).get('en', thing.data.get('title', identifier))
                       for identifier, thing in graph.items()},
                facts={identifier: thing.data for identifier, thing in graph.items() if thing.kind == 'fact'},
                sources={identifier: thing.data for identifier, thing in graph.items() if thing.kind == 'source'},
                cuisines={identifier: thing.data['names']['en'] for identifier, thing in graph.items() if thing.kind == 'cuisine'},
                reviewers={identifier: thing.data for identifier, thing in graph.items()
                           if thing.kind == 'reviewer' and thing.data['kind'] == 'person'})


def page(root, data):
    assets = Path(root, 'reviewer')
    text = (assets / 'approvals.html').read_text(encoding='utf-8')
    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    for marker, value in (
        ('__APPROVAL_STYLE__', (assets / 'style.css').read_text(encoding='utf-8')),
        ('__APPROVAL_DATA__', encoded),
        ('__APPROVAL_WORDS__', (assets / 'words.js').read_text(encoding='utf-8')),
        ('__APPROVAL_SCRIPT__', (assets / 'approvals.js').read_text(encoding='utf-8')),
    ):
        text = text.replace(marker, value)
    return text
