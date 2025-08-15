import { WorldSnapshot, WorldDiff, ServerHello } from "./types"

type EventHandler = (msg: any) => void

export class GameConnection {
  private ws?: WebSocket
  private handlers: EventHandler[] = []
  connect(url: string) {
    return new Promise<void>((resolve, reject) => {
      this.ws = new WebSocket(url)
      this.ws.onopen = () => resolve()
      this.ws.onerror = e => reject(e)
      this.ws.onmessage = ev => {
        try {
          const data = JSON.parse(ev.data)
            this.handlers.forEach(h => h(data))
        } catch (e) {
          console.error("Bad message", e)
        }
      }
    })
  }
  on(handler: EventHandler) {
    this.handlers.push(handler)
  }
  sendCommand(cmd: string, data: Record<string, any> = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ cmd, data }))
    }
  }
  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send("ping")
    }
  }
}

export interface NetEvents {
  hello?: (h: ServerHello) => void
  full?: (w: WorldSnapshot) => void
  diff?: (d: WorldDiff) => void
  ack?: (a: any) => void
}

export function attachTyped(conn: GameConnection, map: NetEvents) {
  conn.on(msg => {
    if (msg.protocol && msg.title && map.hello) {
      map.hello(msg as ServerHello)
      return
    }
    if (msg.type === "full" && map.full) {
      map.full(msg.payload as WorldSnapshot)
      return
    }
    if (msg.type === "diff" && map.diff) {
      map.diff(msg.payload as WorldDiff)
      return
    }
    if (msg.status && map.ack) {
      map.ack(msg)
    }
  })
}