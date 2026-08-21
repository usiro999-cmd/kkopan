const $ = (selector) => document.querySelector(selector);

function parseCircuit(source) {
  return source.split("\n").map((line) => line.trim()).filter(Boolean).map((line, index) => {
    const [name, first, second] = line.split(/\s+/);
    const gate = name.toUpperCase();
    if (gate === "CX") {
      if (first === undefined || second === undefined) throw new Error(`${index + 1}行目: CX control target`);
      return { gate, control: Number(first), target: Number(second) };
    }
    if (gate === "RY") {
      if (first === undefined || second === undefined) throw new Error(`${index + 1}行目: RY qubit angle`);
      return { gate, qubit: Number(first), angle: Number(second) };
    }
    if (first === undefined) throw new Error(`${index + 1}行目: ${gate} qubit`);
    return { gate, qubit: Number(first) };
  });
}

function renderStates(selector, states) {
  const visible = states.filter((state) => state.probability > 0.0000001);
  $(selector).innerHTML = visible.map((state) => `
    <div class="probability-row">
      <span class="state">|${state.state}⟩</span>
      <div class="bar-track"><div class="bar" style="width:${state.probability * 100}%"></div></div>
      <span class="value">${(state.probability * 100).toFixed(2)}%</span>
    </div>`).join("");
}

async function compare() {
  $("#error").textContent = "";
  try {
    const numQubits = Number($("#qubit-count").value);
    const body = {
      left: { num_qubits: numQubits, gates: parseCircuit($("#left-gates").value), shots: 1024 },
      right: { num_qubits: numQubits, gates: parseCircuit($("#right-gates").value), shots: 1024 },
    };
    const response = await fetch("/api/twin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "ツイン実行に失敗しました。");
    renderStates("#left-results", data.left.states);
    renderStates("#right-results", data.right.states);
    $("#similarity").textContent = `${(data.comparison.similarity * 100).toFixed(2)}%`;
    $("#distance").textContent = data.comparison.total_variation_distance.toFixed(4);
  } catch (error) {
    $("#error").textContent = error.message;
  }
}

$("#compare").addEventListener("click", compare);
$("#preset").addEventListener("click", () => {
  $("#qubit-count").value = "2";
  $("#left-gates").value = "H 0\nCX 0 1";
  $("#right-gates").value = "H 1\nCX 1 0";
  compare();
});
compare();
