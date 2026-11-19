#!/usr/bin/env python3
"""Collect browser facts or check a saved snapshot; never assign an aesthetic score.

Informed by Huashu Design's facts/visual-review split. This is an independent,
host-neutral implementation, not a wrapper for its Playwright/Pillow toolchain.
"""
import argparse
import json
import math
import sys
from pathlib import Path


COLLECTOR = r"""() => {
  const root = document.documentElement;
  const visible = el => {
    const box = el.getBoundingClientRect();
    if (box.width <= 0 || box.height <= 0) return false;
    for (let node = el; node; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (style.display === 'none' || style.visibility !== 'visible' || Number(style.opacity) === 0) return false;
    }
    return true;
  };
  const path = el => {
    const parts = [];
    for (let node = el; node && parts.length < 5; node = node.parentElement) {
      const tag = node.localName;
      if (!tag) break;
      const siblings = node.parentElement ? [...node.parentElement.children].filter(x => x.localName === tag) : [];
      parts.unshift(tag + (siblings.length > 1 ? `:nth-of-type(${siblings.indexOf(node) + 1})` : ''));
    }
    return parts.join(' > ');
  };
  const text = [];
  const walker = document.createTreeWalker(document.body || root, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    const el = node.parentElement;
    if (!el || el.closest('script,style,noscript,template,textarea,input,[contenteditable],svg')) continue;
    const sample = node.textContent.trim().replace(/\s+/g, ' ');
    if (!sample || !visible(el)) continue;
    const style = getComputedStyle(el);
    const box = el.getBoundingClientRect();
    text.push({path: path(el), sample: sample.slice(0, 80), font_size: parseFloat(style.fontSize),
      font_weight: style.fontWeight, font_family: style.fontFamily, color: style.color,
      numeric_variant: style.fontVariantNumeric,
      in_viewport: box.bottom > 0 && box.top < innerHeight && box.right > 0 && box.left < innerWidth});
  }
  const images = [...document.images].filter(visible).map(el => ({path: path(el),
    status: !el.complete ? 'pending' : el.naturalWidth > 0 ? 'loaded' : 'broken'}));
  return {schema_version: 1, captured_at: new Date().toISOString(),
    document: {ready_state: document.readyState, fonts_status: document.fonts ? document.fonts.status : 'unknown'},
    viewport: {width: innerWidth, height: innerHeight, scroll_x: scrollX, scroll_y: scrollY},
    horizontal_overflow: Math.max(0, root.scrollWidth - root.clientWidth), text, images,
    coverage: {text_nodes: text.length, images: images.length,
      iframes: document.querySelectorAll('iframe').length,
      shadow_hosts: [...document.querySelectorAll('*')].filter(el => el.shadowRoot).length}};
}"""


class EvidenceError(ValueError):
    pass


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def check(snapshot, min_text=None):
    """Separate observed failures, review hints and work the snapshot cannot prove."""
    if not isinstance(snapshot, dict) or type(snapshot.get('schema_version')) is not int or snapshot['schema_version'] != 1:
        raise EvidenceError('Expected a schema_version=1 browser snapshot')
    try:
        viewport = snapshot['viewport']
        if not all(number(viewport[key]) and viewport[key] > 0 for key in ('width', 'height')):
            raise EvidenceError('Invalid viewport')
        overflow = snapshot['horizontal_overflow']
        if not number(overflow) or overflow < 0:
            raise EvidenceError('Invalid horizontal_overflow')
        for key in ('text', 'images'):
            if not isinstance(snapshot[key], list):
                raise EvidenceError('Invalid ' + key)
        if not isinstance(snapshot['document'], dict) or not isinstance(snapshot['coverage'], dict):
            raise EvidenceError('Missing document/coverage')
        if not isinstance(snapshot['captured_at'], str) or not snapshot['captured_at'].strip():
            raise EvidenceError('Missing capture time')
        if snapshot['document']['ready_state'] not in ('loading', 'interactive', 'complete'):
            raise EvidenceError('Invalid document state')
        if snapshot['document']['fonts_status'] not in ('loading', 'loaded', 'unknown'):
            raise EvidenceError('Invalid font state')
        for key in ('text_nodes', 'images', 'iframes', 'shadow_hosts'):
            if type(snapshot['coverage'][key]) is not int or snapshot['coverage'][key] < 0:
                raise EvidenceError('Invalid coverage count')
        for row in snapshot['text']:
            if not isinstance(row, dict) or not number(row['font_size']) or row['font_size'] <= 0:
                raise EvidenceError('Invalid text measurement')
        for row in snapshot['images']:
            if not isinstance(row, dict) or row['status'] not in ('loaded', 'pending', 'broken'):
                raise EvidenceError('Invalid image status')
    except (KeyError, TypeError) as error:
        raise EvidenceError('Incomplete browser evidence: ' + str(error)) from error
    if min_text is not None and (not number(min_text) or min_text <= 0):
        raise EvidenceError('min_text must be a positive finite CSS pixel value')

    failures, review = [], []
    for row in snapshot['images']:
        if row['status'] == 'broken':
            failures.append({'kind': 'broken_image', 'path': row.get('path', '')})
        elif row['status'] == 'pending':
            review.append({'kind': 'pending_image', 'path': row.get('path', ''), 'action': 'Wait for the relevant image and recapture'})
    if overflow > 1:
        review.append({'kind': 'horizontal_overflow', 'pixels': overflow,
                       'action': 'Check the viewport screenshot; an intentional scroll region is not automatically a defect'})
    if snapshot['document'].get('ready_state') != 'complete':
        review.append({'kind': 'document_not_complete'})
    if snapshot['document'].get('fonts_status') != 'loaded':
        review.append({'kind': 'fonts_not_settled'})
    if min_text is not None:
        review.extend({'kind': 'below_project_text_threshold', 'path': row.get('path', ''),
                       'measured_css_px': row['font_size'], 'threshold_css_px': min_text}
                      for row in snapshot['text'] if row['font_size'] < min_text)
    if not snapshot['text'] and not snapshot['images']:
        review.append({'kind': 'no_supported_content', 'action': 'A canvas/SVG/blank screen requires visual inspection'})
    for key in ('iframes', 'shadow_hosts'):
        if snapshot['coverage'].get(key, 0):
            review.append({'kind': 'outside_collector_scope', 'content': key, 'count': snapshot['coverage'][key]})
    return {'schema_version': 1, 'status': 'observed_failures' if failures else 'needs_review',
            'viewport': viewport, 'failures': failures, 'review': review,
            'unverified': ['visual_quality_and_direction', 'contrast_and_actual_font_glyphs',
                           'keyboard_touch_focus_and_business_states', 'motion_reduced_motion_and_performance',
                           'console_network_errors_and_unvisited_content', 'pseudo_elements_svg_canvas_and_closed_shadow_dom'],
            'note': 'No pass/compliance/aesthetic score. Pair with screenshots and actual interactions.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('collector', help='Print a read-only function for an already authorized browser evaluator')
    audit = sub.add_parser('check', help='Check one saved browser snapshot; prints JSON, writes no files')
    audit.add_argument('snapshot', type=Path)
    audit.add_argument('--min-text', type=float, help='Optional project-specific CSS px review threshold')
    args = parser.parse_args(argv)
    if args.command == 'collector':
        print(COLLECTOR)
        return 0
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))
        result = check(snapshot, args.min_text)
    except (OSError, ValueError, TypeError) as error:
        print('Evidence unavailable: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['failures'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
