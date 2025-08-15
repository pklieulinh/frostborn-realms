export interface ImageEntry {
  id: string;
  url: string;
  type: string;
  frameWidth?: number;
  frameHeight?: number;
}

export interface RawManifest {
  images: ImageEntry[];
}

export interface LoadedTextureInfo extends ImageEntry {
  baseTextureKey: string;
}

export class AssetManifest {
  images: ImageEntry[] = [];
  constructor(raw: RawManifest) {
    this.images = raw.images;
  }
  static async fetch(url = '/assets/asset-manifest.json') {
    const res = await fetch(url);
    if (!res.ok) throw new Error('Cannot load manifest ' + url);
    const json = await res.json() as RawManifest;
    return new AssetManifest(json);
  }
}