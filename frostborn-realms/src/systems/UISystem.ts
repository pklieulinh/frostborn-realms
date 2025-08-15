import { System } from '../core/ecs/Systems';
import { World } from '../world/World';
import { EntityManager } from '../core/ecs/EntityManager';
import { RenderingSystem } from './RenderingSystem';
import { AIStrategicSystem } from './AIStrategicSystem';
import { ExpeditionSystem } from './ExpeditionSystem';
import { TechSystem } from './TechSystem';
import { SpectatorSystem } from './SpectatorSystem';
import { DataRegistry } from '../data/registry';

interface Decision { id: string; priority: number; rationale: string[]; }

export class UISystem implements System {
  id = 'ui';
  private leaderId: number | null = null;
  private decisions: Decision[] = [];
  private intervention = false;
  private overlay: HTMLElement;
  private expeditionOverlay: HTMLElement;
  private lastUpdate = 0;

  resourceEl = document.getElementById('resource-panel')!;
  leaderEl = document.getElementById('leader-panel')!;
  moodEl = document.getElementById('mood-panel')!;
  expeditionEl = document.getElementById('expedition-panel')!;
  techEl = document.getElementById('tech-panel')!;
  eventFeedEl = document.getElementById('event-feed')!;
  cameraEl = document.getElementById('camera-panel')!;
  saveLoadEl = document.getElementById('save-load-panel')!;
  spectatorEl = document.getElementById('spectator-panel')!;
  modEl = document.getElementById('mod-panel')!;

  // New panels
  searchPanel: HTMLElement;
  analyticsPanel: HTMLElement;

  private feed: string[] = [];
  private searchQuery = '';
  private searchCategory = 'resources';
  private searchResults: any[] = [];
  private data: DataRegistry;

  constructor(private world: World, private em: EntityManager, private render: RenderingSystem, private aiStrategic: AIStrategicSystem, private expeditionSystem: ExpeditionSystem, private techSystem: TechSystem, private spectator: SpectatorSystem, data: DataRegistry) {
    this.data = data;
    this.overlay = document.getElementById('center-overlay')!;
    this.expeditionOverlay = document.getElementById('expedition-map-overlay')!;
    // Create search & analytics panel containers
    this.searchPanel = this.createPanelAfter(this.modEl, 'search-panel');
    this.analyticsPanel = this.createPanelAfter(this.searchPanel, 'analytics-panel');
    this.renderEverything();
  }

  setData(reg: DataRegistry) { this.data = reg; }

  private createPanelAfter(afterEl: HTMLElement, id: string) {
    const div = document.createElement('div');
    div.className = 'panel';
    div.id = id;
    afterEl.parentElement!.insertBefore(div, afterEl.nextSibling);
    return div;
  }

  update(dt: number, elapsed: number): void {
    if (elapsed - this.lastUpdate > 0.8) {
      this.lastUpdate = elapsed;
      this.renderEverything();
    }
    this.renderExpeditionRealtime();
  }

  renderEverything() {
    this.renderResources();
    this.renderLeader();
    this.renderMood();
    this.renderExpeditions();
    this.renderTech();
    this.renderEventFeed();
    this.renderCamera();
    this.renderSaveLoad();
    this.renderSpectator();
    this.renderModPanel();
    this.renderSearchPanel();
    this.renderAnalyticsPanel();
  }

  setLeader(id: number) { this.leaderId = id; this.render.setLeader(id); }
  setStrategicDecisions(d: Decision[]) { this.decisions = d; }
  promptDecision(q: { title: string; options: { id: string; label: string; cb: () => void }[] }) {
    this.overlay.innerHTML = '';
    const h = document.createElement('h2'); h.textContent = q.title;
    this.overlay.appendChild(h);
    const wrap = document.createElement('div');
    for (const opt of q.options) {
      const b = document.createElement('button'); b.textContent = opt.label;
      b.onclick = () => { opt.cb(); this.overlay.style.display = 'none'; };
      wrap.appendChild(b);
    }
    this.overlay.appendChild(wrap);
    this.overlay.style.display = 'block';
  }
  pushEventFeed(msg: string) {
    this.feed.unshift(new Date().toLocaleTimeString() + ' ' + msg);
    if (this.feed.length > 200) this.feed.pop();
  }

