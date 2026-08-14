"use strict";

const state = {
  trajectories: [], treatments: [], results: null, measure: "radius_um",
  animationFrame: null, animationStarted: 0, animationFrom: 0, view: "colony",
  engineered: [], longitudinal: [], chromosomes: [], resultsV1: null,
  genomeCondition: "PA", genomeDay: 200,
};
const colors = { PA1: "#55a889", PA2: "#e78769", PA3: "#e4bd59", PA4: "#7795cf", PA5: "#aa78b2" };
const profiles = {
  PA1: { seed: 1103, arms: 6, split: .20, turn: .018, jitter: .23, name: "open radial seed" },
  PA2: { seed: 2207, arms: 5, split: .31, turn: -.025, jitter: .34, name: "asymmetric branching seed" },
  PA3: { seed: 3313, arms: 8, split: .15, turn: .008, jitter: .17, name: "compact branching seed" },
  PA4: { seed: 4421, arms: 4, split: .24, turn: .055, jitter: .27, name: "curved long-arm seed" },
  PA5: { seed: 5527, arms: 7, split: .36, turn: -.045, jitter: .30, name: "dense entangling seed" },
};
const svgNS = "http://www.w3.org/2000/svg";
const topologyCache = {};

function clamp(value, low = 0, high = 1) { return Math.min(high, Math.max(low, value)); }
function svgElement(name, attrs = {}) {
  const element = document.createElementNS(svgNS, name);
  Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, String(value)));
  return element;
}
function seededRandom(seed) {
  let value = seed >>> 0;
  return () => {
    value += 0x6D2B79F5;
    let mixed = value;
    mixed = Math.imul(mixed ^ (mixed >>> 15), mixed | 1);
    mixed ^= mixed + Math.imul(mixed ^ (mixed >>> 7), mixed | 61);
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 4294967296;
  };
}

function buildTopology(population, maximum = 150) {
  const cacheKey = `${population}-${maximum}`;
  if (topologyCache[cacheKey]) return topologyCache[cacheKey];
  const profile = profiles[population];
  const random = seededRandom(profile.seed);
  const cells = [{ x: 0, y: 0, angle: -Math.PI / 2, parent: null, depth: 0, arm: null }];
  const tips = Array.from({ length: profile.arms }, () => []);
  for (let arm = 0; arm < profile.arms; arm += 1) {
    const angle = (arm / profile.arms) * Math.PI * 2 - Math.PI / 2 + (random() - .5) * .12;
    cells.push({ x: Math.cos(angle), y: Math.sin(angle), angle, parent: 0, depth: 1, arm });
    tips[arm].push(cells.length - 1);
  }
  while (cells.length < maximum) {
    const arm = (cells.length - profile.arms - 1) % profile.arms;
    const armTips = tips[arm];
    const tipPosition = Math.floor(random() * armTips.length);
    let parentIndex = armTips[tipPosition];
    const shouldSplit = random() < profile.split;
    if (shouldSplit && cells.length > profile.arms * 3) {
      const sameArm = cells
        .map((cell, index) => ({ cell, index }))
        .filter(({ cell }) => cell.arm === arm && cell.depth > 1);
      parentIndex = sameArm[Math.floor(random() * sameArm.length)].index;
    }
    const parent = cells[parentIndex];
    const direction = random() < .5 ? -1 : 1;
    let best = null;
    for (let attempt = 0; attempt < 7; attempt += 1) {
      const angle = parent.angle + profile.turn +
        (shouldSplit ? direction * (.38 + random() * .42) : 0) +
        (random() - .5) * profile.jitter;
      const step = .84 + random() * .28;
      const candidate = {
        x: parent.x + Math.cos(angle) * step,
        y: parent.y + Math.sin(angle) * step,
        angle,
      };
      const clearance = Math.min(
        ...cells.filter((_, index) => index !== parentIndex)
          .map((cell) => Math.hypot(candidate.x - cell.x, candidate.y - cell.y)),
      );
      const score = clearance + .08 * Math.hypot(candidate.x, candidate.y);
      if (!best || score > best.score) best = { ...candidate, score };
    }
    cells.push({
      x: best.x, y: best.y, angle: best.angle, parent: parentIndex,
      depth: parent.depth + 1, arm,
    });
    const nextIndex = cells.length - 1;
    if (shouldSplit) armTips.push(nextIndex); else armTips[tipPosition] = nextIndex;
    if (armTips.length > 5) armTips.splice(Math.floor(random() * armTips.length), 1);
  }
  const maxDistance = Math.max(...cells.map((cell) => Math.hypot(cell.x, cell.y)));
  cells.forEach((cell) => { cell.x /= maxDistance; cell.y /= maxDistance; });
  topologyCache[cacheKey] = cells;
  return cells;
}

