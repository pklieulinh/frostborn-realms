import { ClientState } from "./state"
import { GameConnection } from "./net"

export function bindUI(state: ClientState, conn: GameConnection) {
  const resEl = document.getElementById("resources")!
  const decEl = document.getElementById("decisions")!
  const pendEl = document.getElementById("pending")!
  const eventEl = document.getElementById("events")!
  const expEl = document.getElementById("expeditions")!
  const toggleBtn = document.getElementById("toggleIntervention") as HTMLButtonElement
  const launchBtn = document.getElementById("launchExpedition") as HTMLButtonElement
  const seedInput = document.getElementById("portalSeed") as HTMLInputElement
  const saveBtn = document.getElementById("saveBtn") as HTMLButtonElement
  const loadBtn = document.getElementById("loadBtn") as HTMLButtonElement

  toggleBtn.onclick = () => conn.sendCommand("toggle_intervention")
  launchBtn.onclick = () => {
    const seed = parseInt(seedInput.value)
    if (!isNaN(seed)) conn.sendCommand("launch_expedition", { seed })
  }
  saveBtn.onclick = () => fetch("/save",{method:"POST"})
  loadBtn.onclick = () => fetch("/load",{method:"POST"})

  function redraw() {
    const agg = state.aggregateResources()
    resEl.textContent = Object.entries(agg).map(([k,v])=>`${k}:${v}`).join(" | ")
    decEl.innerHTML = ""
    const decisions = state.meta.decision_feed || []
    for (let i = decisions.length-1; i>=0; i--) {
      const d = decisions[i]
      const div = document.createElement("div")
      div.textContent = `[${d.tick}] ${d.type} -> ${d.chosen}`
      decEl.appendChild(div)
    }
    pendEl.innerHTML = ""
    const leader = findLeader(state)
    if (leader && leader.LeaderAI && leader.LeaderAI.intervention_pending && leader.LeaderAI.intervention_pending.length) {
      const pending = leader.LeaderAI.intervention_pending
      pending.forEach((p: any, idx: number) => {
        const wrap = document.createElement("div")
        wrap.className = "decision-pending"
        wrap.textContent = `Pending: ${p.chosen}`
        const btnC = document.createElement("button")
        btnC.textContent = "Confirm"
        btnC.onclick = () => conn.sendCommand("confirm_decision", { index: idx })
        const btnR = document.createElement("button")
        btnR.textContent = "Reject"
        btnR.onclick = () => conn.sendCommand("reject_decision", { index: idx })
        wrap.appendChild(btnC)
        wrap.appendChild(btnR)
        pendEl.appendChild(wrap)
      })
    }
    eventEl.innerHTML = ""
    const events = state.meta.event_feed || []
    for (let i = events.length-1; i>=0; i--) {
      const e = events[i]
      const div = document.createElement("div")
      div.textContent = `[${e.tick}] ${e.type}: ${e.detail}`
      eventEl.appendChild(div)
    }
    expEl.innerHTML = ""
    const exps = state.meta.expedition_feed || []
    for (let i = exps.length-1; i>=0; i--) {
      const e = exps[i]
      const div = document.createElement("div")
      div.textContent = `[${e.tick}] #${e.id} ${e.status}`
      expEl.appendChild(div)
    }
  }
  setInterval(redraw, 500)
}

function findLeader(state: ClientState): any {
  for (const [, comps] of state.entities) {
    if (comps.Role && comps.Role.type === "Leader") return comps
  }
  return null
}