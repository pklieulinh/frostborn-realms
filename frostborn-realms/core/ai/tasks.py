# (ĐÃ CHỈNH – bổ sung stubs cũ ở cuối. PHẦN LOGIC CHÍNH GIỮ NGUYÊN BẢN C4.3 / C4.2 TUỲ THEO NHÁNH.)
from ..ecs.world import World
from ..ecs.components import (ResourceNode, ResourceInventory, ConstructionSite, Building,
                              FarmField, AnimalPen, ActivityState, WorkIntent,
                              Movement, Position, Role, Health,
                              ResourceDeposit, Sapling, WorkStats, EmotionState, PortalGate)
from ..ai.pathfinding import a_star
from random import randint

def _performance(world: World, eid: int):
    emos = world.entities.get_component_store("EmotionState")
    wstats = world.entities.get_component_store("WorkStats")
    mood = emos[eid].mood if eid in emos else 0.7
    fatigue = wstats[eid].fatigue if eid in wstats else 0.0
    stress = wstats[eid].stress if eid in wstats else 0.0
    perf = (0.9 + mood*0.35) * (1 - 0.45*fatigue) * (1 - 0.35*stress)
    if perf < 0.3: perf = 0.3
    if perf > 1.6: perf = 1.6
    return perf

def assign_tasks(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    intents = em.get_component_store("WorkIntent")
    acts = em.get_component_store("ActivityState")
    pos = em.get_component_store("Position")
    sites = em.get_component_store("ConstructionSite")
    fields = em.get_component_store("FarmField")
    pens = em.get_component_store("AnimalPen")
    nodes = em.get_component_store("ResourceNode")
    roles = em.get_component_store("Role")
    deposits = em.get_component_store("ResourceDeposit")
    saplings = em.get_component_store("Sapling")
    wildlife_targets = [eid for eid,r in roles.items() if r.type=="Wildlife"]
    for eid, intent in intents.items():
        if intent.job in ("Idle","Leader"): continue
        if eid not in pos: continue
        act = acts.setdefault(eid, ActivityState())
        if act.state in ("Moving","Working","Delivering"): continue
        job = intent.job
        if job == "Builder":
            target = _pick_site(sites); 
            if target: _move_to(world,eid,target); continue
        if job == "Farmer":
            fid = _pick_field(fields); 
            if fid: _move_to(world,eid,fid); continue
        if job == "Herder":
            pid = _pick_pen(pens); 
            if pid: _move_to(world,eid,pid); continue
        if job == "Gatherer":
            nid = _pick_node(nodes); 
            if nid: _move_to(world,eid,nid); continue
        if job == "Hunter":
            wid = _pick_wildlife(wildlife_targets,pos,pos.get(eid))
            if wid: _move_to(world,eid,wid); continue
        if job == "Miner":
            mid = _pick_deposit(deposits)
            if mid: _move_to(world,eid,mid); continue
        if job == "Forester":
            if _need_more_wood_nodes(world,nodes,saplings):
                spot = _find_free_adjacent(world,pos[eid].x,pos[eid].y,nodes,saplings)
                if spot: _plant_sapling(world,spot)
        if job == "Explorer":
            nid = _pick_node(nodes)
            if nid: _move_to(world,eid,nid); continue

def process_work(world: World):
    em = world.entities
    acts = em.get_component_store("ActivityState")
    intents = em.get_component_store("WorkIntent")
    invs = em.get_component_store("ResourceInventory")
    sites = em.get_component_store("ConstructionSite")
    nodes = em.get_component_store("ResourceNode")
    fields = em.get_component_store("FarmField")
    pens = em.get_component_store("AnimalPen")
    roles = em.get_component_store("Role")
    healths = em.get_component_store("Health")
    deposits = em.get_component_store("ResourceDeposit")
    for eid, act in acts.items():
        if act.state != "Working": continue
        if eid not in intents: continue
        perf = _performance(world, eid)
        job = intents[eid].job
        if job == "Builder" and act.target in sites:
            site = sites[act.target]
            need = _needed_resource(site)
            if need:
                inv = invs.get(eid)
                if inv and inv.stored.get(need,0) > 0:
                    site.delivered[need] = site.delivered.get(need,0)+1
                    inv.stored[need]-=1
                else:
                    _pull_resource(world,eid,need)
            else:
                site.progress += 0.055 * perf
                if site.progress >= 1.0:
                    site.complete = True
                    act.state="Idle"; act.target=None
        elif job == "Gatherer" and act.target in nodes:
            node = nodes[act.target]
            node.amount -= max(1,int(perf))
            inv = invs.get(eid)
            if inv:
                inv.stored[node.rtype] = inv.stored.get(node.rtype,0)+max(1,int(perf))
            if node.amount <= 0:
                del nodes[act.target]
            act.state="Idle"; act.target=None
        elif job == "Farmer" and act.target in fields:
            fields[act.target].growth_progress += 0.45 * perf
            act.state="Idle"; act.target=None
        elif job == "Herder" and act.target in pens:
            pens[act.target].husbandry_timer += int(4 * perf)
            act.state="Idle"; act.target=None
        elif job == "Hunter" and act.target in roles and roles[act.target].type=="Wildlife":
            wid = act.target
            if wid in healths:
                healths[wid].hp -= int(12 * perf)
                if healths[wid].hp <=0:
                    _harvest_wildlife(world,eid,wid); world.entities.destroy(wid)
                    act.state="Idle"; act.target=None
            else:
                _harvest_wildlife(world,eid,wid); world.entities.destroy(wid)
                act.state="Idle"; act.target=None
        elif job == "Miner" and act.target in deposits:
            dep = deposits[act.target]
            inv = invs.get(eid)
            if not inv:
                act.state="Idle"; act.target=None; continue
            take = min(int(dep.yield_per_cycle * perf), dep.amount_remaining)
            if take <=0: take = 1
            dep.amount_remaining -= take
            inv.stored[dep.resource_type] = inv.stored.get(dep.resource_type,0)+take
            act.state="Idle"; act.target=None
        else:
            act.state="Idle"

def movement_step(world: World):
    em = world.entities
    acts = em.get_component_store("ActivityState")
    pos_store = em.get_component_store("Position")
    mov_store = em.get_component_store("Movement")
    for eid, act in acts.items():
        if act.state == "Moving" and eid in mov_store and eid in pos_store:
            mv = mov_store[eid]
            if not mv.path:
                act.state = "Working"; act.changed_tick = world.state.tick; continue
            nx, ny = mv.path[0]
            if pos_store[eid].x == nx and pos_store[eid].y == ny:
                mv.path.pop(0); continue
            if world.grid.walkable(nx, ny):
                pos_store[eid].x = nx
                pos_store[eid].y = ny
                mv.path.pop(0)
            else:
                mv.path = a_star(world.grid, (pos_store[eid].x,pos_store[eid].y), mv.target)[:30]
            if not mv.path:
                act.state = "Working"; act.changed_tick = world.state.tick

def convert_completed_sites(world: World):
    # Kept in leader patch (managed in separate convert in previous milestone), no-op here.
    pass

def _move_to(world: World, eid: int, target_eid: int):
    em = world.entities
    pos = em.get_component_store("Position")
    mov = em.get_component_store("Movement")
    acts = em.get_component_store("ActivityState")
    if eid not in pos or target_eid not in pos or eid not in mov: return
    start = (pos[eid].x,pos[eid].y); goal = (pos[target_eid].x,pos[target_eid].y)
    path = a_star(world.grid,start,goal)
    mv = mov[eid]; mv.target=goal; mv.path=path
    act = acts[eid]; act.state="Moving"; act.target=target_eid; act.target_pos=goal; act.changed_tick=world.state.tick

def _pick_site(sites):
    for sid,s in sites.items():
        if not s.complete: return sid
    return None
def _pick_field(fields):
    for fid in fields.keys(): return fid
    return None
def _pick_pen(pens):
    for pid in pens.keys(): return pid
    return None
def _pick_node(nodes):
    best=None; best_amt=0
    for nid,n in nodes.items():
        if n.amount>best_amt: best=nid; best_amt=n.amount
    return best
def _needed_resource(site: ConstructionSite):
    for r,amt in site.needed.items():
        if site.delivered.get(r,0)<amt: return r
    return None
def _pull_resource(world: World, worker_id: int, rtype: str):
    em=world.entities; invs=em.get_component_store("ResourceInventory")
    worker_inv=invs.get(worker_id)
    if not worker_inv: return
    for eid,inv in invs.items():
        if inv is worker_inv: continue
        have=inv.stored.get(rtype,0)
        if have>0:
            inv.stored[rtype]-=1
            worker_inv.stored[rtype]=worker_inv.stored.get(rtype,0)+1
            return
def _pick_wildlife(wlist,pos_store,p):
    if not p or not wlist: return None
    best=None; bestd=1e9
    for wid in wlist:
        if wid not in pos_store: continue
        wp=pos_store[wid]; d=abs(wp.x-p.x)+abs(wp.y-p.y)
        if d<bestd: bestd=d; best=wid
    return best
def _harvest_wildlife(world: World, hunter_id: int, wid: int):
    invs=world.entities.get_component_store("ResourceInventory")
    if hunter_id not in invs: return
    inv=invs[hunter_id]; meat=randint(2,4); hide=randint(0,1)
    inv.stored["MeatRaw"]=inv.stored.get("MeatRaw",0)+meat
    if hide>0: inv.stored["HideRough"]=inv.stored.get("HideRough",0)+hide
def _pick_deposit(deposits):
    for eid,dep in deposits.items():
        if dep.amount_remaining>0: return eid
    return None
def _need_more_wood_nodes(world,nodes,saplings):
    existing=sum(1 for n in nodes.values() if n.rtype=="WoodCold")+len(saplings)
    pop=world.state.meta.get("population",0)
    target=max(6,pop*2)
    return existing<target
def _find_free_adjacent(world,x,y,nodes,saplings):
    grid=world.grid
    occupied={(p.x,p.y) for p in world.entities.get_component_store("Position").values()}
    for radius in range(1,6):
        for dx in range(-radius,radius+1):
            for dy in range(-radius,radius+1):
                nx,ny=x+dx,y+dy
                if not grid.in_bounds(nx,ny): continue
                if not grid.walkable(nx,ny): continue
                if (nx,ny) in occupied: continue
                return (nx,ny)
    return None
def _plant_sapling(world,spot):
    from ..ecs.components import Sapling, Position, Renderable
    from ..util.id_gen import GLOBAL_ID_GEN
    eid=world.entities.create(GLOBAL_ID_GEN.next())
    world.entities.add_component(eid,"Position",Position(spot[0],spot[1]))
    world.entities.add_component(eid,"Renderable",Renderable("wood_node"))
    world.entities.add_component(eid,"Sapling",Sapling(ticks_to_mature=300+randint(-40,40),wood_amount=randint(50,95)))

# Backward compatibility stubs (old code might import these)
def assign_gather_task(world, eid): return
def process_task(world, eid): return
def assign_construction_tasks(world, eid): return