function rowsFor(population) { return state.trajectories.filter((row) => row.population === population).sort((a, b) => a.day - b.day); }
function interpolateField(rows, day, field) {
  const valid = rows.filter((row) => row[field] !== null);
  const before = [...valid].reverse().find((row) => row.day <= day) || valid[0];
  const after = valid.find((row) => row.day >= day) || valid[valid.length - 1];
  if (before.day === after.day) return before[field];
  const fraction = (day - before.day) / (after.day - before.day);
  return before[field] + (after[field] - before[field]) * fraction;
}
function selectedData() {
  const population = document.querySelector("#population").value;
  const day = Number(document.querySelector("#day").value);
  const rows = rowsFor(population);
  return { population, day, exact: rows.find((row) => row.day === day) || null, aspect: interpolateField(rows, day, "aspect_ratio"), radius: interpolateField(rows, day, "radius_um") };
}
function modelMetrics(aspect, radius) {
  const packingRelief = clamp((aspect - 1.25) / (3.2 - 1.25));
  const growth = clamp(Math.log(Math.max(radius, 16.7472384) / 16.7472384) / Math.log(600 / 16.7472384));
  const entanglement = clamp((growth - .38) / .62) * (.45 + .55 * packingRelief);
  return { packingRelief, growth, entanglement };
}
function visibleCells(population, count, visualRadius) {
  return buildTopology(population).slice(0, count).map((cell) => ({ ...cell, x: 400 + cell.x * visualRadius, y: 300 + cell.y * visualRadius }));
}
function localCrowding(cells) {
  const scores = cells.map((cell, index) => cells.reduce((count, other, otherIndex) => {
    if (index === otherIndex) return count;
    const distance = Math.hypot(cell.x - other.x, cell.y - other.y);
    return count + (distance < 42 ? (42 - distance) / 42 : 0);
  }, 0));
  const maximum = Math.max(...scores, 1);
  return scores.map((score) => score / maximum);
}
function drawPackingField(group, cells, packingRelief) {
  group.replaceChildren();
  if (state.view !== "packing") return [];
  const crowding = localCrowding(cells);
  const load = crowding.map((value) => value * (1 - .65 * packingRelief));
  cells.forEach((cell, index) => {
    if (load[index] < .32 || index === 0) return;
    group.append(svgElement("circle", {
      cx: cell.x, cy: cell.y, r: 15 + load[index] * 23,
      fill: `rgba(255, 112, 84, ${.05 + load[index] * .28})`,
      stroke: `rgba(255, 171, 119, ${.15 + load[index] * .55})`,
      "stroke-width": 1.2, class: "packing-field",
    }));
  });
  return load;
}
function subtreeIndices(cells, rootIndex) {
  const result = new Set([rootIndex]);
  let changed = true;
  while (changed) {
    changed = false;
    cells.forEach((cell, index) => {
      if (!result.has(index) && result.has(cell.parent)) {
        result.add(index); changed = true;
      }
    });
  }
  return result;
}
function crossComponentContacts(cells, detached) {
  const contacts = [];
  cells.forEach((first, firstIndex) => {
    if (!detached.has(firstIndex)) return;
    cells.forEach((second, secondIndex) => {
      if (detached.has(secondIndex) || firstIndex === secondIndex) return;
      const distance = Math.hypot(first.x - second.x, first.y - second.y);
      if (distance >= 15 && distance <= 52) contacts.push([firstIndex, secondIndex, distance]);
    });
  });
  return contacts.sort((a, b) => a[2] - b[2]);
}
function fractureScenario(cells, metrics) {
  const candidates = [];
  for (let index = 1; index < cells.length; index += 1) {
    if (cells[index].depth < 3) continue;
    const detached = subtreeIndices(cells, index);
    if (detached.size < 2 || detached.size > cells.length * .42) continue;
    const contacts = crossComponentContacts(cells, detached);
    candidates.push({ index, detached, contacts });
  }
  const eligible = metrics.entanglement >= .24 && cells.length >= 42;
  candidates.sort((a, b) => eligible
    ? b.contacts.length - a.contacts.length || b.detached.size - a.detached.size
    : a.contacts.length - b.contacts.length || a.detached.size - b.detached.size);
  const fallbackIndex = Math.max(1, cells.length - 1);
  const selected = candidates[0] || {
    index: fallbackIndex,
    detached: subtreeIndices(cells, fallbackIndex),
    contacts: [],
  };
  const retained = eligible && selected.contacts.length > 0;
  return { ...selected, retained, contacts: retained ? selected.contacts.slice(0, 5) : [] };
}
function drawEntanglements(group, cells, scenario) {
  group.replaceChildren();
  if (state.view !== "fracture" || !scenario.retained) return;
  scenario.contacts.forEach(([a, b], index) => {
    const first = cells[a]; const second = cells[b];
    const middleX = (first.x + second.x) / 2 + (index % 2 ? 8 : -8);
    const middleY = (first.y + second.y) / 2 + (index % 2 ? -7 : 7);
    const path = svgElement("path", {
      d: `M${first.x},${first.y} Q${middleX},${middleY} ${second.x},${second.y}`,
      fill: "none", stroke: "#ffd166", "stroke-width": 5, opacity: .96,
      class: "entanglement retained-contact",
    });
    const title = svgElement("title");
    title.textContent = "Modelled steric contact between disconnected branches—not a bond";
    path.append(title); group.append(path);
  });
}

