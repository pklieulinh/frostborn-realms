import sys, inspect, pygame
from pathlib import Path
_THIS_FILE=Path(__file__).resolve()
for root in [_THIS_FILE.parent,_THIS_FILE.parent.parent,_THIS_FILE.parent.parent.parent]:
    if (root/"core").is_dir() and str(root) not in sys.path:
        sys.path.insert(0,str(root))
        
# Fix asset loader import path
if (_THIS_FILE.parent / "frostborn-realms").is_dir():
    sys.path.insert(0, str(_THIS_FILE.parent / "frostborn-realms"))
    
from assets.loader.asset_loader import AssetLoader
from core.ecs.world import World
from core.config import WORLD_SEED, TICK_INTERVAL_SEC
from core.simulation.tick_manager import TickManager
from core.systems import (
    defs_system,events_system,predator_spawn_system,wildlife_spawn_system,guard_system,predator_ai_system,
    leader_system,leader_def_system,task_system,movement_system,farm_system,housing_system,emotion_system,
    relationship_system,stress_system,morale_system,needs_system,crafting_system,portal_upgrade_system,
    combat_system,expedition_system,victory_system,telemetry_system,assignment_system,
    dialogue_system,deposit_system,forestry_system,heat_system,traits_system,
    population_system,health_regen_system,gather_haul_system,storage_system,construction_system,
    attribute_system,attribute_inject_system,skills_system,skills_xp_hooks,item_stack_system,
    blueprint_system,construction_def_system,colonist_growth_system,legacy_resource_convert_system,
    reproduction_system,threat_response_system,predator_loot_system,gather_balance_system,housing_capacity_system
)
from core.ai.leader import load_research_tree
from core.ui_data import gather_ui_state
from core.ecs.components import Identity, Profession, Role, Dialogue, FarmField, ResourceDeposit, ActivityState, WorkIntent, WorkStats

WIDTH, HEIGHT = 1640, 970
TILE=24
FONT_NAME="consolas"
try: KEY_F3=pygame.K_F3
except: KEY_F3=getattr(pygame,"K_f3",None)
RUNTIME_REQUIRED_IDS=["leader","worker","wood_node","storage","heat","site","portal","portal_gate","foundry","research_station","predator","guard","portal_gate_built","expedition_team","scholar","engineer","scout","soldier","wildlife","mine"]
PREGAME_HELP=["CHỌN LÃNH ĐẠO","Click/TAB chọn","ENTER/L xác nhận","1/2/3 Speed","H Heat | Q/Esc Thoát"]

