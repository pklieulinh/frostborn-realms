import { ClientState } from "./state"
export function render(state: ClientState, ctx: CanvasRenderingContext2D) {
  ctx.fillStyle = "#0b0f14"
  ctx.fillRect(0,0,ctx.canvas.width, ctx.canvas.height)
  const tileSize = 20
  for (let x=0;x<40;x++){
    for (let y=0;y<30;y++){
      ctx.fillStyle = "#1d3344"
      ctx.fillRect(x*tileSize, y*tileSize, tileSize-1, tileSize-1)
    }
  }
  state.entities.forEach((comp, id) => {
    if (comp.Position && comp.Renderable) {
      const { x, y } = comp.Position
      const spr = comp.Renderable.sprite
      let color = "#fff"
      if (spr === "npc_leader") color = "#ffcc00"
      else if (spr === "npc_worker") color = "#66ccff"
      else if (spr === "wood") color = "#885522"
      else if (spr === "site") color = "#999999"
      else if (spr === "storage") color = "#44aa44"
      else if (spr === "heat") color = "#ff4444"
      ctx.fillStyle = color
      ctx.fillRect(x*tileSize+4, y*tileSize+4, tileSize-8, tileSize-8)
    }
  })
  ctx.fillStyle = "#fff"
  ctx.fillText("Tick: "+state.tick, 5, 12)
}