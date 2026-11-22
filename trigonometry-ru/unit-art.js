// Chalk sketches for the unit headers on the contents page, one per unit, drawn in the unit's colour.
// Each entry is the inside of an SVG with viewBox 0 0 600 180; keep the left ~200 px light (the unit title sits there
// on narrow screens). Classes, styled in lib/units.css:
//   d  a stroke that draws itself in when the unit scrolls into view (--k orders the strokes)
//   t  text or a filled shape that fades in
//   a  faint chalk white instead of the unit colour;  faint  even fainter
// A sketch may add one looping motion after it is drawn: give an element a class that lib/units.css animates (swap-a,
// hop, orbit, ride, spin, tilt, breathe, ...), or add your own .seen .unit-art .NAME rule and keyframes in a <style> in index.html.
'use strict';
(() => {
  let k = 0;
  const P = (d, cls = '', extra = '') => `<path class="d ${cls}" pathLength="1" style="--k:${k++}" d="${d}" ${extra}/>`;
  const Tx = (x, y, s, size = 24, cls = '', anchor = 'start') => `<text class="t ${cls}" style="--k:${k++}" x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}">${s}</text>`;
  const C = (cx, cy, r, cls = '') => `<circle class="d ${cls}" pathLength="1" style="--k:${k++}" cx="${cx}" cy="${cy}" r="${r}"/>`;
  const reset = s => { k = 0; return s; };

  window.UNIT_ART = [
    // 1 Trigonometric functions: a unit circle with the point M, its radius and two legs, and sin α = y beside it.
    reset(P('M250 140H470', 'a') + P('M360 172V18', 'a') + P('M450 140A90 90 0 0 0 270 140') +
      P('M360 140L424 76') + P('M424 76V140') + P('M360 140H424') +
      `<circle class="t" cx="424" cy="76" r="6" fill="currentColor" stroke="none" style="--k:${k++}"/>` +
      Tx(490, 70, 'sin α = y', 26) + Tx(490, 110, 'cos α = x', 26, 'a')),
  ];
})();