class PygameRuntime:
    def __init__(self,screen,loader):
        self.screen=screen
        self.loader=loader
        self.world=World(seed=WORLD_SEED)
        self.world.bootstrap()
        load_research_tree(self.world)
        self.tick_manager=TickManager(TICK_INTERVAL_SEC)
        self.tick_manager.add_task(self.simulation_step)
        self.font_small=pygame.font.SysFont(FONT_NAME,14)
        self.font_medium=pygame.font.SysFont(FONT_NAME,16)
        self.font_large=pygame.font.SysFont(FONT_NAME,20)
        self.selected_eid=None
        self.show_heat=False
        self.show_telemetry=False
        self.speed_mult=1
    def simulation_step(self,tick_index:int,dt:float):
        w=self.world
        w.state.tick=tick_index
        defs_system(w)
        item_stack_system(w)
        legacy_resource_convert_system(w)
        heat_system(w)
        traits_system(w)
        if w.state.meta.get("pregame",False): return
        attribute_inject_system(w)
        population_system(w)
        housing_capacity_system(w)
        colonist_growth_system(w)
        reproduction_system(w)
        gather_balance_system(w)
        attribute_system(w)
        skills_xp_hooks(w)
        skills_system(w)
        threat_response_system(w)
        assignment_system(w)
        gather_haul_system(w)
        events_system(w)
        predator_spawn_system(w)
        wildlife_spawn_system(w)
        guard_system(w)
        predator_ai_system(w)
        leader_system(w, tick_index)
        leader_def_system(w)
        task_system(w)
        movement_system(w)
        construction_system(w)
        blueprint_system(w)
        construction_def_system(w)
        farm_system(w)
        housing_system(w)
        emotion_system(w)
        relationship_system(w)
        stress_system(w)
        morale_system(w)
        needs_system(w)
        crafting_system(w)
        portal_upgrade_system(w)
        combat_system(w)
        predator_loot_system(w)
        expedition_system(w)
        deposit_system(w)
        forestry_system(w)
        health_regen_system(w)
        storage_system(w)
        victory_system(w)
        telemetry_system(w)
        dialogue_system(w)
    def update(self,dt:float):
        self.tick_manager.set_speed_mult(self.speed_mult)
        self.tick_manager.step()
    def render(self):
        self._draw_grid()
        if self.show_heat: self._draw_heat_overlay()
        self._draw_entities()
        if self.world.state.meta.get("pregame",False):
            self._draw_pregame_overlay()
        else:
            ui_state=gather_ui_state(self.world)
            self._draw_side_panel(ui_state)
        if self.show_telemetry: self._draw_telemetry_panel()
    def _draw_grid(self):
        g=self.world.grid
        for x in range(g.width):
            for y in range(g.height):
                c=(28,44,60) if (x+y)%2==0 else (24,38,52)
                pygame.draw.rect(self.screen,c,(x*TILE,y*TILE,TILE,TILE))
    def _draw_heat_overlay(self):
        hm=self.world.state.meta.get("heat_map")
        if not hm: return
        surf=pygame.Surface((self.world.grid.width*TILE,self.world.grid.height*TILE),pygame.SRCALPHA)
        for x in range(self.world.grid.width):
            for y in range(self.world.grid.height):
                v=hm[x][y]
                if v<=0: continue
                color=(min(255,int(v)),min(255,int(v*0.5)),255-min(255,int(v)),110)
                pygame.draw.rect(surf,color,(x*TILE,y*TILE,TILE,TILE))
        self.screen.blit(surf,(0,0),special_flags=pygame.BLEND_RGBA_ADD)
    def _draw_entities(self):
        em=self.world.entities
        pos=em.get_component_store("Position")
        rend=em.get_component_store("Renderable")
        healths=em.get_component_store("Health")
        roles=em.get_component_store("Role")
        dialogues=em.get_component_store("Dialogue")
        farms=em.get_component_store("FarmField")
        deposits=em.get_component_store("ResourceDeposit")
        workstats=em.get_component_store("WorkStats")
        for eid in em.entities:
            if eid not in pos or eid not in rend: continue
            p=pos[eid]; r=rend[eid]
            sprite=self.loader.resolve(r.sprite)
            rect=pygame.Rect(p.x*TILE+2,p.y*TILE+2,TILE-4,TILE-4)
            if sprite: self.screen.blit(pygame.transform.smoothscale(sprite,(rect.width,rect.height)),rect.topleft)
            else: pygame.draw.rect(self.screen,(200,200,200),rect)
            if eid in healths:
                hp=healths[eid]
                ratio=max(0,min(1,hp.hp/hp.max_hp))
                bw=rect.width; fw=int(bw*ratio)
                pygame.draw.rect(self.screen,(40,40,40),(rect.left,rect.top-6,bw,4))
                pygame.draw.rect(self.screen,(int((1-ratio)*255),int(ratio*255),60),(rect.left,rect.top-6,fw,4))
            if eid in roles:
                ch=roles[eid].type[0].upper()
                self.screen.blit(self.font_small.render(ch,True,(255,255,255)),(rect.left,rect.bottom-12))
            if eid in farms and not self.world.state.meta.get("pregame",False):
                f=farms[eid]
                self.screen.blit(self.font_small.render(f"{int(f.growth_progress)}%",True,(120,255,120)),(rect.left,rect.bottom))
            if eid in deposits:
                d=deposits[eid]
                self.screen.blit(self.font_small.render(f"{d.resource_type[:2]}:{d.amount_remaining}",True,(200,210,140)),(rect.left,rect.top-18))
            if eid in dialogues and not self.world.state.meta.get("pregame",False):
                line=dialogues[eid].line
                if line: self.screen.blit(self.font_small.render(line,True,(255,255,160)),(rect.left,rect.top-18))
            if eid in workstats and roles.get(eid) and roles[eid].type=="Leader":
                ws=workstats[eid]
                bw=rect.width; val=int(bw*ws.fatigue)
                pygame.draw.rect(self.screen,(60,60,60),(rect.left,rect.bottom+2,bw,4))
                pygame.draw.rect(self.screen,(255,120,80),(rect.left,rect.bottom+2,val,4))
            if eid==self.selected_eid:
                pygame.draw.rect(self.screen,(255,255,0),rect,2)
    def _draw_pregame_overlay(self):
        g=self.world.grid; w=560; h=420
        surf=pygame.Surface((w,h),pygame.SRCALPHA)
        surf.fill((18,28,46,245))
        title=self.font_large.render("Chọn Leader",True,(255,255,255))
        surf.blit(title,(16,10))
        y=50
        for line in PREGAME_HELP:
            surf.blit(self.font_small.render(line,True,(200,220,240)),(16,y)); y+=18
        em=self.world.entities
        ids=em.get_component_store("Identity")
        prof=em.get_component_store("Profession")
        role=em.get_component_store("Role")
        cands=[eid for eid in ids.keys() if eid in role]
        cands.sort()
        if cands and self.selected_eid not in cands:
            self.selected_eid=cands[0]
        list_y=140
        for eid in cands:
            ident=ids[eid]; pr=prof.get(eid)
            col=(255,255,0) if eid==self.selected_eid else (220,220,220)
            line=f"#{eid} {ident.name} [{pr.main_class}/{pr.subclass}]"
            surf.blit(self.font_small.render(line,True,col),(16,list_y))
            list_y+=16
        if self.selected_eid and self.selected_eid in ids:
            ident=ids[self.selected_eid]; pr=prof.get(self.selected_eid)
            dx=300; dy=140
            surf.blit(self.font_medium.render(ident.name,True,(255,255,140)),(dx,dy)); dy+=24
            surf.blit(self.font_small.render(f"{pr.main_class}/{pr.subclass}",True,(200,220,255)),(dx,dy)); dy+=16
            surf.blit(self.font_small.render("ENTER / L confirm",True,(255,255,180)),(dx,dy))
        self.screen.blit(surf,(g.width*TILE//2 - w//2,g.height*TILE//2 - h//2))
    def _leader_working(self):
        em=self.world.entities
        roles=em.get_component_store("Role")
        acts=em.get_component_store("ActivityState")
        for eid,r in roles.items():
            if r.type=="Leader":
                act=acts.get(eid)
                return act and act.state in ("Working","Moving")
        return False
    def _draw_side_panel(self,ui_state):
        panel_x=self.world.grid.width*TILE+8
        panel_w=WIDTH-panel_x-8
        pygame.draw.rect(self.screen,(18,28,38),(panel_x-4,0,panel_w+8,HEIGHT))
        y=8
        tps_real=self.tick_manager.tps_real
        speed_line=f"Tick {ui_state['tick']} Speed:x{self.speed_mult} TPS:{tps_real:.0f}"
        self.screen.blit(self.font_large.render(speed_line,True,(255,255,255)),(panel_x,y)); y+=28
        res_line=" | ".join(f"{k}:{v}" for k,v in list(ui_state['resources'].items())[:12])
        for seg in self._wrap(res_line,panel_w):
            self.screen.blit(self.font_small.render(seg,True,(200,220,240)),(panel_x,y)); y+=16
        phase=self.world.state.meta.get("colony_phase",0)
        food_ticks=int(self.world.state.meta.get("food_ticks",0))
        farms=self.world.state.meta.get("farm_count",0)
        pending_farms=self.world.state.meta.get("farm_sites_pending",0)
        df=self.world.state.meta.get("desired_farms_calc",0)
        pop=self.world.state.meta.get("population",0)
        cap=self.world.state.meta.get("housing_capacity",0)
        free=cap-pop
        portals=self.world.state.portal_count
        births=self.world.state.meta.get("births_total",0)
        directive=self.world.state.meta.get("colony_directive","Normal")
        self.screen.blit(self.font_small.render(f"Phase:{phase} Dir:{directive} FoodTicks:{food_ticks} Births:{births}",True,(180,255,180)),(panel_x,y)); y+=16
        self.screen.blit(self.font_small.render(f"Farms:{farms}(+{pending_farms})/{df} Portals:{portals}",True,(200,255,200)),(panel_x,y)); y+=16
        self.screen.blit(self.font_small.render(f"Pop:{pop}/{cap} (+{free})",True,(200,200,255)),(panel_x,y)); y+=16
        storage_used=self.world.state.meta.get("storage_used",0)
        storage_cap=self.world.state.meta.get("storage_capacity",0)
        pressure=self.world.state.meta.get("storage_pressure",0)
        self.screen.blit(self.font_small.render(f"Storage:{storage_used}/{storage_cap} ({int(pressure*100)}%)",True,(200,220,160)),(panel_x,y)); y+=16
        roster=self._roster_summary()
        self.screen.blit(self.font_small.render(f"Roster {roster}",True,(200,220,255)),(panel_x,y)); y+=16
        rp_line=f"RP:{ui_state['research_points']} AR:{'Y' if ui_state['auto_research'] else 'N'}"
        self.screen.blit(self.font_small.render(rp_line,True,(200,255,180)),(panel_x,y)); y+=16
        y+=4
        self.screen.blit(self.font_medium.render("Decisions:",True,(255,255,255)),(panel_x,y)); y+=20
        for d in reversed(ui_state["decisions"][-10:]):
            self.screen.blit(self.font_small.render(f"{d['tick']} {d.get('chosen','')}",True,(230,230,230)),(panel_x,y)); y+=16
        y+=8
        self.screen.blit(self.font_medium.render("Events:",True,(255,255,255)),(panel_x,y)); y+=20
        for e in reversed(ui_state["events"][-10:]):
            self.screen.blit(self.font_small.render(f"{e['tick']} {e['type']}",True,(180,220,255)),(panel_x,y)); y+=16
    def _wrap(self,text,w):
        words=text.split(); lines=[]; cur=""
        for w2 in words:
            t=(cur+" "+w2).strip()
            if self.font_small.size(t)[0]<=w: cur=t
            else:
                if cur: lines.append(cur)
                cur=w2
        if cur: lines.append(cur)
        return lines
    def _roster_summary(self):
        intents=self.world.entities.get_component_store("WorkIntent")
        c={}
        for wi in intents.values():
            j=wi.job
            if j in ("Leader","Idle"): continue
            c[j]=c.get(j,0)+1
        return " ".join(f"{k}:{v}" for k,v in c.items())
    def select_tile(self,mx,my):
        gw=self.world.grid.width*TILE; gh=self.world.grid.height*TILE
        if mx>=gw or my>=gh: return
        tx=mx//TILE; ty=my//TILE
        pos=self.world.entities.get_component_store("Position")
        for eid,p in pos.items():
            if p.x==tx and p.y==ty:
                self.selected_eid=eid; return
    def confirm_leader(self):
        if not self.selected_eid: return
        self.world.start_game_with_leader(self.selected_eid)
    def _draw_telemetry_panel(self):
        snap=self.tick_manager.get_profile_snapshot()
        ema=snap["ema_ms"]
        lines=[f"{k[:14]:14} {v:5.2f} ms" for k,v in sorted(ema.items(),key=lambda kv:kv[1],reverse=True)]
        w=300; h=28+16*min(len(lines),25)
        surf=pygame.Surface((w,h),pygame.SRCALPHA)
        surf.fill((12,12,32,220))
        self.screen.blit(self.font_medium.render("Telemetry",True,(255,255,255)),(10,10))
        y=38
        for line in lines[:25]:
            surf.blit(self.font_small.render(line,True,(200,220,240)),(8,y)); y+=16
        self.screen.blit(surf,(10,10))

def load_assets():
    current=Path(__file__).parent.resolve()
    assets_dir=current/"assets"
    manifest=assets_dir/"assets_manifest.json"
    example=assets_dir/"assets_manifest.example.json"
    chosen=manifest if manifest.is_file() else (example if example.is_file() else None)
    loader=AssetLoader(base_dir=assets_dir,load_surfaces=True,placeholder_on_missing=True,allow_dynamic_placeholders=True)
    if chosen: loader.add_images_from_manifest_file(chosen)
    loader.load_all(); loader.ensure_ids(RUNTIME_REQUIRED_IDS)
    return loader

def main():
    pygame.init()
    screen=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Frozen Dominion – Build Governor Patch")
    loader=load_assets()
    rt=PygameRuntime(screen,loader)
    clock=pygame.time.Clock(); running=True
    while running:
        dt=clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.KEYDOWN:
                pre=rt.world.state.meta.get("pregame",False)
                if event.key in (pygame.K_ESCAPE,pygame.K_q): running=False
                elif event.key==pygame.K_h: rt.show_heat=not rt.show_heat
                elif KEY_F3 and event.key==KEY_F3: rt.show_telemetry=not rt.show_telemetry
                elif event.key==pygame.K_1: rt.speed_mult=1
                elif event.key==pygame.K_2: rt.speed_mult=3
                elif event.key==pygame.K_3: rt.speed_mult=10
                elif pre:
                    if event.key==pygame.K_TAB:
                        ids=sorted(list(rt.world.entities.get_component_store("Identity").keys()))
                        if ids:
                            if rt.selected_eid not in ids: rt.selected_eid=ids[0]
                            else:
                                i=ids.index(rt.selected_eid); rt.selected_eid=ids[(i+1)%len(ids)]
                    elif event.key in (pygame.K_RETURN,pygame.K_l):
                        rt.confirm_leader()
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                rt.select_tile(*event.pos)
        rt.update(dt)
        screen.fill((0,0,0))
        rt.render()
        pygame.display.flip()
    pygame.quit(); sys.exit(0)

if __name__=="__main__":
    main()