function appendJunction(group, parent, cell, status = "intact") {
  const x = (parent.x + cell.x) / 2;
  const y = (parent.y + cell.y) / 2;
  const marker = svgElement("circle", {
    cx: x, cy: y, r: status === "cut" ? 5.5 : 2.8,
    fill: status === "cut" ? "#10231f" : "#d8fff0",
    stroke: status === "cut" ? "#ff6b5e" : "#2f7461",
    "stroke-width": status === "cut" ? 3 : 1.4,
    class: status === "cut" ? "cut-junction" : "tree-junction",
  });
  const title = svgElement("title");
  title.textContent = status === "cut"
    ? "Illustrative severed chitinous parent–daughter junction"
    : "Modelled permanent chitinous parent–daughter junction";
  marker.append(title); group.append(marker);
}

function syncMechanismLegend(scenario) {
  document.querySelectorAll(".chamber-key [data-key]").forEach((item) => {
    const key = item.dataset.key;
    const active = key === "cells" || key === "bonds" ||
      (state.view === "fracture" && key === "fracture") ||
      (state.view === "fracture" && key === "contact" && scenario.retained);
    item.classList.toggle("inactive", !active);
  });
}

function drawCluster(data) {
  const branchGroup = document.querySelector("#model-branches");
  const breakGroup = document.querySelector("#model-breaks");
  const entangleGroup = document.querySelector("#model-entanglements");
  const cellGroup = document.querySelector("#model-cells");
  const junctionGroup = document.querySelector("#model-junctions");
  branchGroup.replaceChildren(); breakGroup.replaceChildren(); cellGroup.replaceChildren();
  junctionGroup.replaceChildren(); entangleGroup.replaceChildren();
  const metrics = modelMetrics(data.aspect, data.radius);
  const cells = visibleCells(data.population, Math.round(18 + metrics.growth * 125), 72 + metrics.growth * 190);
  const scenario = fractureScenario(cells, metrics);
  cells.forEach((cell, index) => {
    if (cell.parent === null) return;
    const parent = cells[cell.parent];
    if (!parent) return;
    const cut = state.view === "fracture" && index === scenario.index;
    if (cut) return;
    branchGroup.append(svgElement("line", {
      x1: parent.x, y1: parent.y, x2: cell.x, y2: cell.y,
      stroke: "#b8e0d0", "stroke-width": state.view === "fracture" ? 2.2 : 3.2,
      opacity: state.view === "packing" ? .38 : .78, class: "tree-bond",
    }));
  });
  const packingLoad = drawPackingField(
    document.querySelector("#model-field"), cells, metrics.packingRelief,
  );
  const rx = clamp(8.4 / Math.sqrt(data.aspect), 4.2, 7.5);
  const ry = clamp(8.4 * Math.sqrt(data.aspect), 9, 16);
  cells.forEach((cell, index) => {
    const detached = state.view === "fracture" && scenario.detached.has(index);
    const loaded = state.view === "packing" && packingLoad[index] > .58;
    const fill = index === 0 ? "#ffe59a" : detached ? "#e78769" : loaded ? "#f2b36d" : colors[data.population];
    cellGroup.append(svgElement("ellipse", {
      cx: cell.x, cy: cell.y, rx, ry, fill, stroke: "#f4efe3", "stroke-width": 1,
      opacity: state.view === "fracture" && !detached ? .74 : .97,
      transform: `rotate(${(cell.angle * 180) / Math.PI + 90} ${cell.x} ${cell.y})`,
      class: `model-cell${detached ? " detached-component" : ""}`,
      style: `--cell-index:${index}`,
    }));
  });
  cells.forEach((cell, index) => {
    if (cell.parent === null || (state.view === "fracture" && index === scenario.index)) return;
    const parent = cells[cell.parent];
    if (parent) appendJunction(junctionGroup, parent, cell);
  });
  if (state.view === "fracture") {
    const cell = cells[scenario.index]; const parent = cells[cell.parent];
    if (parent) {
      const midpointX = (parent.x + cell.x) / 2;
      const midpointY = (parent.y + cell.y) / 2;
      [[parent.x, parent.y, midpointX - (cell.x - parent.x) * .12, midpointY - (cell.y - parent.y) * .12],
        [midpointX + (cell.x - parent.x) * .12, midpointY + (cell.y - parent.y) * .12, cell.x, cell.y]]
        .forEach((line) => breakGroup.append(svgElement("line", {
          x1: line[0], y1: line[1], x2: line[2], y2: line[3],
          stroke: "#ff6b5e", "stroke-width": 5, opacity: 1, class: "broken-bond",
        })));
      appendJunction(breakGroup, parent, cell, "cut");
    }
  }
  drawEntanglements(entangleGroup, cells, scenario);
  syncMechanismLegend(scenario);
  return { metrics, scenario, cellCount: cells.length, packingLoad };
}

