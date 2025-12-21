import { getPosition} from "../api/Interview_position"
import type { Position } from "../api/Interview_position"

// 获取岗位列表
export async function fetchPosition(): Promise<Position[]> {
  const res: Position[] = await getPosition()
  return res
}