const form = document.querySelector("#researchForm");
const queryInput = document.querySelector("#queryInput");
const workflowSelect = document.querySelector("#workflowSelect");
const submitButton = document.querySelector("#submitButton");
const messageBox = document.querySelector("#messageBox");
const reportContent = document.querySelector("#reportContent");
const workflowUsed = document.querySelector("#workflowUsed");
const factVerdict = document.querySelector("#factVerdict");
const sourceCount = document.querySelector("#sourceCount");
const sourceList = document.querySelector("#sourceList");
const apiStatus = document.querySelector("#apiStatus");
const copyButton = document.querySelector("#copyButton");
const reportToolbar = document.querySelector("#reportToolbar");
const emptyState = document.querySelector("#emptyState");
const loadingScreen = document.querySelector("#loadingScreen");
const loadingLabel = document.querySelector("#loadingLabel");
const agentSteps = Array.from(document.querySelectorAll("#agentProgress span"));
const quickPrompts = Array.from(document.querySelectorAll(".quick-prompts button"));

let latestReport = "";
let progressTimer = null;
let progressIndex = 0;
let loadingTextTimer = null;
let loadingTextIndex = 0;
const loadingMessages = [
  "Research agents are warming up",
  "Searching the web for useful sources",
  "Condensing findings into a structured brief",
  "Checking claims against source context",
  "Composing the final report",
];

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalizeReportMarkdown(markdown) {
  return (markdown || "")
    .replace(/\r\n?/g, "\n")
    .replace(/[ \t]+(#{1,3}\s+)/g, "\n\n$1")
    .replace(/[ \t]+([-*]\s+)/g, "\n$1")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function formatInlineMarkdown(value) {
  return value
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>");
}

function renderMarkdown(markdown) {
  const lines = escapeHtml(normalizeReportMarkdown(markdown)).split("\n");
  const html = [];
  let inList = false;

  for (const line of lines) {
    const trimmed = line.trim();

    if (!trimmed) {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      continue;
    }

    if (trimmed.startsWith("### ")) {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      html.push(`<h3>${formatInlineMarkdown(trimmed.slice(4))}</h3>`);
    } else if (trimmed.startsWith("## ")) {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      html.push(`<h2>${formatInlineMarkdown(trimmed.slice(3))}</h2>`);
    } else if (trimmed.startsWith("# ")) {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      html.push(`<h1>${formatInlineMarkdown(trimmed.slice(2))}</h1>`);
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${formatInlineMarkdown(trimmed.slice(2))}</li>`);
    } else {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      html.push(`<p>${formatInlineMarkdown(trimmed)}</p>`);
    }
  }

  if (inList) {
    html.push("</ul>");
  }

  return html.join("");
}

function setMessage(text, type = "info") {
  messageBox.textContent = text;
  messageBox.className = `message${type === "error" ? " error" : ""}`;
}

function hideMessage() {
  messageBox.className = "message hidden";
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? "Researching..." : "Run Research";
  queryInput.disabled = isLoading;
  workflowSelect.disabled = isLoading;

  if (isLoading) {
    showLoadingScreen();
    startAgentProgress();
  } else {
    hideLoadingScreen();
    stopAgentProgress();
  }
}

function resetReportState() {
  latestReport = "";
  reportToolbar.classList.add("hidden");
  reportContent.classList.add("hidden");
  reportContent.innerHTML = "";
  copyButton.disabled = true;
  workflowUsed.textContent = "Waiting";
  factVerdict.textContent = "Waiting";
  sourceCount.textContent = "0";
  updateSources([]);
}

function showLoadingScreen() {
  emptyState.classList.add("hidden");
  reportToolbar.classList.add("hidden");
  reportContent.classList.add("hidden");
  messageBox.classList.add("hidden");
  loadingScreen.classList.remove("hidden");
  loadingTextIndex = 0;
  loadingLabel.textContent = loadingMessages[loadingTextIndex];
  window.clearInterval(loadingTextTimer);
  loadingTextTimer = window.setInterval(() => {
    loadingTextIndex = (loadingTextIndex + 1) % loadingMessages.length;
    loadingLabel.textContent = loadingMessages[loadingTextIndex];
  }, 1800);
}

function hideLoadingScreen() {
  window.clearInterval(loadingTextTimer);
  loadingTextTimer = null;
  loadingScreen.classList.add("hidden");
}

function showEmptyState() {
  emptyState.classList.remove("hidden");
  reportToolbar.classList.add("hidden");
  reportContent.classList.add("hidden");
  loadingScreen.classList.add("hidden");
}

function startAgentProgress() {
  window.clearInterval(progressTimer);
  progressIndex = 0;
  agentSteps.forEach((step) => {
    step.classList.remove("active", "done");
  });
  setProgressStep();
  progressTimer = window.setInterval(setProgressStep, 1200);
}

function setProgressStep() {
  agentSteps.forEach((step, index) => {
    step.classList.toggle("done", index < progressIndex);
    step.classList.toggle("active", index === progressIndex);
  });
  progressIndex = Math.min(progressIndex + 1, agentSteps.length - 1);
}

function stopAgentProgress() {
  window.clearInterval(progressTimer);
  progressTimer = null;
  agentSteps.forEach((step) => {
    step.classList.remove("active");
    step.classList.toggle("done", Boolean(latestReport));
  });
}

function updateSources(sources) {
  sourceCount.textContent = String(sources.length);
  sourceList.innerHTML = "";

  if (!sources.length) {
    const empty = document.createElement("li");
    empty.className = "muted";
    empty.textContent = "No sources returned for this workflow.";
    sourceList.appendChild(empty);
    return;
  }

  for (const source of sources) {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = source.url || "#";
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = source.title || "Untitled source";
    item.appendChild(link);
    sourceList.appendChild(item);
  }
}

function showResult(data) {
  latestReport = data.final_report || "";
  workflowUsed.textContent = data.workflow_used || "Unknown";
  factVerdict.textContent = data.fact_check?.overall_verdict || "Not available";
  updateSources(data.search_results || []);
  reportContent.innerHTML = renderMarkdown(latestReport);

  if (data.errors?.length) {
    setMessage(data.errors.join(" "));
  } else {
    hideMessage();
  }

  if (latestReport) {
    emptyState.classList.add("hidden");
    loadingScreen.classList.add("hidden");
    reportToolbar.classList.remove("hidden");
    reportContent.classList.remove("hidden");
    copyButton.disabled = false;
  } else {
    showEmptyState();
    setMessage("The workflow completed, but no final report was returned.", "error");
  }
}

async function checkApi() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error("API health check failed");
    }
    apiStatus.className = "status ok";
    apiStatus.lastElementChild.textContent = "API Online";
  } catch (error) {
    apiStatus.className = "status error";
    apiStatus.lastElementChild.textContent = "API Offline";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  const workflow = workflowSelect.value;

  if (!query) {
    setMessage("Please enter a research query.", "error");
    return;
  }

  resetReportState();
  setLoading(true);

  try {
    const response = await fetch("/api/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        force_workflow: workflow === "auto" ? "auto" : workflow,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Research request failed.");
    }

    showResult(data);
  } catch (error) {
    showEmptyState();
    setMessage(error.message, "error");
  } finally {
    setLoading(false);
  }
});

copyButton.addEventListener("click", async () => {
  if (!latestReport) {
    return;
  }
  await navigator.clipboard.writeText(latestReport);
  copyButton.textContent = "Copied";
  window.setTimeout(() => {
    copyButton.textContent = "Copy";
  }, 1200);
});

quickPrompts.forEach((button) => {
  button.addEventListener("click", () => {
    queryInput.value = button.dataset.query;
    queryInput.focus();
  });
});

checkApi();
