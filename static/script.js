let seenMessages = 0;

document
  .getElementById("uploadForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    //Reset
    seenMessages = 0;
    document.getElementById("statusList").innerHTML = "";
    document.getElementById("progressSection").style.display = "block";
    document.getElementById("summary").style.display = "none";
    document.getElementById("submitBtn").disabled = true;
    document.getElementById("submitBtn").textContent = "Reviewing…";

    const formData = new FormData(this);

    const response = await fetch("/review", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.error) {
      appendStatus("❌ " + data.error, "done");
      resetButton();
      return;
    }

    startPolling(data.job_id);
  });

function startPolling(jobId) {
  const interval = setInterval(async () => {
    const res = await fetch("/status/" + jobId);
    const data = await res.json();

    if (data.error) {
      clearInterval(interval);
      addStatusItem("❌ " + data.error, "done");
      resetButton();
      return;
    }

    const newMessages = data.messages.slice(seenMessages);
    newMessages.forEach((msg) => {
      if (msg.includes("Complete")) {
        // Update the existing status
        const active = document.querySelector("#statusList li.active");
        if (active) {
          active.textContent = msg;
          active.classList.remove("active");
          active.classList.add("done");
        } else {
          addStatusItem(msg, "done");
        }
      } else {
        addStatusItem(msg, msg.includes("Started") ? "active" : "");
      }
    });
    seenMessages = data.messages.length;

    if (data.done) {
      clearInterval(interval);
      showResult(data);
      resetButton();
    }
  }, 800);
}

function addStatusItem(text, cssClass) {
  const list = document.getElementById("statusList");
  const li = document.createElement("li");
  li.textContent = text;
  if (cssClass) li.classList.add(cssClass);
  list.appendChild(li);
  li.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function showResult(data) {
  document.getElementById("totalScore").textContent =
    data.totalScore + " / 100";
  document.getElementById("securityScore").textContent =
    "🔍 Security: " + data.securityScore;
  document.getElementById("costScore").textContent =
    "💰 Cost: " + data.costScore;
  document.getElementById("identityScore").textContent =
    "🔐 Identity: " + data.identityScore;
  document.getElementById("reliabilityScore").textContent =
    "⚙️ Reliability: " + data.reliabilityScore;
  document.getElementById("businessImpact").textContent = data.businessImpact;
  const keyRisks = data.keyRisks;
  keyRisks.forEach((item) => addSummaryItem("keyRisks", item));
  const topArchitecturalRisks = data.topArchitecturalRisks;
  topArchitecturalRisks.forEach((item) =>
    addSummaryItem("topArchitecturalRisks", item),
  );
  const remediationPlan = data.remediationPlan;
  const tbodyRemediation = document.querySelector("#remediationPlan tbody");
  remediationPlan.forEach((item) => {
    const trRemediation = document.createElement("tr");
    trRemediation.innerHTML = `<td>${item.priority}</td><td>${item.issue}</td><td>${item.recommendation}</td><td>${item.impact}</td>`;
    tbodyRemediation.appendChild(trRemediation);
  });
  const securityIssues = data.securityIssues;
  const tbodySecurity = document.querySelector("#securityIssues tbody");
  securityIssues.forEach((item) => {
    const trSecurity = document.createElement("tr");
    trSecurity.innerHTML = `<td>${item.id}</td><td>${item.severity}</td><td>${item.issue}</td><td>${item.explanation}</td><td>${item.recommendation}</td>`;
    tbodySecurity.appendChild(trSecurity);
  });
  const costIssues = data.costIssues;
  const tbodyCost = document.querySelector("#costIssues tbody");
  costIssues.forEach((item) => {
    const trCost = document.createElement("tr");
    trCost.innerHTML = `<td>${item.id}</td><td>${item.severity}</td><td>${item.issue}</td><td>${item.explanation}</td><td>${item.recommendation}</td>`;
    tbodyCost.appendChild(trCost);
  });
  const identityIssues = data.identityIssues;
  const tbodyIdentity = document.querySelector("#identityIssues tbody");
  identityIssues.forEach((item) => {
    const trIdentity = document.createElement("tr");
    trIdentity.innerHTML = `<td>${item.id}</td><td>${item.severity}</td><td>${item.issue}</td><td>${item.explanation}</td><td>${item.recommendation}</td>`;
    tbodyIdentity.appendChild(trIdentity);
  });
  const reliabilityIssues = data.reliabilityIssues;
  const tbodyReliability = document.querySelector("#reliabilityIssues tbody");
  reliabilityIssues.forEach((item) => {
    const trReliability = document.createElement("tr");
    trReliability.innerHTML = `<td>${item.id}</td><td>${item.severity}</td><td>${item.issue}</td><td>${item.explanation}</td><td>${item.recommendation}</td>`;
    tbodyReliability.appendChild(trReliability);
  });
  document.getElementById("summary").style.display = "block";
}

function addSummaryItem(listId, item) {
  const list = document.getElementById(listId);
  const li = document.createElement("li");
  li.textContent = item;
  list.appendChild(li);
}

function resetButton() {
  const btn = document.getElementById("submitBtn");
  btn.disabled = false;
  btn.textContent = "Review Architecture";
}

document
  .getElementById("downloadPdfBtn")
  .addEventListener("click", function () {
    window.print();
  });
