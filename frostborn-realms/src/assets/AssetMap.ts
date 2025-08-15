import { AssetLoader } from './AssetLoader';

export class AssetMap {
  constructor(private loader: AssetLoader) {}
  npcRoleTexture(role: string): string | null {
    if (role === 'Leader' || role === 'Worker' || role === 'Scout' || role === 'Guard')
      return this.loader.getTexture('chars_settlers') ? 'chars_settlers' : null;
    if (role === 'Monster' || role === 'Goblin')
      return this.loader.getTexture('chars_monsters') ? 'chars_monsters' : null;
    return null;
  }
  buildingTexture(id: string): string | null {
    if (id.includes('portal') && this.loader.getTexture('fx_portal_glow')) return 'fx_portal_glow';
    if (this.loader.getTexture('tiles_dungeon_base')) return 'tiles_dungeon_base';
    if (this.loader.getTexture('tiles_ice_world')) return 'tiles_ice_world';
    return null;
  }
  portalTexture() { return this.loader.getTexture('fx_portal_glow') ? 'fx_portal_glow' : null; }
  resourceNodeTexture(_resourceId: string): string | null {
    if (this.loader.getTexture('icons_resources')) return 'icons_resources';
    return this.loader.getTexture('icons_items') ? 'icons_items' : null;
  }
  framePanelTexture(): string | null {
    return this.loader.getTexture('ui_frame_panel') ? 'ui_frame_panel' : null;
  }
}