function drawHero() {
  const group = document.querySelector("#hero-cells"); group.replaceChildren();
  visibleCells("PA5", 118, 235).forEach((cell, index) => group.append(svgElement("ellipse", { cx: cell.x - 40, cy: cell.y + 60, rx: 5.5, ry: 15.5, fill: index % 7 === 0 ? "#f3de93" : "url(#cell-fill)", stroke: "#8b6721", "stroke-width": 1, transform: `rotate(${(cell.angle * 180) / Math.PI + 90} ${cell.x - 40} ${cell.y + 60})` })));
}
function syncPopulationControls(population) {
  document.querySelectorAll("[data-population]").forEach((button) => { const active = button.dataset.population === population; button.classList.toggle("active", active); button.setAttribute("aria-pressed", String(active)); });
}
function updateMechanismStatus(data, render) {
  const title = document.querySelector("#mechanism-status-title");
  const copy = document.querySelector("#mechanism-status-copy");
  const outcome = document.querySelector("#fracture-outcome");
  if (state.view === "colony") {
    title.textContent = "Connected clonal tree";
    copy.textContent = "Pale collars mark permanent chitinous parent–daughter junctions. The founder is gold.";
    outcome.hidden = true;
    document.querySelector("#mechanism-value").textContent = "Connected tree";
  } else if (state.view === "packing") {
    title.textContent = "Illustrative packing load";
    copy.textContent = "Warm halos mark locally crowded model regions; cell elongation reduces the normalized load cue.";
    outcome.hidden = true;
    document.querySelector("#mechanism-value").textContent = "Packing stress test";
  } else {
    title.textContent = "One-junction fracture stress test";
    copy.textContent = "Coral cells form the disconnected tree component after the red chitinous junction is cut.";
    outcome.hidden = false;
    outcome.classList.toggle("retained", render.scenario.retained);
    outcome.classList.toggle("detached", !render.scenario.retained);
    outcome.textContent = render.scenario.retained
      ? `${render.scenario.contacts.length} steric contact${render.scenario.contacts.length === 1 ? "" : "s"} retain the component · no adhesion`
      : "No cross-component steric retention in this illustrative geometry · component detaches";
    document.querySelector("#mechanism-value").textContent = render.scenario.retained
      ? "Sterically retained" : "Component detaches";
  }
  window.__snowflakeModelSnapshot = {
    population: data.population,
    day: data.day,
    view: state.view,
    cells: render.cellCount,
    intactJunctions: document.querySelectorAll(".tree-junction").length,
    severedJunctions: document.querySelectorAll(".cut-junction").length,
    retainedContacts: document.querySelectorAll(".retained-contact").length,
    retained: render.scenario.retained,
  };
}
function updateChamber() {
  const data = selectedData(); const isPublishedPoint = data.day % 50 === 0; const sourceMissing = data.exact && data.exact.radius_um === null;
  const render = drawCluster(data); const metrics = render.metrics;
  document.querySelector("#day-output").value = String(data.day);
  document.querySelector("#aspect-value").textContent = `${isPublishedPoint ? "" : "≈ "}${data.aspect.toFixed(2)}`;
  document.querySelector("#radius-value").textContent = sourceMissing ? "Not reported" : `${isPublishedPoint ? "" : "≈ "}${data.radius.toFixed(2)} µm`;
  document.querySelector("#relative-value").textContent = sourceMissing ? "—" : `${(data.radius / 16.7472384).toFixed(1)}×`;
  document.querySelector("#packing-value").textContent = `${Math.round(metrics.packingRelief * 100)}%`;
  const status = document.querySelector("#measurement-status");
  status.textContent = sourceMissing ? "Source value missing · animation bridges neighbouring measurements" : isPublishedPoint ? "Published measurement" : "Visual interpolation between published measurements";
  status.classList.toggle("warning", Boolean(sourceMissing));
  const viewExplanation = state.view === "colony"
    ? "The connected tree exposes chitinous parent–daughter junctions without implying measured lineage topology."
    : state.view === "packing"
      ? `The normalized packing-relief cue is ${Math.round(metrics.packingRelief * 100)}%; warm halos show model crowding, not measured cellular stress.`
      : render.scenario.retained
        ? "After one model junction is severed, dashed gold paths mark steric cross-component contacts that retain the coral branch without adhesion or bond repair."
        : "After one model junction is severed, the coral component has no qualifying cross-component contact and would detach.";
  document.querySelector("#model-explanation").textContent = `A fixed ${data.population} ${profiles[data.population].name} supplies a repeatable recognition seed only. Published means determine display scale and cell elongation. ${viewExplanation}`;
  document.querySelector("#cluster-desc").textContent = `${data.population} at transfer ${data.day}: an explanatory branching model driven by published mean aspect ratio and radius.`;
  updateMechanismStatus(data, render);
  syncPopulationControls(data.population);
}
function stopPlayback() {
  if (state.animationFrame) cancelAnimationFrame(state.animationFrame);
  state.animationFrame = null;
  const button = document.querySelector("#play"); button.textContent = "Play evolution"; button.setAttribute("aria-pressed", "false");
}
function animationTick(now) {
  const slider = document.querySelector("#day"); const elapsed = now - state.animationStarted; const remaining = 600 - state.animationFrom;
  const day = Math.min(600, state.animationFrom + (elapsed / 12000) * Math.max(remaining, 1));
  slider.value = String(Math.round(day)); updateChamber();
  if (day >= 600) { stopPlayback(); return; }
  state.animationFrame = requestAnimationFrame(animationTick);
}
function togglePlay() {
  if (state.animationFrame) { stopPlayback(); return; }
  const slider = document.querySelector("#day"); if (Number(slider.value) >= 600) slider.value = "0";
  state.animationFrom = Number(slider.value); state.animationStarted = performance.now();
  const button = document.querySelector("#play"); button.textContent = "Pause evolution"; button.setAttribute("aria-pressed", "true");
  state.animationFrame = requestAnimationFrame(animationTick);
}

