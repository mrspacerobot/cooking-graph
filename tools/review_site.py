"""Build a static editorial review site, separate from the production export."""

import hashlib
import json
import sys
from pathlib import Path

from tools import approval_site, check, queries, recipe_text
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


def substitutions(graph):
    """Each directional claim gets its own feedback target, without safety facts."""
    for thing in graph.values():
        if thing.kind not in queries.FOODS:
            continue
        for row in thing.data['stands_in_for']:
            candidate = thing.data['id']
            original = row['thing']
            digest = hashlib.sha256(json.dumps(row, sort_keys=True).encode('utf-8')).hexdigest()
            data = {field: row[field] for field in ('tier', 'allows', 'when', 'not_when', 'ratio', 'caveat')}
            data.update(id='substitution/%s/%s' % (candidate, digest),
                        candidate=candidate, original=original,
                        names={'en': '%s for %s' % (thing.data['names']['en'], graph[original].data['names']['en'])})
            yield entry(data, 'substitution', candidate)


def recipe_substitutions(graph, recipe_id, claims):
    # Reuse the same context, method and exclusion rules as ./stand-ins.
    # The query's safety message and avoidance facts are not exported.
    lines = queries.stand_ins(graph, recipe_id)['lines']
    for line in lines:
        for row in line['options'] + line['excluded']:
            found = claims.get((row['thing'], line['original']), [])
            if row.get('basis') == 'stand-in':
                fields = ('tier', 'allows', 'when', 'not_when', 'ratio', 'caveat')
                found = [claim for claim in found if all(claim[field] == row[field] for field in fields)]
            elif row.get('basis') == 'part-option':
                found = []
            row['claims'] = [claim['id'] for claim in found]
    return lines


def steps_as_read(graph, recipe):
    """Each step with `text_as_read`: the step text as written for the recipe's own foods, so a reviewer reads words."""
    texts = dict(recipe_text.rendered_steps(graph, recipe))
    return [dict(step, text_as_read=texts[number]) for number, step in enumerate(recipe['steps'], start=1)]


def payload(things, commit):
    graph = {identifier: thing for identifier, thing in sorted(things.items()) if thing.path.startswith('graph/')}
    entries = {row['id']: row for row in substitutions(graph)}
    claims = {}
    for row in entries.values():
        claims.setdefault((row['candidate'], row['original']), []).append(row)
    for thing in graph.values():
        if thing.kind in ('technique', 'recipe', 'preparation'):
            data = dict(thing.data)
            if thing.kind == 'recipe':
                data['substitutions'] = recipe_substitutions(graph, data['id'], claims)
                data['steps'] = steps_as_read(graph, data)
            elif thing.kind == 'technique':
                data['recipes'] = queries.recipes(graph, data['id'])['recipes']
                data['variants'] = [dict(row, thing=other.data['id'])
                                    for other in graph.values() if other.kind == 'technique'
                                    for row in other.data['variant_of'] if row['thing'] == data['id']]
            record = entry(data, thing.kind, thing.data['id'])
            entries[record['id']] = record
        elif thing.kind == 'program':
            for record in classes(thing.data):
                entries[record['id']] = record
    # Food labels support navigation without exporting ingredient safety assertions.
    labels = {}
    for thing in graph.values():
        if thing.kind in LABEL_KINDS:
            labels[thing.data['id']] = {
                'name': thing.data.get('names', {}).get('en', thing.data['id']),
                'cuisines': [row['thing'] for row in thing.data.get('belongs_to', []) + thing.data.get('in_pantry_of', [])],
            }
    return {'entries': entries, 'names': labels, 'commit': commit, 'repository': REPOSITORY}


def page(root, data):
    assets = Path(root, 'reviewer')
    text = (assets / 'index.html').read_text(encoding='utf-8')
    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    for marker, content in (
        ('__REVIEW_STYLE__', (assets / 'style.css').read_text(encoding='utf-8')),
        ('__REVIEW_DATA__', encoded),
        ('__REVIEW_WORDS__', (assets / 'words.js').read_text(encoding='utf-8')),
        ('__REVIEW_PROGRESS__', (assets / 'progress.js').read_text(encoding='utf-8')),
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
    (destination / 'approvals.html').write_text(approval_site.page(assets or root, approval_site.payload(things, data['commit'])), encoding='utf-8')
    (destination / '.nojekyll').touch()
    print('Built %d review entries: %s' % (len(data['entries']), (destination / 'index.html').resolve()))
    return 0
