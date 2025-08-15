import { Assets, Texture } from 'pixi.js';

export interface ImageDef {
  id: string;
  url: string;
  type?: string;
  frameWidth?: number;
  frameHeight?: number;
}
interface Manifest { images: ImageDef[] }

export class AssetLoader {
  private manifestPath = 'assets/asset-manifest.json'; // relative (respects Vite base)
  private images: ImageDef[] = [];
  private textures: Record<string, Texture> = {};
  private placeholder: Texture = this.buildPlaceholder();
  private failed: string[] = [];

  async loadAll() {
    const manifest = await this.fetchManifest();
    if (!manifest) {
      console.error('[AssetLoader] Manifest missing:', this.manifestPath);
      return;
    }
    this.images = manifest.images || [];
    const bundle: Record<string,string> = {};
    for (const im of this.images) if (!im.url.startsWith('/__missing__')) bundle[im.id] = im.url;
    try { Assets.addBundle('core', bundle); } catch {}
    for (const im of this.images) await this.loadImage(im);
    this.printSummary();
  }

  getTexture(id: string) { return this.textures[id]; }
  resolve(id: string): Texture { return this.textures[id] || this.placeholder; }
  listIds(){ return Object.keys(this.textures); }

  private async fetchManifest(): Promise<Manifest|null> {
    try {
      const res = await fetch(this.manifestPath);
      if (!res.ok) return null;
      return await res.json();
    } catch { return null; }
  }

  private async loadImage(im: ImageDef) {
    if (im.url.startsWith('/__missing__')) {
      this.textures[im.id] = this.placeholder;
      return;
    }
    try {
      const tex = await Assets.load(im.url);
      if (!this.valid(tex)) {
        console.warn('[AssetLoader] invalid texture', im.id, im.url);
        await this.diagnose(im.url);
        this.textures[im.id] = this.placeholder;
      } else {
        this.textures[im.id] = tex;
      }
    } catch (e:any) {
      console.warn('[AssetLoader] load error', im.id, im.url, e?.message || e);
      await this.diagnose(im.url);
      this.textures[im.id] = this.placeholder;
      this.failed.push(im.id);
    }
  }

  private async diagnose(url: string) {
    try {
      const res = await fetch(url, { method: 'GET' });
      const ct = res.headers.get('content-type') || '';
      const len = res.headers.get('content-length') || '?';
      if (!res.ok) {
        console.warn('[DIAG]', url, 'status', res.status, 'ct', ct, 'len', len);
        return;
      }
      let buf: ArrayBuffer;
      try { buf = await res.clone().arrayBuffer(); } catch { return; }
      const bytes = new Uint8Array(buf).slice(0, 64);
      const textProbe = new TextDecoder().decode(bytes);
      const hexSig = bytes.slice(0,8);
      const sigHex = Array.from(hexSig).map(b=>b.toString(16).padStart(2,'0')).join('');
      if (textProbe.startsWith('<!DOCTYPE') || textProbe.startsWith('<html')) {
        console.warn('[DIAG]', url, 'HTML_FALLBACK', 'ct', ct, 'len', len);
      } else if (sigHex !== '89504e470d0a1a0a') {
        console.warn('[DIAG]', url, 'NOT_PNG_SIG', sigHex, 'ct', ct, 'len', len);
      } else {
        console.warn('[DIAG]', url, 'PNG_SIG_OK lengthMaybe?', len, '→ decode step failed (possible corruption).');
      }
    } catch (e:any) {
      console.warn('[DIAG_FAIL]', url, e?.message || e);
    }
  }

  private valid(t: Texture | undefined): t is Texture {
    return !!t && !!t.baseTexture && t.baseTexture.valid && t.width > 0 && t.height > 0;
  }

  private buildPlaceholder(): Texture {
    const c = document.createElement('canvas'); c.width = 8; c.height = 8;
    const g = c.getContext('2d')!;
    for (let y=0;y<8;y++) for (let x=0;x<8;x++) {
      g.fillStyle = (x+y)%2===0 ? '#505860' : '#22282d';
      g.fillRect(x,y,1,1);
    }
    return Texture.from(c);
  }

  private printSummary() {
    console.log('[AssetLoader] SUMMARY total:', this.images.length, 'failedIds:', this.failed.length);
  }
}