function drawChart() {
  const svg = document.querySelector("#trajectory-chart"); svg.replaceChildren();
  const margin = { left: 82, right: 36, top: 38, bottom: 72 }; const width = 1000 - margin.left - margin.right; const height = 520 - margin.top - margin.bottom;
  const values = state.trajectories.map((row) => row[state.measure]).filter((value) => value !== null); const min = state.measure === "radius_um" ? 0 : 1; const max = state.measure === "radius_um" ? 620 : Math.max(...values) * 1.08;
  const x = (day) => margin.left + (day / 600) * width; const y = (value) => margin.top + height - ((value - min) / (max - min)) * height;
  const yTicks = state.measure === "radius_um" ? [0, 100, 200, 300, 400, 500, 600] : [1, 1.5, 2, 2.5, 3, 3.5];
  yTicks.forEach((tick) => { svg.append(svgElement("line", { x1: margin.left, x2: 1000 - margin.right, y1: y(tick), y2: y(tick), stroke: "#10231f", opacity: .13 })); const label = svgElement("text", { x: margin.left - 15, y: y(tick) + 5, "text-anchor": "end", fill: "#53645e", "font-size": 14 }); label.textContent = String(tick); svg.append(label); });
  for (let day = 0; day <= 600; day += 100) { const label = svgElement("text", { x: x(day), y: 485, "text-anchor": "middle", fill: "#53645e", "font-size": 14 }); label.textContent = String(day); svg.append(label); }
  Object.keys(colors).forEach((population, legendIndex) => {
    const rows = state.trajectories.filter((row) => row.population === population && row[state.measure] !== null); let path = "";
    rows.forEach((row, index) => { path += `${index === 0 ? "M" : "L"}${x(row.day)},${y(row[state.measure])} `; });
    svg.append(svgElement("path", { d: path, fill: "none", stroke: colors[population], "stroke-width": 4 }));
    rows.forEach((row) => svg.append(svgElement("circle", { cx: x(row.day), cy: y(row[state.measure]), r: 5, fill: colors[population], stroke: "#f4efe3", "stroke-width": 2 })));
    const legend = svgElement("text", { x: margin.left + legendIndex * 88, y: 24, fill: colors[population], "font-size": 15, "font-weight": 700 }); legend.textContent = population; svg.append(legend);
  });
  const axis = svgElement("text", { x: 500, y: 510, "text-anchor": "middle", fill: "#53645e", "font-size": 14 }); axis.textContent = "Daily transfers"; svg.append(axis);
  document.querySelector("#chart-summary").textContent = state.measure === "radius_um" ? "Cluster radius increased across all five lines, from 16.75 micrometres at day zero to 288.73–579.76 micrometres at day 600." : "Mean cellular aspect ratio increased from 1.25 to 2.54–3.16 across all five lines.";
}
function drawTreatments() {
  const labels = { ancestor: "Ancestor", obligately_aerobic: "Obligately aerobic", mixotrophic: "Mixotrophic", anaerobic: "Anaerobic" }; const plot = document.querySelector("#treatment-plot"); plot.replaceChildren();
  Object.keys(labels).forEach((treatment) => {
    const values = state.treatments.filter((row) => row.treatment === treatment).map((row) => row.radius_um); const row = document.createElement("div"); row.className = "treatment-row"; row.dataset.treatment = treatment;
    const label = document.createElement("span"); label.textContent = labels[treatment]; const track = document.createElement("div"); track.className = "treatment-track";
    values.forEach((value) => { const dot = document.createElement("i"); dot.className = "treatment-dot"; dot.style.left = `${Math.min(100, (value / 620) * 100)}%`; dot.title = `${value.toFixed(2)} µm`; track.append(dot); });
    const summary = document.createElement("strong"); summary.textContent = `${(values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)} µm`; row.append(label, track, summary); plot.append(row);
  });
}

