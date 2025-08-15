import { EntityPayload } from "./types"

export class ClientState {
  tick = 0
  entities: Map<number, Record<string, any>> = new Map()
  meta: Record<string, any> = {}
  applyFull(snap: { tick: number, entities: EntityPayload[], meta: any }) {
    this.tick = snap.tick
    this.entities.clear()
    snap.entities.forEach(e => this.entities.set(e.id, e.components))
    this.meta = snap.meta
  }
  applyDiff(diff: { tick: number, added: EntityPayload[], updated: EntityPayload[], removed: number[], meta: any }) {
    this.tick = diff.tick
    diff.added.forEach(e => this.entities.set(e.id, e.components))
    diff.updated.forEach(e => this.entities.set(e.id, e.components))
    diff.removed.forEach(id => this.entities.delete(id))
    this.meta = diff.meta
  }
  aggregateResources(): Record<string, number> {
    const sum: Record<string, number> = {}
    this.entities.forEach(c => {
      if (c.ResourceInventory) {
        const inv = c.ResourceInventory
        for (const k in inv.stored) {
          sum[k] = (sum[k] || 0) + inv.stored[k]
        }
      }
    })
    return sum
  }
}