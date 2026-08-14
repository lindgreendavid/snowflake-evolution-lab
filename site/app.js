"use strict";

const state = { trajectories: [], treatments: [], results: null, measure: "radius_um", timer: null };
const colors = { PA1: "#234f42", PA2: "#c56b4f", PA3: "#98732b", PA4: "#586f9d", PA5: "#76577d" };
const svgNS = "http://www.w3.org/2000/svg";

function svgElement(name, attrs = {}) {
  const element = document.createElementNS(svgNS, name);
  Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, String(value)));
  return element;
}

function deterministicCells(count, aspect, cx, cy, radius) {
  const cells = [];
  const branches = Math.min(9, Math.max(5, Math.round(count / 8)));
  for (let i = 0; i < count; i += 1) {
    const arm = i % branches;
    const layer = Math.floor(i / branches) + 1;
    const twist = layer * 0.18 * (arm % 2 ? 1 : -1);
    const angle = (arm / branches) * Math.PI * 2 + twist;
    const distance = Math.min(radius, layer * (radius / Math.max(3, Math.ceil(count / branches))));
    cells.push({ x: cx + Math.cos(angle) * distance, y: cy + Math.sin(angle) * distance, angle, aspect, parent: i >= branches ? i - branches : null });
  }
  return cells;
}

function drawCluster(groupCells, groupBranches, count, aspect, size = 1) {
  groupCells.replaceChildren();
  if (groupBranches) groupBranches.replaceChildren();
  const cells = deterministicCells(count, aspect, 400, 310, 220 * size);
  if (groupBranches) {
    cells.forEach((cell) => {
      if (cell.parent === null) return;
      const parent = cells[cell.parent];
      groupBranches.append(svgElement("line", { x1: parent.x, y1: parent.y, x2: cell.x, y2: cell.y, stroke: "#9bc0ae", "stroke-width": 3, opacity: .7 }));
    });
  }
  cells.forEach((cell, index) => {
    const ellipse = svgElement("ellipse", {
      cx: cell.x, cy: cell.y,
      rx: 8 + Math.min(5, cell.aspect), ry: (8 + Math.min(5, cell.aspect)) * cell.aspect,
      fill: index % 5 === 0 ? "#edc767" : "#f3de93", stroke: "#80611f", "stroke-width": 1,
      transform: `rotate(${(cell.angle * 180) / Math.PI + 90} ${cell.x} ${cell.y})`,
    });
    groupCells.append(ellipse);
  });
}

function drawHero() {
  const group = document.querySelector("#hero-cells");
  group.replaceChildren();
  deterministicCells(82, 2.7, 360, 360, 235).forEach((cell, index) => {
    group.append(svgElement("ellipse", {
      cx: cell.x, cy: cell.y, rx: 7, ry: 18,
      fill: index % 6 === 0 ? "#f3de93" : "url(#cell-fill)", stroke: "#8b6721", "stroke-width": 1,
      transform: `rotate(${(cell.angle * 180) / Math.PI + 90} ${cell.x} ${cell.y})`,
    }));
  });
}

function selectedRow() {
  const population = document.querySelector("#population").value;
  const day = Number(document.querySelector("#day").value);
  return state.trajectories.find((row) => row.population === population && row.day === day);
}

function updateChamber() {
  const row = selectedRow();
  if (!row) return;
  const radius = row.radius_um;
  document.querySelector("#day-output").value = row.day;
  document.querySelector("#aspect-value").textContent = row.aspect_ratio.toFixed(2);
  document.querySelector("#radius-value").textContent = radius === null ? "Not reported" : `${radius.toFixed(2)} µm`;
  document.querySelector("#relative-value").textContent = radius === null ? "—" : `${(radius / 16.7472384).toFixed(1)}×`;
  const count = Math.round(28 + row.day / 12);
  const scale = .72 + Math.min(.28, Math.log10(Math.max(radius || 16.75, 16.75) / 16.75 + 1) * .18);
  drawCluster(document.querySelector("#model-cells"), document.querySelector("#model-branches"), count, row.aspect_ratio, scale);
}

function togglePlay() {
  const button = document.querySelector("#play");
  if (state.timer) {
    clearInterval(state.timer); state.timer = null;
    button.textContent = "Play evolution"; button.setAttribute("aria-pressed", "false");
    return;
  }
  button.textContent = "Pause evolution"; button.setAttribute("aria-pressed", "true");
  state.timer = window.setInterval(() => {
    const slider = document.querySelector("#day");
    slider.value = Number(slider.value) >= 600 ? 0 : Number(slider.value) + 50;
    updateChamber();
  }, 700);
}

