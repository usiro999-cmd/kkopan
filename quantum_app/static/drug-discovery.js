const targets = ["D2", "5-HT2A", "NMDA", "M1"];
const defaults = {
  left: [0.65, 0.75, 0.60, 0.55],
  right: [0.45, 0.60, 0.80, 0.70],
};
const $ = (selector) => document.querySelector(selector);

function createControls(side) {
  $(`#${side}-controls`).innerHTML = targets.map((target, index) => `
    <label>${target}
      <input data-side="${side}" data-target="${target}" type="range"
        min="0" max="1" step="0.05" value="${defaults[side][index]}">
      <output>${defaults[side][index].toFixed(2)}</output>
    </label>`).join("");
}

createControls("left");
createControls("right");

document.querySelectorAll("input[type=range]").forEach((input) => {
  input.addEventListener("input", () => {
    input.nextElementSibling.textContent = Number(input.value).toFixed(2);
  });
});

function requestProfile(side) {
  const desiredProfile = {};
  document.querySelectorAll(`[data-side="${side}"]`).forEach((input) => {
    desiredProfile[input.dataset.target] = Number(input.value);
  });
  return {
    desired_profile: desiredProfile,
    safety_weight: Number($(`#${side}-safety`).value),
  };
}

function renderRanking(selector, candidates) {
  $(selector).innerHTML = candidates.map((candidate) => `
    <div class="compact-rank">
      <strong><em>#${candidate.rank}</em> ${candidate.id}</strong>
      <div class="bar-track"><div class="bar" style="width:${candidate.score * 100}%"></div></div>
      <span>${(candidate.score * 100).toFixed(1)}%</span>
    </div>`).join("");
}

async function runTwinScreen() {
  $("#error").textContent = "";
  try {
    const response = await fetch("/api/drug-twin-ranking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        left: requestProfile("left"),
        right: requestProfile("right"),
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "ツイン評価に失敗しました。");
    renderRanking("#left-ranking", data.left.candidates);
    renderRanking("#right-ranking", data.right.candidates);
    $("#correlation").textContent = data.comparison.rank_correlation.toFixed(2);
    $("#same-leader").textContent = data.comparison.same_leader ? "一致" : "不一致";
    $("#rank-shifts").innerHTML = data.comparison.candidates.map((candidate) => {
      const direction = candidate.rank_delta > 0 ? "↑" : candidate.rank_delta < 0 ? "↓" : "—";
      return `<span>${candidate.id}: ${candidate.left_rank} → ${candidate.right_rank} ${direction}</span>`;
    }).join("");
  } catch (error) {
    $("#error").textContent = error.message;
  }
}

$("#screen").addEventListener("click", runTwinScreen);
runTwinScreen();
