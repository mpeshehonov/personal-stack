import fs from "fs/promises";
import path from "path";

const DATA_DIR = process.env.VISIT_COUNTER_PATH
  ? path.dirname(process.env.VISIT_COUNTER_PATH)
  : path.join(process.cwd(), "data");
const COUNTER_FILE =
  process.env.VISIT_COUNTER_PATH || path.join(DATA_DIR, "visits.json");

type VisitData = {
  total: number;
};

async function readCounter(): Promise<VisitData> {
  try {
    const raw = await fs.readFile(COUNTER_FILE, "utf-8");
    const data = JSON.parse(raw) as Partial<VisitData>;
    return { total: Math.max(0, Number(data.total) || 0) };
  } catch {
    return { total: 0 };
  }
}

async function writeCounter(data: VisitData): Promise<void> {
  await fs.mkdir(DATA_DIR, { recursive: true });
  await fs.writeFile(COUNTER_FILE, JSON.stringify(data), "utf-8");
}

export async function getVisitCount(): Promise<number> {
  const data = await readCounter();
  return data.total;
}

export async function incrementVisitCount(): Promise<number> {
  const data = await readCounter();
  data.total += 1;
  await writeCounter(data);
  return data.total;
}