function comparison(condition, outcome) {
  return state.resultsV1.engineered_intervention.comparisons.find(
    (row) => row.condition === condition && row.outcome === outcome,
  );
}

function drawIntervention() {
  const condition = state.genomeCondition;
  const outcomes = [
    ["weighted_mean_radius_um_24h", "#effect-radius", "#effect-radius-detail", "µm"],
    ["mean_cell_volume_um3", "#effect-volume", "#effect-volume-detail", "µm³"],
    ["mean_aspect_ratio", "#effect-aspect", "#effect-aspect-detail", ""],
  ];
  document.querySelector("#intervention-title").textContent = `${condition}: immediate 2N → 4N effect`;
  outcomes.forEach(([outcome, valueSelector, detailSelector, unit]) => {
    const result = comparison(condition, outcome);
    const digits = outcome === "mean_aspect_ratio" ? 3 : 1;
    document.querySelector(valueSelector).textContent = `+${result.difference_4n_minus_2n.toFixed(digits)} ${unit}`.trim();
    document.querySelector(detailSelector).textContent = `${result.mean_2n.toFixed(digits)} → ${result.mean_4n.toFixed(digits)} ${unit}`.trim();
  });
  const primary = comparison(condition, "weighted_mean_radius_um_24h");
  document.querySelector("#intervention-inference").textContent =
    `Exact one-sided permutation p = ${primary.exact_one_sided_permutation_probability.toFixed(4)}; ` +
    `Holm-adjusted p = ${primary.holm_adjusted_probability.toFixed(4)}. Biological inference unit: replicate strain (n = 4 per group).`;
}

