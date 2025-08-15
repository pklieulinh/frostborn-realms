from enum import IntEnum
from typing import Dict
from ..ecs.world import World

class ColonyPhase(IntEnum):
    BOOTSTRAP = 0
    STABILIZE_FOOD = 1
    INDUSTRY = 2
    RESEARCH = 3
    PORTAL = 4
    ASCENSION = 5

def determine_phase(world: World, counts: Dict[str,int], food_days: float, pop: int) -> ColonyPhase:
    portals = world.state.portal_count
    research_stations = counts.get("ResearchStation",0)
    farms = counts.get("FarmPlot",0)
    foundries = counts.get("Foundry",0)
    # Ascension placeholder: khi đủ portal + research
    if portals >= world.state.meta.get("ascension_portal_req", 3) and research_stations >= 1 and food_days >= world.state.meta.get("phase_food_goal", 1200):
        return ColonyPhase.ASCENSION
    if portals > 0 or (research_stations >= 1 and food_days >= world.state.meta.get("phase_food_goal", 1200)):
        return ColonyPhase.PORTAL
    if research_stations >= 1 and foundries >= 1 and food_days >= world.state.meta.get("phase_food_min", 800):
        return ColonyPhase.RESEARCH
    if foundries >= 1 and food_days >= world.state.meta.get("phase_food_min", 800):
        return ColonyPhase.INDUSTRY
    if farms >= max(1, pop//6) and food_days >= world.state.meta.get("phase_food_min", 800):
        return ColonyPhase.INDUSTRY  # early promotion if strong food
    if farms >= 1 or food_days >= world.state.meta.get("phase_food_bootstrap_exit", 400):
        return ColonyPhase.STABILIZE_FOOD
    return ColonyPhase.BOOTSTRAP