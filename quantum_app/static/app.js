const gates = [];
const gateNames = ["H", "X", "Y", "Z", "S", "T", "RY", "CX"];
let selectedGate = "H";

const $ = (selector) => document.querySelector(selector);
const palette = $("#gate-palette");

gateNames.forEach((name) => {
  const button = document.createElement("button");
  button.className = `gate-button${name === selectedGate ? " active" : ""}`;
  button.textContent = name;
  button.addEventListener("click", () => {
    selectedGate = name;
    document.querySelectorAll(".gate-button").forEach((item) => item.classList.toggle("active", item.textContent === name));
    updateConditionalFields();
  });
  palette.append(button);
});

function numQubits() {
  return Number($("#qubit-count").value);
}

function updateQubitSelectors() {
  const options = Array.from({ length: numQubits() }, (_, index) => `<option value="${index}">q${index}</option>`).join("");
  $("#target-qubit").innerHTML = options;
  $("#control-qubit").innerHTML = options;
  if (numQubits() > 1) $("#target-qubit").value = "1";
}

function updateConditionalFields() {
  $("#control-field").hidden = selectedGate !== "CX";
  $("#angle-field").hidden = selectedGate !== "RY";
}

function addGate() {
  const target = Number($("#target-qubit").value);
  if (selectedGate === "CX") {
    const control = Number($("#control-qubit").value);
    if (control === target) {
      $("#error").textContent = "CX の制御と対象には別の qubit を選んでください。";
      return;
    }
    gates.push({ gate: "CX", control, target });
  } else if (selectedGate === "RY") {
    gates.push({ gate: "RY", qubit: target, angle: Number($("#angle").value) });
  } else {
    gates.push({ gate: selectedGate, qubit: target });
  }
  runSimulation();
}

function gateOnWire(gate, qubit) {
  if (gate.gate === "CX") {
    if (gate.control === qubit) return "●";
    if (gate.target === qubit) return "⊕";
    return "";
  }
  return gate.qubit === qubit ? gate.gate : "";
}

function renderCircuit() {
  $("#gate-count").textContent = `${gates.length} gate${gates.length === 1 ? "" : "s"}`;
  $("#circuit").innerHTML = Array.from({ length: numQubits() }, (_, qubit) => `
    <div class="wire">
      <span class="wire-label">q${qubit}</span>
      <div class="wire-line"><div class="circuit-gates">
        ${gates.map((gate) => {
          const label = gateOnWire(gate, qubit);
          return `<span class="circuit-gate${label ? "" : " empty"}">${label || "."}</span>`;
        }).join("")}
      </div></div>
    </div>`).join("");
}

function renderResults(data) {
  const visibleStates = data.states.filter((state) => state.probability > 0.0000001);
  $("#probabilities").innerHTML = visibleStates.map((state) => `
    <div class="probability-row">
      <span class="state">|${state.state}⟩</span>
      <div class="bar-track"><div class="bar" style="width:${state.probability * 100}%"></div></div>
      <span class="value">${(state.probability * 100).toFixed(2)}%</span>
    </div>`).join("");

  const entries = Object.entries(data.counts);
  const maxCount = Math.max(...entries.map(([, count]) => count));
  $("#measurements").innerHTML = `<div class="measurement-grid">${entries.map(([state, count]) => `
    <div class="measure-column">
      <div class="measure-bar" style="height:${count / maxCount * 150}px"></div>
      <small>${count}</small><span class="state">${state}</span>
    </div>`).join("")}</div>`;
}

async function runSimulation() {
  $("#error").textContent = "";
  renderCircuit();
  try {
    const response = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ num_qubits: numQubits(), gates, shots: 1024 }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "シミュレーションに失敗しました。");
    renderResults(data);
  } catch (error) {
    $("#error").textContent = error.message;
  }
}

$("#add-gate").addEventListener("click", addGate);
$("#clear").addEventListener("click", () => { gates.length = 0; runSimulation(); });
$("#bell-state").addEventListener("click", () => {
  $("#qubit-count").value = Math.max(2, numQubits());
  updateQubitSelectors();
  gates.length = 0;
  gates.push({ gate: "H", qubit: 0 }, { gate: "CX", control: 0, target: 1 });
  runSimulation();
});
$("#qubit-count").addEventListener("change", () => {
  gates.length = 0;
  updateQubitSelectors();
  runSimulation();
});
$("#angle").addEventListener("input", (event) => { $("#angle-output").textContent = `${event.target.value} rad`; });

updateQubitSelectors();
updateConditionalFields();
runSimulation();