function copyColor(copy) {
  if (copy === 4) return "#f3de93";
  if (copy < 4) return "#7eb3c4";
  return "#e78769";
}

function drawGenome() {
  const line = document.querySelector("#genome-line").value;
  const condition = state.genomeCondition;
  const day = state.genomeDay;
  const observation = state.longitudinal.find(
    (row) => row.condition === condition && row.line === line && row.day === day,
  );
  const copies = state.chromosomes.filter(
    (row) => row.condition === condition && row.line === line && row.day === day,
  );
  const burden = state.resultsV1.aneuploidy_burdens.find(
    (row) => row.condition === condition && row.line === line && row.day === day,
  );
  document.querySelector("#genome-title").textContent = `${condition}${line} · transfer ${day.toLocaleString()}`;
  document.querySelector("#genome-ploidy").textContent = `${observation.g1_peak_n.toFixed(3)}N`;
  document.querySelector("#genome-radius").textContent = `${observation.weighted_mean_radius_um.toFixed(1)} µm`;
  document.querySelector("#genome-aspect").textContent = observation.mean_aspect_ratio.toFixed(3);
  document.querySelector("#genome-burden").textContent = `${burden.aneuploidy_burden} copy-step${burden.aneuploidy_burden === 1 ? "" : "s"}`;
  const grid = document.querySelector("#chromosome-grid");
  grid.replaceChildren();
  copies.forEach((row) => {
    const item = document.createElement("div");
    item.className = "chromosome";
    const bar = document.createElement("div");
    bar.className = "chromosome-bar";
    bar.dataset.copy = row.copy_number;
    bar.style.height = `${Math.max(12, row.copy_number * 28)}px`;
    bar.style.setProperty("--copy-color", copyColor(row.copy_number));
    bar.title = `Chromosome ${row.chromosome}: ${row.copy_number} copies`;
    const label = document.createElement("span");
    label.className = "chromosome-label";
    label.textContent = row.chromosome;
    item.append(bar, label);
    grid.append(item);
  });
  grid.setAttribute(
    "aria-label",
    `${condition}${line} at transfer ${day}: ${copies.map((row) => `${row.chromosome} ${row.copy_number}`).join(", ")}`,
  );
  drawIntervention();
}

