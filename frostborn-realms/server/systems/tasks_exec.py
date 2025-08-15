from ..ecs.world import World
from ..ecs.components import Role
from ..ai.tasks import assign_gather_task, process_task, assign_construction_tasks, convert_completed_sites

def task_system(world: World):
    em = world.entities
    role_store = em.get_component_store("Role")
    agent_store = em.get_component_store("TaskAgent")
    for eid, role in role_store.items():
        if role.type in ("Worker", "Guard", "Scout"):
            agent = agent_store.get(eid)
            if not agent:
                continue
            if not agent.current:
                assign_construction_tasks(world, eid)
            if not agent.current:
                assign_gather_task(world, eid)
            process_task(world, eid)
    convert_completed_sites(world)