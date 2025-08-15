type Handler = (data: any) => void;
export class EventBus {
  private map = new Map<string, Set<Handler>>();
  on(event: string, handler: Handler) {
    if (!this.map.has(event)) this.map.set(event, new Set());
    this.map.get(event)!.add(handler);
  }
  off(event: string, handler: Handler) {
    const set = this.map.get(event);
    if (set) set.delete(handler);
  }
  emit(event: string, data: any) {
    const set = this.map.get(event);
    if (set) for (const h of set) h(data);
  }
}