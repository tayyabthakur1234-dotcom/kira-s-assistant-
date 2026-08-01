export interface BatteryStatus {
  supported: boolean;
  level: number | null; // 0 to 100
  charging: boolean | null;
  statusText: string;
}

/**
 * Helper function to fetch the user's system battery level and charging state.
 * Uses the Web Battery Status API if available in the user's browser environment.
 */
export async function fetchBatteryStatus(): Promise<BatteryStatus> {
  try {
    if ('getBattery' in navigator && typeof (navigator as any).getBattery === 'function') {
      const battery = await (navigator as any).getBattery();
      const level = Math.round((battery.level ?? 1) * 100);
      const charging = Boolean(battery.charging);
      const statusText = `${level}%${charging ? ' (Charging)' : ''}`;
      return {
        supported: true,
        level,
        charging,
        statusText,
      };
    }
  } catch (err) {
    console.warn('[battery] Battery Status API error or unsupported:', err);
  }

  return {
    supported: false,
    level: null,
    charging: null,
    statusText: 'N/A',
  };
}
