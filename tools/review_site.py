"""Build a static editorial review site, separate from the production export."""

import hashlib
import json
import sys
from pathlib import Path

from tools import check
from tools.viewer import metadata

REPOSITORY = 'mrspacerobot/cooking-graph'
LABEL_KINDS = {'technique', 'recipe', 'program', 'ingredient', 'preparation',
               'dish', 'equipment', 'group', 'form', 'cuisine'}


def entry(data, kind, source):
    record = dict(data, kind=kind, source=source)
    encoded = json.dumps(record, sort_keys=True, ensure_ascii=False).encode('utf-8')
    record['hash'] = hashlib.sha256(encoded).hexdigest()
    return record


def classes(program):
    """Levels are reviewable lessons; their parent program remains the source."""
    for course in program['courses']:
        for skill in course['skills']:
            for level in skill['levels']:
                identifier = '/'.join(['class', program['id'].split('/')[1],
                                       course['slug'], skill['slug'], str(level['number'])])
                data = dict(level, id=identifier, tier=program['tier'],
                            program=program['names']['en'], course=course['names']['en'],
                            skill=skill['names']['en'], skill_slug=skill['slug'],
                            comes_after=skill['comes_after'])
                yield entry(data, 'class', program['id'])


def payload(things, commit):
    graph = [thing for _, thing in sorted(things.items()) if thing.path.startswith('graph/')]
    entries = {}
    for thing in graph:
        if thing.kind in ('technique', 'recipe'):
            record = entry(thing.data, thing.kind, thing.data['id'])
            entries[record['id']] = record
        elif thing.kind == 'program':
            for record in classes(thing.data):
                entries[record['id']] = record
    # Labels and dish links are enough to navigate. Ingredient safety assertions
    # and stand-in claims do not belong in this editorial site.
    labels = {}
    for thing in graph:
        if thing.kind in LABEL_KINDS:
            labels[thing.data['id']] = {
                'name': thing.data.get('names', {}).get('en', thing.data['id']),
                'cuisines': [row['thing'] for row in thing.data.get('belongs_to', [])],
            }
    return {'entries': entries, 'names': labels, 'commit': commit, 'repository': REPOSITORY}


def page(root, data):
    assets = Path(root, 'reviewer')
    text = (assets / 'index.html').read_text(encoding='utf-8')
    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    for marker, content in (
        ('__REVIEW_STYLE__', (assets / 'style.css').read_text(encoding='utf-8')),
        ('__REVIEW_DATA__', encoded),
        ('__REVIEW_SCRIPT__', (assets / 'app.js').read_text(encoding='utf-8')),
    ):
        text = text.replace(marker, content)
    return text


def main(root, assets=None):
    things, issues = check.read_repository(root)
    if issues:
        print('review-site: graph has %d issues; run ./check' % len(issues), file=sys.stderr)
        return 1
    data = payload(things, metadata(root)['commit'])
    destination = Path(root, 'out', 'site')
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'index.html').write_text(page(assets or root, data), encoding='utf-8')
    (destination / '.nojekyll').touch()
    print('Built %d review entries: %s' % (len(data['entries']), (destination / 'index.html').resolve()))
    return 0