function drawChart() {
  const svg = document.querySelector("#trajectory-chart");
  svg.replaceChildren();
  const margin = { left: 82, right: 36, top: 38, bottom: 72 };
  const width = 1000 - margin.left - margin.right;
  const height = 520 - margin.top - margin.bottom;
  const values = state.trajectories.map((row) => row[state.measure]).filter((value) => value !== null);
  const min = state.measure === "radius_um" ? 0 : 1;
  const max = state.measure === "radius_um" ? 620 : Math.max(...values) * 1.08;
  const x = (day) => margin.left + (day / 600) * width;
  const y = (value) => margin.top + height - ((value - min) / (max - min)) * height;
  const yTicks = state.measure === "radius_um" ? [0, 100, 200, 300, 400, 500, 600] : [1, 1.5, 2, 2.5, 3, 3.5];
  yTicks.forEach((tick) => {
    svg.append(svgElement("line", { x1: margin.left, x2: 1000 - margin.right, y1: y(tick), y2: y(tick), stroke: "#10231f", opacity: .13 }));
    const label = svgElement("text", { x: margin.left - 15, y: y(tick) + 5, "text-anchor": "end", fill: "#53645e", "font-size": 14 });
    label.textContent = String(tick); svg.append(label);
  });
  for (let day = 0; day <= 600; day += 100) {
    const label = svgElement("text", { x: x(day), y: 485, "text-anchor": "middle", fill: "#53645e", "font-size": 14 });
    label.textContent = String(day); svg.append(label);
  }
  Object.keys(colors).forEach((population, legendIndex) => {
    const rows = state.trajectories.filter((row) => row.population === population && row[state.measure] !== null);
    let path = "";
    rows.forEach((row, index) => { path += `${index === 0 ? "M" : "L"}${x(row.day)},${y(row[state.measure])} `; });
    svg.append(svgElement("path", { d: path, fill: "none", stroke: colors[population], "stroke-width": 4 }));
    rows.forEach((row) => svg.append(svgElement("circle", { cx: x(row.day), cy: y(row[state.measure]), r: 5, fill: colors[population], stroke: "#f4efe3", "stroke-width": 2 })));
    const legend = svgElement("text", { x: margin.left + legendIndex * 88, y: 24, fill: colors[population], "font-size": 15, "font-weight": 700 });
    legend.textContent = population; svg.append(legend);
  });
  const axis = svgElement("text", { x: 500, y: 510, "text-anchor": "middle", fill: "#53645e", "font-size": 14 });
  axis.textContent = "Daily transfers"; svg.append(axis);
  document.querySelector("#chart-summary").textContent = state.measure === "radius_um" ? "Cluster radius increased across all five lines, from 16.75 micrometres at day zero to 288.73–579.76 micrometres at day 600." : "Mean cellular aspect ratio increased from 1.25 to 2.54–3.16 across all five lines.";
}

function drawTreatments() {
  const labels = { ancestor: "Ancestor", obligately_aerobic: "Obligately aerobic", mixotrophic: "Mixotrophic", anaerobic: "Anaerobic" };
  const plot = document.querySelector("#treatment-plot");
  plot.replaceChildren();
  Object.keys(labels).forEach((treatment) => {
    const values = state.treatments.filter((row) => row.treatment === treatment).map((row) => row.radius_um);
    const row = document.createElement("div"); row.className = "treatment-row"; row.dataset.treatment = treatment;
    const label = document.createElement("span"); label.textContent = labels[treatment];
    const track = document.createElement("div"); track.className = "treatment-track";
    values.forEach((value) => { const dot = document.createElement("i"); dot.className = "treatment-dot"; dot.style.left = `${Math.min(100, (value / 620) * 100)}%`; dot.title = `${value.toFixed(2)} µm`; track.append(dot); });
    const summary = document.createElement("strong"); summary.textContent = `${(values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)} µm`;
    row.append(label, track, summary); plot.append(row);
  });
}

async function init() {
  drawHero();
  try {
    const [trajectories, treatments, results] = await Promise.all([
      fetch("data/trajectories-v0.1.json").then((response) => response.json()),
      fetch("data/treatments-v0.1.json").then((response) => response.json()),
      fetch("data/results-v0.1.json").then((response) => response.json()),
    ]);
    state.trajectories = trajectories; state.treatments = treatments; state.results = results;
    document.querySelector('[data-result="median"]').textContent = results.confirmatory.median_spearman_rho.toFixed(3);
    updateChamber(); drawChart(); drawTreatments();
  } catch (error) {
    document.querySelector("#experiment").insertAdjacentHTML("afterbegin", '<p role="alert">Interactive data could not be loaded. The source links and research report remain available.</p>');
  }
}

document.querySelector("#population").addEventListener("change", updateChamber);
document.querySelector("#day").addEventListener("input", updateChamber);
document.querySelector("#play").addEventListener("click", togglePlay);
document.querySelectorAll(".chart-choice").forEach((button) => button.addEventListener("click", () => {
  state.measure = button.dataset.measure;
  document.querySelectorAll(".chart-choice").forEach((item) => item.classList.toggle("active", item === button));
  drawChart();
}));
init();
