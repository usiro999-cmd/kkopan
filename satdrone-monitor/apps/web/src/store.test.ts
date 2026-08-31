import { afterEach, describe, expect, it } from "vitest";
import { useOperationsStore } from "./store";
import type { Anomaly } from "./types";

const anomaly: Anomaly = {
  id: "anomaly-1",
  type: "solar-defect",
  confidence: 0.94,
  longitude: 139.75,
  latitude: 35.68,
  severity: "critical",
};

afterEach(() => {
  useOperationsStore.getState().selectAnomaly(null);
});

describe("operations store", () => {
  it("tracks the selected anomaly", () => {
    useOperationsStore.getState().selectAnomaly(anomaly);

    expect(useOperationsStore.getState().selectedAnomaly).toEqual(anomaly);
  });
});