  renderResources() {
    const list = Object.entries(this.world.resourceStock).map(([id, qty]) => `<span class="pill">${id}:${qty}</span>`).join('');
    this.resourceEl.innerHTML = `<h3>Tài Nguyên</h3>
    <div>Kho: ${this.world.storageUsed}/${this.world.storageCapacity}</div>
    <div>Nhiệt TB: ${this.world.avgTemp.toFixed(1)}° | PortalBoost ${this.world.portalBoost}</div>
    <div>${list || '<i>Trống</i>'}</div>`;
  }
  renderLeader() {
    const decStr = this.decisions.map(d => `<div>${d.id} ${(d.priority*100).toFixed(0)}%<br>${d.rationale.join(', ')}</div>`).join('');
    this.leaderEl.innerHTML = `<h3>Thủ Lĩnh</h3>
    <div>ID: ${this.leaderId ?? 'N/A'}</div>
    <div><button id="btn-interv">${this.intervention ? 'Can Thiệp: BẬT' : 'Can Thiệp: TẮT'}</button></div>
    <div>Quyết định:</div>
    <div style="max-height:130px; overflow:auto;">${decStr || '<i>Không</i>'}</div>`;
    const btn = this.leaderEl.querySelector('#btn-interv') as HTMLButtonElement;
    btn.onclick = () => {
      this.intervention = !this.intervention;
      this.aiStrategic.toggleIntervention(this.intervention);
      this.renderLeader();
    };
  }
  renderMood() {
    let sumMor = 0; let sumSan = 0; let n = 0;
    for (const m of this.em.mood.values()) { sumMor += m.morale; sumSan += m.sanity; n++; }
    const avgM = n ? sumMor / n : 0;
    const avgS = n ? sumSan / n : 0;
    const moodLabel = avgM < 25 ? 'Despair' : avgM < 50 ? 'Low' : avgM < 80 ? 'Stable' : 'Inspired';
    this.moodEl.innerHTML = `<h3>Tinh Thần</h3>
      <div>Morale: ${avgM.toFixed(1)} (${moodLabel})</div>
      <div>Sanity: ${avgS.toFixed(1)}</div>`;
  }

  renderExpeditions() {
    const exps = this.em.expeditions.slice(-8);
    const lines = exps.map(e => {
      if (e.result) return `<div>[#${e.id}] ${e.result.success ? 'Thành công' : 'Thất bại'} ${e.result.loot ? e.result.loot.map((l: any) => l.resource + '+' + l.qty).join(', ') : ''}</div>`;
      return `<div>[#${e.id}] ${e.status}</div>`;
    }).join('');
    this.expeditionEl.innerHTML = `<h3>Thám Hiểm</h3>
    <button id="btn-exp">Tạo Expedition</button>
    <button id="btn-exp-overlay">Toggle Map</button>
    <div style="max-height:140px; overflow:auto;">${lines || '<i>Chưa có</i>'}</div>`;
    (this.expeditionEl.querySelector('#btn-exp') as HTMLButtonElement).onclick = () => {
      const members = Array.from(this.em.role.entries()).filter(([id,r]) => r.role === 'Scout' || r.role === 'Guard').slice(0,3).map(([id])=>id);
      if (members.length >= 2) {
        this.em.createTask('expedition_form', { members }, 0.7);
        this.pushEventFeed('Yêu cầu Expedition');
      }
    };
    (this.expeditionEl.querySelector('#btn-exp-overlay') as HTMLButtonElement).onclick = () => {
      this.expeditionOverlay.style.display = this.expeditionOverlay.style.display === 'none' ? 'block' : 'none';
    };
  }

