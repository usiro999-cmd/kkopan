import type { ServiceStatus } from "./types";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchSystemStatus(): Promise<ServiceStatus> {
  const response = await fetch(`${apiUrl}/api/v1/system/status`);
  if (!response.ok) {
    throw new Error(`Status request failed with ${response.status}`);
  }
  return response.json() as Promise<ServiceStatus>;
}

