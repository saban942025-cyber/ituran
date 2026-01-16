export interface FleetEvent {
  id: string;
  driver_name: string;
  event_type: 'PTO_OPEN' | 'PTO_CLOSE' | 'IDLE' | 'OFF_HOURS';
  event_timestamp: string;
  location: string;
  speed?: string;
}

export interface DriverStats {
  driver_name: string;
  total_km: number;
  idle_minutes: number;
  pto_count: number;
}