  renderTech() {
    const techs = (window as any).gameData?.techs || [];
    const unlocked = this.em.tech.unlocked;
    const active = this.em.tech.active;
    const list = techs.map((t: any) => {
      const u = unlocked.has(t.id);
      const prog = this.em.tech.progress[t.id] || 0;
      return `<div style="margin-bottom:4px; border-bottom:1px solid #233;">
        <b>${t.title}</b> [${u ? 'Unlocked' : (active===t.id ? 'Researching '+((prog/t.time)*100).toFixed(0)+'%' : 'Locked')}]
        <br><small>${t.description}</small>
        ${(!u && active!==t.id) ? `<button data-tech="${t.id}">Nghiên cứu</button>`:''}
      </div>`;
    }).join('');
    this.techEl.innerHTML = `<h3>Công Nghệ</h3><div style="max-height:160px; overflow:auto;">${list}</div>`;
    this.techEl.querySelectorAll('button[data-tech]').forEach(b => {
      b.addEventListener('click', () => {
        const id = (b as any).dataset.tech;
        this.techSystem.setActive(id);
        this.pushEventFeed('Bắt đầu nghiên cứu '+id);
      });
    });
  }
  renderEventFeed() {
    this.eventFeedEl.innerHTML = `<h3>Sự Kiện</h3><div class="feed">${this.feed.map(f=>`<div>${f}</div>`).join('')}</div>`;
  }
  renderCamera() {
    const acts = Array.from(this.em.role.entries()).slice(0,40);
    this.cameraEl.innerHTML = `<h3>Camera</h3>${acts.map(([id,r])=>`<button data-cam="${id}" class="mini">${r.role[0]}#${id}</button>`).join('')}`;
    this.cameraEl.querySelectorAll('button[data-cam]').forEach(b=>{
      b.addEventListener('click', ()=>{
        const id = parseInt((b as any).dataset.cam);
        this.render.setLeader(id);
        this.pushEventFeed('Camera -> '+id);
      });
    });
  }
  renderSaveLoad() {
    this.saveLoadEl.innerHTML = `<h3>Lưu/Tải</h3>
    <button id="btn-save">Lưu</button>
    <button id="btn-load">Tải</button>
    <button id="btn-redraw">Vẽ Lại</button>`;
    (this.saveLoadEl.querySelector('#btn-save') as HTMLButtonElement).onclick = () => (window as any).gameSave();
    (this.saveLoadEl.querySelector('#btn-load') as HTMLButtonElement).onclick = () => (window as any).gameLoad();
    (this.saveLoadEl.querySelector('#btn-redraw') as HTMLButtonElement).onclick = () => this.render.drawTiles();
  }
  renderSpectator() {
    this.spectatorEl.innerHTML = `<h3>Spectator</h3>
    <button id="btn-spec-connect">Kết nối</button>
    <button id="btn-spec-toggle">Bật/Tắt</button>`;
    (this.spectatorEl.querySelector('#btn-spec-connect') as HTMLButtonElement).onclick = () => {
      this.spectator.connect('ws://localhost:8091');
      this.pushEventFeed('Spectator connect');
    };
    (this.spectatorEl.querySelector('#btn-spec-toggle') as HTMLButtonElement).onclick = () => {
      this.spectator.setEnabled(!this.spectator.enabled);
      this.pushEventFeed('Spectator '+(this.spectator.enabled?'ON':'OFF'));
    };
  }
  renderModPanel() {
    this.modEl.innerHTML = `<h3>Mods</h3>
    <button id="btn-reload-mods">Reload Mods</button>`;
    (this.modEl.querySelector('#btn-reload-mods') as HTMLButtonElement).onclick = () => (window as any).reloadMods();
  }

  renderSearchPanel() {
    const categories = ['resources','items','buildings','monsters','events','techs','recipes'];
    const catSelect = categories.map(c => `<option value="${c}" ${c===this.searchCategory?'selected':''}>${c}</option>`).join('');
    this.searchPanel.innerHTML = `<h3>Tìm Kiếm</h3>
      <input id="search-query" placeholder="từ khóa / rarity:epic / tier:3" style="width:95%;" value="${this.searchQuery}"/>
      <select id="search-cat">${catSelect}</select>
      <button id="search-run">Tìm</button>
      <div style="max-height:160px; overflow:auto; font-size:11px; margin-top:4px;">${this.searchResults.map(r=>this.renderSearchResult(r)).join('') || '<i>Chưa có kết quả</i>'}</div>`;
    (this.searchPanel.querySelector('#search-run') as HTMLButtonElement).onclick = () => {
      const qEl = this.searchPanel.querySelector('#search-query') as HTMLInputElement;
      const cEl = this.searchPanel.querySelector('#search-cat') as HTMLSelectElement;
      this.searchQuery = qEl.value;
      this.searchCategory = cEl.value;
      this.executeSearch();
      this.renderSearchPanel();
    };
  }

  private renderSearchResult(r: any): string {
    if (!r) return '';
    if (r.id && r.title) return `<div><b>${r.id}</b> - ${r.title}<br><span>${r.description || ''}</span></div>`;
    if (r.id && r.label) return `<div><b>${r.id}</b> - ${r.label}<br><span>${r.description || ''}</span></div>`;
    return `<div><b>${r.id || 'entry'}</b></div>`;
  }

