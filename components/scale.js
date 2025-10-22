/**
 * Линейная интерполяция цвета по t∈[0..1] между красным (#c0392b), жёлтым (#f1c40f) и зелёным (#27ae60).
 * Возвращает строку вида "#rrggbb".
 */
export function redYellowGreen(t) {
  const clamp = (x) => Math.max(0, Math.min(1, x));
  t = clamp(t);

  // два сегмента: [0..0.5] red→yellow, [0.5..1] yellow→green
  const lerp = (a, b, u) => a + (b - a) * u;

  const R1 = [0xc0, 0x39, 0x2b]; // #c0392b
  const R2 = [0xf1, 0xc4, 0x0f]; // #f1c40f
  const R3 = [0x27, 0xae, 0x60]; // #27ae60

  let r, g, b;
  if (t <= 0.5) {
    const u = t / 0.5;
    r = Math.round(lerp(R1[0], R2[0], u));
    g = Math.round(lerp(R1[1], R2[1], u));
    b = Math.round(lerp(R1[2], R2[2], u));
  } else {
    const u = (t - 0.5) / 0.5;
    r = Math.round(lerp(R2[0], R3[0], u));
    g = Math.round(lerp(R2[1], R3[1], u));
    b = Math.round(lerp(R2[2], R3[2], u));
  }
  return "#" + [r, g, b].map(x => x.toString(16).padStart(2, "0")).join("");
}

/** Равные интервалы между min..max, возвращает массив границ длиной (bins+1) */
export function equalBreaks(min, max, bins) {
  if (!(isFinite(min) && isFinite(max)) || bins <= 0) return [0, 1];
  if (min === max) return [min, max]; // хитом по плоскому массиву
  const step = (max - min) / bins;
  const edges = [];
  for (let i = 0; i <= bins; i++) edges.push(min + step * i);
  return edges;
}

/** Находит индекс интервала [edges[i], edges[i+1]) для значения v */
export function binIndex(v, edges) {
  if (!isFinite(v) || edges.length < 2) return 0;
  const last = edges.length - 2;
  for (let i = 0; i < edges.length - 1; i++) {
    const lo = edges[i], hi = edges[i + 1];
    if (v < hi || i === last) return i;
  }
  return last;
}
