#!/usr/bin/env python3
"""
Nano Directory build script.

Reads directory.json and writes index.html.

    python3 build.py

The page layout, styles and scripts live in template.html. Everything
between the BUILD markers in that file is replaced with the generated
sections. Nothing else is touched.
"""

import datetime
import html as htmlmod
import json
import sys
from collections import Counter

DATA = 'directory.json'
TEMPLATE = 'template.html'
OUT = 'index.html'

START = '<!-- BUILD:START -->'
END = '<!-- BUILD:END -->'


def esc(s):
    """Escape text for use in HTML content."""
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;'))


def esc_attr(s):
    """Escape text for use in an HTML attribute value."""
    return esc(s).replace('"', '&quot;')


def fail(msg):
    print('ABORTED: ' + msg)
    sys.exit(1)


# ---------------------------------------------------------------- load

data = json.load(open(DATA, encoding='utf-8'))
sections = data['sections']
entries = data['entries']

# Stamp today's date. build.py is run when the directory changes, so the
# build date is the last-updated date. It is written back into
# directory.json so the published data, the page footer, the JSON-LD and
# the sitemap all carry the same value.
today = datetime.date.today().isoformat()
if data.get('updated') != today:
    data['updated'] = today
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

# index sections by id, and remember each one's depth
index = {}


def walk(nodes, depth, parent):
    for s in nodes:
        if s['id'] in index:
            fail('duplicate section id: %s' % s['id'])
        index[s['id']] = {'node': s, 'depth': depth, 'parent': parent}
        walk(s.get('children', []), depth + 1, s['id'])


walk(sections, 1, None)

# group entries by section, preserving file order
grouped = {}
for e in entries:
    sec = e.get('section')
    if sec not in index:
        fail('entry "%s" references unknown section "%s"' % (e['name'], sec))
    grouped.setdefault(sec, []).append(e)


# ------------------------------------------------------------ validate

problems = []

by_url = {}
for e in entries:
    by_url.setdefault(e['url'], set()).add(e['name'])
for url, names in by_url.items():
    if len(names) > 1:
        problems.append('one URL, several names: %s -> %s'
                        % (url, ', '.join(sorted(names))))

for e in entries:
    if not e.get('name'):
        problems.append('entry with no name at %s' % e.get('url'))
    if not e.get('url', '').startswith(('http://', 'https://')):
        problems.append('bad url on "%s": %s' % (e.get('name'), e.get('url')))

if problems:
    print('VALIDATION PROBLEMS (%d):' % len(problems))
    for p in problems:
        print('  ' + p)
    print()


# -------------------------------------------------------------- render

def render_item(e):
    a = '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (
        esc_attr(e['url']), esc(e['name']))
    desc = e.get('description')
    if desc:
        return '<li>%s \u2013 %s</li>' % (a, esc(desc))
    return '<li>%s</li>' % a


def render_section(sec, depth, indent):
    out = []
    pad = '  ' * indent
    items = grouped.get(sec['id'], [])
    kids = sec.get('children', [])

    if sec.get('collapsed'):
        out.append('%s<details id="%s"><summary>%s</summary>'
                   % (pad, esc_attr(sec['id']), esc(sec['title'])))
        if items:
            out.append('%s  <ul>' % pad)
            for e in items:
                out.append('%s    %s' % (pad, render_item(e)))
            out.append('%s  </ul>' % pad)
        for k in kids:
            out.extend(render_section(k, depth + 1, indent + 1))
        out.append('%s</details>' % pad)
        return out

    level = min(depth + 1, 6)          # depth 1 -> h2, depth 2 -> h3, ...
    if depth == 1:
        out.append('')
        out.append('<div class="category" id="%s">' % esc_attr(sec['id']))
        out.append('  <h2>%s</h2>' % esc(sec['title']))
    else:
        out.append('')
        out.append('%s<h%d id="%s">%s</h%d>'
                   % (pad, level, esc_attr(sec['id']), esc(sec['title']), level))

    if items:
        out.append('%s<ul>' % pad)
        for e in items:
            out.append('%s  %s' % (pad, render_item(e)))
        out.append('%s</ul>' % pad)

    for k in kids:
        out.extend(render_section(k, depth + 1, indent + 1 if depth > 1 else 1))

    if depth == 1:
        out.append('</div>')
    return out


body = []
for s in sections:
    body.extend(render_section(s, 1, 1))

