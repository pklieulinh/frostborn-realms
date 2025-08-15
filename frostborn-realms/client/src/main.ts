import { GameConnection, attachTyped } from "./net"
import { ClientState } from "./state"
import { render } from "./render"
import { bindUI } from "./ui"

const canvas = document.getElementById("view") as HTMLCanvasElement
const ctx = canvas.getContext("2d")!
const state = new ClientState()

async function run() {
  const conn = new GameConnection()
  await conn.connect(`ws://${location.host.replace(/:\\d+$/, ":8000")}/ws`)
  attachTyped(conn, {
    full: snap => { state.applyFull(snap) },
    diff: diff => { state.applyDiff(diff) },
  })
  bindUI(state, conn)
  setInterval(()=>conn.ping(), 3000)
  function loop(){
    render(state, ctx)
    requestAnimationFrame(loop)
  }
  loop()
}

run().catch(e => console.error(e))