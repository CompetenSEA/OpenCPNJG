export interface ChartDataset {
  id: string;
  title: string;
  bounds?: number[];
}

export interface ChartRegistry {
  base?: string[];
  enc?: { datasets: ChartDataset[] };
  geotiff?: { datasets: ChartDataset[] };
  [key: string]: any;
}

export async function fetchCharts(): Promise<ChartRegistry> {
  const resp = await fetch('/charts');
  return resp.json();
}
