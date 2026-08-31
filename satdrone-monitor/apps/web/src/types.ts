export interface ServiceStatus {
  status: "operational" | "degraded";
  services: Record<string, "operational" | "unavailable">;
}

export interface Anomaly {
  id: string;
  type: string;
  confidence: number;
  longitude: number;
  latitude: number;
  severity: "critical" | "warning";
}