function drawSufficiency() {
  const summaries = state.resultsV1.longitudinal_sufficiency.treatment_summaries;
  const timeline = document.querySelector("#sufficiency-timeline");
  timeline.replaceChildren();
  const key = document.createElement("div");
  key.className = "timeline-key";
  key.innerHTML = "<span><i></i>PA mean</span><span><i class=\"pm\"></i>PM mean</span>";
  timeline.append(key);
  [600, 1000].forEach((day) => {
    const summary = summaries[String(day)];
    const row = document.createElement("div");
    row.className = "timeline-row";
    const label = document.createElement("span"); label.textContent = `t${day}`;
    const track = document.createElement("div"); track.className = "timeline-track";
    const pa = document.createElement("i"); pa.className = "timeline-bar"; pa.style.width = `${(summary.mean_pa_radius_um / 450) * 100}%`;
    const pm = document.createElement("i"); pm.className = "timeline-bar pm"; pm.style.width = `${(summary.mean_pm_radius_um / 450) * 100}%`;
    track.append(pa, pm);
    const ratio = document.createElement("strong"); ratio.textContent = `${summary.pa_over_pm_ratio.toFixed(2)}×`;
    row.append(label, track, ratio); timeline.append(row);
  });
}

async function init() {
  drawHero();
  try {
    const [trajectories, treatments, results, engineered, longitudinal, chromosomes, resultsV1] = await Promise.all([
      fetch("data/trajectories-v0.1.json").then((response) => response.json()),
      fetch("data/treatments-v0.1.json").then((response) => response.json()),
      fetch("data/results-v0.1.json").then((response) => response.json()),
      fetch("data/engineered-v1.0.json").then((response) => response.json()),
      fetch("data/longitudinal-v1.0.json").then((response) => response.json()),
      fetch("data/chromosome-copy-v1.0.json").then((response) => response.json()),
      fetch("data/results-v1.0.json").then((response) => response.json()),
    ]);
    state.trajectories = trajectories; state.treatments = treatments; state.results = results;
    state.engineered = engineered; state.longitudinal = longitudinal; state.chromosomes = chromosomes; state.resultsV1 = resultsV1;
    document.querySelector('[data-result="median"]').textContent = results.confirmatory.median_spearman_rho.toFixed(3); updateChamber(); drawChart(); drawTreatments(); drawGenome(); drawSufficiency();
  } catch (error) { document.querySelector("#experiment").insertAdjacentHTML("afterbegin", '<p role="alert">Interactive data could not be loaded. The source links and research report remain available.</p>'); }
}

document.querySelector("#population").addEventListener("change", updateChamber);
document.querySelectorAll("[data-population]").forEach((button) => button.addEventListener("click", () => { document.querySelector("#population").value = button.dataset.population; updateChamber(); }));
document.querySelector("#day").addEventListener("input", () => { stopPlayback(); updateChamber(); });
document.querySelector("#play").addEventListener("click", togglePlay);
document.querySelectorAll(".view-choice").forEach((button) => button.addEventListener("click", () => { state.view = button.dataset.view; document.querySelectorAll(".view-choice").forEach((item) => { const active = item === button; item.classList.toggle("active", active); item.setAttribute("aria-pressed", String(active)); }); updateChamber(); }));
document.querySelectorAll(".chart-choice").forEach((button) => button.addEventListener("click", () => { state.measure = button.dataset.measure; document.querySelectorAll(".chart-choice").forEach((item) => item.classList.toggle("active", item === button)); drawChart(); }));
document.querySelectorAll("[data-genome-condition]").forEach((button) => button.addEventListener("click", () => {
  state.genomeCondition = button.dataset.genomeCondition;
  document.querySelectorAll("[data-genome-condition]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
  drawGenome();
}));
document.querySelectorAll("[data-genome-day]").forEach((button) => button.addEventListener("click", () => {
  state.genomeDay = Number(button.dataset.genomeDay);
  document.querySelectorAll("[data-genome-day]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
  drawGenome();
}));
document.querySelector("#genome-line").addEventListener("change", drawGenome);
init();
