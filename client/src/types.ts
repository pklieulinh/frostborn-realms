export interface EntityPayload {
  id: number
  components: Record<string, any>
}
export interface WorldSnapshot {
  tick: number
  protocol: string
  seed: number
  entities: EntityPayload[]
  removed: number[]
  meta: Record<string, any>
}
export interface WorldDiff {
  tick: number
  protocol: string
  seed: number
  added: EntityPayload[]
  updated: EntityPayload[]
  removed: number[]
  meta: Record<string, any>
}
export interface ServerHello {
  protocol: string
  title: string
  seed: number
}
export interface Ack {
  status: string
  detail: string
}