nav = ['  <select id="sectionJump">',
       '    <option value="">Select...</option>']
for s in sections:
    nav.append('    <option value="#%s">%s</option>'
               % (esc_attr(s['id']), esc(s['title'])))
nav.append('  </select>')


# --------------------------------------------------------------- write

tpl = open(TEMPLATE, encoding='utf-8').read()
if START not in tpl or END not in tpl:
    fail('template.html is missing the BUILD markers')

head, rest = tpl.split(START, 1)
_, tail = rest.split(END, 1)

generated = '\n'.join(body)
result = head + START + '\n' + generated + '\n' + END + tail

result = result.replace('<!-- NAV:START -->', '\n'.join(nav))
result = result.replace('{{UPDATED}}', data.get('updated', ''))
result = result.replace('{{URL}}', data.get('url', ''))
result = result.replace('{{DESCRIPTION}}', esc_attr(data.get('description', '')))

open(OUT, 'w', encoding='utf-8').write(result)

# ------------------------------------------------------------- llms.txt

def render_llms():
    """Write llms.txt: a plain markdown view of the directory for LLMs."""
    out = []
    out.append('# %s' % data.get('name', 'Directory'))
    out.append('')
    out.append('> %s' % data.get('description', ''))
    out.append('')
    out.append('Machine-readable version of this directory: %s/directory.json'
               % data.get('url', '').rstrip('/'))
    out.append('Last updated: %s' % data.get('updated', ''))
    out.append('')

    def line(e):
        mark = ''
        tags = e.get('tags') or []
        if 'agent' in tags:
            mark = ' [agent]'
        elif 'agent-infra' in tags:
            mark = ' [agent-infra]'
        desc = e.get('description')
        if desc:
            return '- [%s](%s): %s%s' % (e['name'], e['url'], desc, mark)
        return '- [%s](%s)%s' % (e['name'], e['url'], mark)

    # agent-focused summary, deduplicated by URL, in directory order
    seen = set()
    agent, infra = [], []
    for e in entries:
        if e['url'] in seen:
            continue
        tags = e.get('tags') or []
        if 'agent' in tags:
            agent.append(e); seen.add(e['url'])
        elif 'agent-infra' in tags:
            infra.append(e); seen.add(e['url'])

    if agent or infra:
        out.append('## For AI agents')
        out.append('')
        out.append('Entries below are marked [agent] where the project is built for '
                   'autonomous agents, and [agent-infra] where it provides '
                   'infrastructure an agent needs (keys and signing, work '
                   'generation, node access, payment APIs, monitoring). The same '
                   'markers appear throughout this file, and the tags are in '
                   'directory.json.')
        out.append('')
        if agent:
            out.append('### Built for agents')
            out.append('')
            for e in agent:
                out.append(line(e))
            out.append('')
        if infra:
            out.append('### Infrastructure for agents')
            out.append('')
            for e in infra:
                out.append(line(e))
            out.append('')

    def section(sec, depth):
        hashes = '#' * min(depth + 1, 6)
        out.append('%s %s' % (hashes, sec['title']))
        out.append('')
        for e in grouped.get(sec['id'], []):
            out.append(line(e))
        if grouped.get(sec['id']):
            out.append('')
        for k in sec.get('children', []):
            section(k, depth + 1)

    for s in sections:
        section(s, 1)

    text = '\n'.join(out).rstrip() + '\n'
    open('llms.txt', 'w', encoding='utf-8').write(text)
    return text


# ------------------------------------------------------------ sitemap.xml

SITEMAP = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>%s/</loc>
    <lastmod>%s</lastmod>
  </url>
</urlset>
'''

open('sitemap.xml', 'w', encoding='utf-8').write(
    SITEMAP % (data.get('url', '').rstrip('/'), data['updated']))


llms = render_llms()
print('Wrote llms.txt (%d lines, %.1f KB)'
      % (llms.count('\n'), len(llms.encode('utf-8')) / 1024))

print('Wrote sitemap.xml')
print('Wrote %s' % OUT)
print('  updated : %s' % data['updated'])
print('  sections: %d (%d top level)' % (len(index), len(sections)))
print('  entries : %d' % len(entries))
counts = Counter(e['section'] for e in entries)
empty = [i for i in index if i not in counts and not index[i]['node'].get('children')]
if empty:
    print('  note: %d section(s) with no entries and no children: %s'
          % (len(empty), ', '.join(empty)))
