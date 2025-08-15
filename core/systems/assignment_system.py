from ..ecs.world import World
from ..ecs.components import WorkIntent, Profession, Role, Skills, Attributes

SKILL_JOB_MAP = {
    "Builder":"Construction",
    "Farmer":"Plants",
    "Gatherer":"Plants",
    "Miner":"Mining",
    "Hunter":"Shooting",
    "Herder":"Animals",
    "Hauler":"Construction",
    "Forester":"Plants",
}

def assignment_system(world: World):
    if world.state.meta.get("pregame", False): return
    em=world.entities
    intents=em.get_component_store("WorkIntent")
    profs=em.get_component_store("Profession")
    roles=em.get_component_store("Role")
    skills=em.get_component_store("Skills")
    attrs=em.get_component_store("Attributes")
    deposits=em.get_component_store("ResourceDeposit")
    pens=em.get_component_store("AnimalPen")
    sites=em.get_component_store("ConstructionSite")

    pop=sum(1 for r in roles.values() if r.type in ("Worker","Leader","Guard","Scholar","Engineer","Scout","Soldier"))
    desired_farms=world.state.meta.get("desired_farms_calc",1)
    farm_slots=min(desired_farms,max(1,pop//6))
    miner_slots=min(max(1,len(deposits)),max(1,pop//5)) if deposits else 0
    builder_slots=max(1,min(4,len([s for s in sites.values() if not s.complete])+1))
    herder_slots=max(0,len(pens))
    gatherer_slots=max(1,pop//3)
    hunter_slots=1
    forester_slots=1 if world.state.meta.get("colony_phase",0)>=2 else 0

    hauling_backlog=world.state.meta.get("hauling_backlog",0.0)
    storage_pressure=world.state.meta.get("storage_pressure",0.0)
    hauler_slots=0
    if hauling_backlog>0.5 or storage_pressure>0.8: hauler_slots=max(1,pop//6)
    if hauling_backlog>1.5: hauler_slots=max(2,pop//5)

    directive=world.state.meta.get("colony_directive","Normal")
    predators=world.state.meta.get("threat_predators",0)
    if directive=="Defend":
        hunter_slots=max(2,pop//4)
    elif directive=="FocusPredators":
        hunter_slots=max(2,max(2,int(pop*0.4)))
    elif directive=="Retreat":
        hunter_slots=0
        builder_slots=max(1,builder_slots-1)
        gatherer_slots=max(1,gatherer_slots-1)

    slot_order=[
        ("Builder",builder_slots),
        ("Farmer",farm_slots),
        ("Miner",miner_slots),
        ("Forester",forester_slots),
        ("Herder",herder_slots),
        ("Gatherer",gatherer_slots),
        ("Hauler",hauler_slots),
        ("Hunter",hunter_slots),
    ]
    assigned={k:0 for k,_ in slot_order}
    leader_hands_on=world.state.meta.get("leader_hands_on",True)
    leader_id=None
    for eid,r in roles.items():
        if r.type=="Leader": leader_id=eid; break

    for eid,intent in intents.items():
        if eid==leader_id and not leader_hands_on:
            intent.job="Leader"; continue
        if intent.job in assigned and assigned[intent.job]<dict(slot_order)[intent.job]:
            assigned[intent.job]+=1
        else:
            if eid==leader_id: intent.job="Leader"
            else: intent.job="Idle"

    def job_score(eid, job):
        base=1.0
        pr=profs.get(eid)
        if pr:
            if job=="Builder" and pr.main_class in ("Engineer","Worker"): base+=0.7
            if job=="Miner" and pr.main_class in ("Worker","Engineer"): base+=0.4
            if job=="Farmer" and pr.main_class=="Worker": base+=0.3
            if job=="Hunter" and pr.main_class=="Scout": base+=0.6
            if job=="Hauler" and pr.subclass=="Lumberjack": base+=0.2
        skname=SKILL_JOB_MAP.get(job)
        if skname and eid in skills:
            lvl=skills[eid].levels.get(skname,0)
            base += lvl*0.08
            passion=skills[eid].passions.get(skname,"None")
            if passion=="Minor": base+=0.2
            elif passion=="Major": base+=0.4
        if job=="Hauler" and eid in attrs:
            base += attrs[eid].hauling*0.6 + attrs[eid].stamina*0.3
        if job=="Gatherer" and eid in attrs:
            base += attrs[eid].strength*0.3 + attrs[eid].agility*0.25 + attrs[eid].botany*0.25
        return base

    for eid,intent in intents.items():
        if intent.job!="Idle": continue
        if eid==leader_id and not leader_hands_on:
            intent.job="Leader"; continue
        best=None; best_score=-1
        for job,need in slot_order:
            if assigned[job]>=need: continue
            sc=job_score(eid,job)
            if sc>best_score:
                best_score=sc; best=job
        if best:
            intent.job=best
            assigned[best]+=1
        else:
            intent.job="Gatherer" if assigned["Gatherer"]<dict(slot_order)["Gatherer"] else "Idle"

    if leader_id and leader_hands_on and predators>0 and directive in ("Defend","FocusPredators"):
        lint=intents.get(leader_id)
        if lint and lint.job not in ("Hunter","Builder"):
            lint.job="Hunter"