  private executeSearch() {
    const tokens = this.searchQuery.trim().toLowerCase().split(/\s+/).filter(t=>t);
    const filters: { key: string; val: string }[] = [];
    const free: string[] = [];
    for (const t of tokens) {
      const idx = t.indexOf(':');
      if (idx > 0) {
        filters.push({ key: t.slice(0, idx), val: t.slice(idx+1) });
      } else free.push(t);
    }
    let arr: any[] = [];
    if (this.searchCategory === 'resources') arr = this.data.resources;
    else if (this.searchCategory === 'items') arr = this.data.items;
    else if (this.searchCategory === 'buildings') arr = this.data.buildings;
    else if (this.searchCategory === 'monsters') arr = this.data.monsters;
    else if (this.searchCategory === 'events') arr = this.data.events;
    else if (this.searchCategory === 'techs') arr = this.data.techs;
    else if (this.searchCategory === 'recipes') arr = this.data.recipes;

    this.searchResults = arr.filter(entry => {
      for (const f of filters) {
        const kv = (entry as any)[f.key];
        if (kv === undefined) return false;
        if (typeof kv === 'number') {
          if (kv.toString() !== f.val) return false;
        } else if (typeof kv === 'string') {
          if (kv.toLowerCase() !== f.val) return false;
        } else return false;
      }
      if (free.length) {
        const text = JSON.stringify(entry).toLowerCase();
        for (const w of free) if (!text.includes(w)) return false;
      }
      return true;
    }).slice(0, 120);
  }

  renderAnalyticsPanel() {
    const a = this.em.analytics || {};
    const topProd = Object.entries(a.ema || {})
      .filter(([k]) => k.startsWith('prod:'))
      .sort((a,b)=> b[1].value - a[1].value)
      .slice(0,5)
      .map(([k,v])=> `${k.slice(5)}=${v.value.toFixed(1)}/m`).join(', ');
    this.analyticsPanel.innerHTML = `<h3>Analytics</h3>
      <div>Morale: ${a.morale?.toFixed?.(1) || 0} | Sanity: ${a.sanity?.toFixed?.(1) || 0}</div>
      <div>PathEff: ${(a.pathEfficiency||1).toFixed(2)} | Automation: ${(a.automation||0).toFixed(2)} | Logistics: ${(a.logistics||1).toFixed(2)}</div>
      <div>Expedition Success: ${(a.expeditionSuccess*100||0).toFixed(0)}%</div>
      <div>Active Recipes (unique tracked): ${Object.keys(a.activeRecipes||{}).length}</div>
      <div>Top Production: ${topProd || 'N/A'}</div>`;
  }

  renderExpeditionRealtime() {
    const exp = this.em.expeditions.find(e => e.realtime && e.status==='ongoing');
    if (!exp || !exp.realtime) {
      this.expeditionOverlay.innerHTML = '<b>No Active Expedition Map</b>';
      return;
    }
    const map = exp.realtime;
    const size = map.size;
    if (!map.canvas) {
      map.canvas = document.createElement('canvas');
      map.canvas.width = 160;
      map.canvas.height = 160;
      map.canvas.className = 'expedition-mini';
      this.expeditionOverlay.appendChild(map.canvas);
    }
    const ctx = map.canvas.getContext('2d')!;
    ctx.fillStyle = '#0a0f16'; ctx.fillRect(0,0,160,160);
    for (let y=0;y<size;y++){
      for (let x=0;x<size;x++){
        const v = map.terrain[y][x];
        ctx.fillStyle = v===1?'#203040':'#15202b';
        ctx.fillRect(x*10,y*10,10,10);
      }
    }
    ctx.fillStyle='#ffff66';
    ctx.fillRect(map.goal.x*10,map.goal.y*10,10,10);
    ctx.fillStyle='#66ffcc';
    ctx.fillRect(map.party.x*10,map.party.y*10,10,10);
    this.expeditionOverlay.innerHTML = `<b>Expedition #${exp.id}</b><br>Goal (${map.goal.x},${map.goal.y}) Party(${map.party.x},${map.party.y})<br>Status: ${map.done?'DONE':'RUNNING'}<br>`;
    this.expeditionOverlay.appendChild(map.canvas);
  }
}