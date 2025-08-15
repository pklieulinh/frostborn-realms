class AssetMap:
    def __init__(self, loader):
        self.loader = loader
    def npc_role_texture(self, role: str) -> str:
        if role in ("Leader", "Worker", "Scout", "Guard"):
            return "chars_settlers"
        if role in ("Monster", "Goblin"):
            return "chars_monsters"
        return "chars_settlers"
    def portal_texture(self) -> str:
        return "fx_portal_glow"
    def resource_icon(self) -> str:
        return "icons_resources"
    def frame_panel(self) -> str:
        return "ui_frame_panel"