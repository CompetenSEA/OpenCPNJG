export function encSource(id: string) {
  return {
    type: 'vector',
    tiles: [`/tiles/enc/${id}/{z}/{x}/{y}`],
  };
}
