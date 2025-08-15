import { World } from './World';

interface Node {
  x: number;
  y: number;
  g: number;
  f: number;
  parent?: Node;
}
export function findPath(world: World, sx: number, sy: number, tx: number, ty: number, maxIter = 500): { x: number; y: number }[] | null {
  if (sx === tx && sy === ty) return [];
  const open: Node[] = [];
  const start: Node = { x: sx, y: sy, g: 0, f: heuristic(sx, sy, tx, ty) };
  open.push(start);
  const visited = new Map<string, number>();
  while (open.length && maxIter-- > 0) {
    open.sort((a, b) => a.f - b.f);
    const cur = open.shift()!;
    if (cur.x === tx && cur.y === ty) {
      const path: { x: number; y: number }[] = [];
      let n: Node | undefined = cur;
      while (n && n !== start) {
        path.push({ x: n.x, y: n.y });
        n = n.parent;
      }
      path.reverse();
      return path;
    }
    const key = cur.x + ',' + cur.y;
    visited.set(key, cur.g);
    for (const [dx, dy] of [[1,0],[-1,0],[0,1],[0,-1]]) {
      const nx = cur.x + dx, ny = cur.y + dy;
      const tile = world.getTile(nx, ny);
      if (!tile) continue;
      const nk = nx + ',' + ny;
      const g = cur.g + 1;
      if (visited.has(nk) && visited.get(nk)! <= g) continue;
      let node = open.find(o => o.x === nx && o.y === ny);
      if (!node) {
        node = { x: nx, y: ny, g, f: g + heuristic(nx, ny, tx, ty), parent: cur };
        open.push(node);
      } else if (g < node.g) {
        node.g = g;
        node.parent = cur;
        node.f = g + heuristic(nx, ny, tx, ty);
      }
    }
  }
  return null;
}
function heuristic(x: number, y: number, tx: number, ty: number) {
  return Math.abs(x - tx) + Math.abs(y - ty);
}