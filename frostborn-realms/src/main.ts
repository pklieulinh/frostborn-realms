import { Application } from 'pixi.js';
import { AssetLoader } from './assets/AssetLoader';
import { AssetMap } from './assets/AssetMap';
import { World } from './world/World';
import { EntityManager } from './core/ecs/EntityManager';
import { RenderingSystem } from './systems/RenderingSystem';
import { AILocalSystem } from './systems/AILocalSystem';
import { GameLoop } from './core/loop/GameLoop';
import { UISystem } from './systems/UISystem';

const overlay = document.createElement('div');
Object.assign(overlay.style, {
  position:'fixed', inset:'0', background:'#0d1419',
  display:'flex', flexDirection:'column', alignItems:'center',
  justifyContent:'center', font:'13px monospace', color:'#9fb6c9', zIndex:'9999'
});
overlay.innerHTML = '<div>Loading...</div><div id="st" style="opacity:.8;margin-top:6px">Init</div>';
document.body.appendChild(overlay);
const st = overlay.querySelector('#st') as HTMLElement;
function setStatus(s:string){ if(st) st.textContent=s; }

async function bootstrap() {
  setStatus('Pixi');
  const app = new Application();
  await app.init({ backgroundAlpha:0, width:window.innerWidth, height:window.innerHeight });
  document.body.appendChild(app.canvas);
  window.addEventListener('resize',()=>app.renderer.resize(window.innerWidth,window.innerHeight));

  setStatus('Assets');
  const loader = new AssetLoader();
  await loader.loadAll();

  setStatus('World');
  const world = new World();
  (world as any).generateInitial?.();
  const em = new EntityManager();
  (window as any).em = em;

  setStatus('Systems');
  const assetMap = new AssetMap(loader);
  const renderSystem = new RenderingSystem(app, world, em, loader);
  const ai = new AILocalSystem(em);
  const ui = new UISystem(world, em, loader, assetMap, renderSystem);

  const loop = new GameLoop();
  loop.add(dt=>{
    ai.update(dt);
    renderSystem.update();
    ui.update?.(dt);
  });
  loop.start();

  overlay.style.transition='opacity .25s';
  overlay.style.opacity='0';
  setTimeout(()=>overlay.remove(),260);
}

bootstrap().catch(e=>{
  console.error('[BOOT FAIL]', e);
  overlay.innerHTML = '<div style="color:#ff6666;font:14px monospace">Boot error: '+(e?.message||e)+'</div>';
});