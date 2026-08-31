import { create } from "zustand";
import type { Anomaly } from "./types";

interface OperationsState {
  selectedAnomaly: Anomaly | null;
  selectAnomaly: (anomaly: Anomaly | null) => void;
}

export const useOperationsStore = create<OperationsState>((set) => ({
  selectedAnomaly: null,
  selectAnomaly: (selectedAnomaly) => set({ selectedAnomaly }),
}));

