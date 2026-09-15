"use strict";
const $ = (id) => document.getElementById(id);
const history = [];
let sortKey = "time",
  sortDirection = -1;
const colors = ["#ed896b", "#eabb69", "#8d9fd5", "#bcc7d2"];
const categories = ["Phishing", "Scams", "Marketing", "Other"];
const svg = (content) =>
  `<svg viewBox="0 0 500 170" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">${content}</svg>`;
$("today").textContent = new Date().toLocaleDateString(undefined, {
  month: "short",
  day: "numeric",
  year: "numeric",
});
function countChars() {
  $("charCount").textContent =
    `${$("messageInput").value.length.toLocaleString()} / 10,000`;
}
$("messageInput").addEventListener("input", countChars);
countChars();
$("sampleButton").addEventListener("click", () => {
  $("messageInput").value =
    "Hi, are we still meeting for lunch at noon? I will see you at the cafe.";
  countChars();
  $("messageInput").focus();
});
function renderHistory() {
  const rows = history
    .filter(
      (row) =>
        $("statusFilter").value === "all" ||
        row.result === $("statusFilter").value,
    )
    .sort(
      (a, b) =>
        (typeof a[sortKey] === "string"
          ? a[sortKey].localeCompare(b[sortKey])
          : a[sortKey] - b[sortKey]) * sortDirection,
    );
  $("activityRows").replaceChildren();
  for (const row of rows) {
    const tr = document.createElement("tr");
    const message = document.createElement("td");
    message.textContent = row.message;
    message.title = row.message;
    const status = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = `badge ${row.result === "SPAM" ? "spam" : ""}`;
    badge.textContent = row.result === "SPAM" ? "Spam" : "Clean";
    status.append(badge);
    const confidence = document.createElement("td");
    confidence.textContent = `${row.confidence}%`;
    const time = document.createElement("td");
    time.textContent = new Date(row.time).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
    tr.append(message, status, confidence, time);
    $("activityRows").append(tr);
  }
  if (!rows.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 4;
    td.className = "empty";
    td.textContent = history.length
      ? "No messages match this filter."
      : "A clean slate. Analyze your first message to get started.";
    tr.append(td);
    $("activityRows").append(tr);
  }
  $("activityCount").textContent =
    `${rows.length} of ${history.length} messages`;
}
$("statusFilter").addEventListener("change", renderHistory);
document.querySelectorAll("[data-sort]").forEach((button) =>
  button.addEventListener("click", () => {
    sortDirection = sortKey === button.dataset.sort ? -sortDirection : 1;
    sortKey = button.dataset.sort;
    document
      .querySelectorAll("th")
      .forEach((th) => th.removeAttribute("aria-sort"));
    button
      .closest("th")
      .setAttribute(
        "aria-sort",
        sortDirection === 1 ? "ascending" : "descending",
      );
    renderHistory();
  }),
);
function renderDashboard() {
  const spam = history.filter((row) => row.result === "SPAM");
  $("totalScanned").textContent = history.length.toLocaleString();
  $("spamBlocked").textContent = spam.length.toLocaleString();
  const dates = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - 6 + i);
    return date;
  });
  const values = (result) =>
    dates.map(
      (date) =>
        history.filter(
          (row) =>
            new Date(row.time).toDateString() === date.toDateString() &&
            row.result === result,
        ).length,
    );
  const cleanValues = values("NOT SPAM"),
    spamValues = values("SPAM");
  const max = Math.max(1, ...cleanValues, ...spamValues);
  const grid = [0, 0.5, 1]
    .map(
      (n) =>
        `<line x1="28" y1="${145 - n * 130}" x2="490" y2="${145 - n * 130}" stroke="#edf0f4"/><text x="0" y="${149 - n * 130}" fill="#94a0ad" font-size="10">${+(n * max).toFixed(1)}</text>`,
    )
    .join("");
  const line = (data, color) =>
    `<polyline points="${data.map((n, i) => `${28 + i * 77},${145 - (n / max) * 130}`).join(" ")}" fill="none" stroke="${color}" stroke-width="2.5"/>` +
    data
      .map(
        (n, i) =>
          `<circle cx="${28 + i * 77}" cy="${145 - (n / max) * 130}" r="3" fill="${color}"/>`,
      )
      .join("");
  $("trendChart").innerHTML = svg(
    grid + line(cleanValues, "#17a995") + line(spamValues, "#ed896b"),
  );
  $("trendChart").setAttribute(
    "aria-label",
    `Last seven days: ${cleanValues.join(", ")} clean; ${spamValues.join(", ")} spam.`,
  );
  $("trendDays").replaceChildren(
    ...dates.map((date) => {
      const span = document.createElement("span");
      span.textContent = date.toLocaleDateString(undefined, {
        weekday: "short",
      });
      return span;
    }),
  );
  $("categoryTotal").textContent = spam.length;
  let angle = 0;
  const segments = [];
  $("categoryLegend").replaceChildren();
  categories.forEach((category, i) => {
    const count = spam.filter((row) => row.category === category).length;
    const next = angle + (spam.length ? (count / spam.length) * 360 : 0);
    segments.push(`${colors[i]} ${angle}deg ${next}deg`);
    angle = next;
    const li = document.createElement("li");
    const dot = document.createElement("i");
    dot.className = "dot";
    dot.style.background = colors[i];
    const number = document.createElement("b");
    number.textContent = count;
    li.append(dot, document.createTextNode(category), number);
    $("categoryLegend").append(li);
  });
  $("donut").style.background = spam.length
    ? `conic-gradient(${segments.join(",")})`
    : "#edf1f5";
  renderHistory();
}
$("testForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = $("messageInput").value.trim();
  $("error").hidden = true;
  if (!message) {
    $("error").textContent = "Please enter a message.";
    $("error").hidden = false;
    $("messageInput").focus();
    return;
  }
  $("checkButton").disabled = true;
  $("checkButton").textContent = "Analyzing…";
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      signal: AbortSignal.timeout(15000),
    });
    const data = await response.json();
    if (!response.ok)
      throw new Error(data.error || "Analysis failed. Please try again.");
    $("spamProbability").textContent = `${data.spam_probability.toFixed(1)}%`;
    $("gauge").style.setProperty(
      "--angle",
      `${data.spam_probability * 1.8}deg`,
    );
    $("resultText").textContent =
      data.result === "SPAM"
        ? "Potential spam detected"
        : "Looks like a clean message";
    $("confidence").textContent =
      `${data.confidence}% confidence in this classification`;
    $("highlightedMessage").replaceChildren();
    const keywords = new Set(data.keywords);
    for (const token of message.split(/(\b\w+\b)/)) {
      if (keywords.has(token.toLowerCase())) {
        const mark = document.createElement("mark");
        mark.textContent = token;
        $("highlightedMessage").append(mark);
      } else $("highlightedMessage").append(document.createTextNode(token));
    }
    $("explanation").hidden = false;
    history.push({ ...data, message, time: Date.now() });
    renderDashboard();
  } catch (error) {
    $("error").textContent =
      error.name === "TimeoutError"
        ? "Analysis timed out. Please try again."
        : error.message;
    $("error").hidden = false;
  } finally {
    $("checkButton").disabled = false;
    $("checkButton").textContent = "Analyze message ↗";
  }
});
async function loadMetrics() {
  try {
    const response = await fetch("/metrics");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    $("accuracy").textContent = `${data.accuracy.toFixed(1)}%`;
    $("auc").textContent = `AUC ${data.auc.toFixed(4)}`;
    $("evaluation").textContent =
      `${data.test_size.toLocaleString()} held-out messages`;
    const labels = ["True clean", "False spam", "Missed spam", "True spam"];
    $("matrix").replaceChildren(
      ...data.confusion_matrix.flat().map((value, i) => {
        const div = document.createElement("div");
        div.textContent = value;
        const label = document.createElement("small");
        label.textContent = labels[i];
        div.append(label);
        return div;
      }),
    );
    $("rocChart").innerHTML =
      '<svg viewBox="0 0 150 120" role="img" aria-label="True positive rate versus false positive rate"><path d="M12 5V105H145" fill="none" stroke="#dbe3e9"/><path d="M12 105L145 5" stroke="#dbe3e9" stroke-dasharray="4"/><polyline points="' +
      data.roc.map(([x, y]) => `${12 + x * 133},${105 - y * 100}`).join(" ") +
      '" fill="none" stroke="#17a995" stroke-width="2"/></svg>';
  } catch (error) {
    $("metricsError").textContent = error.message;
    $("metricsError").hidden = false;
    $("evaluation").textContent = "Unavailable";
  }
}
renderDashboard();
loadMetrics();
