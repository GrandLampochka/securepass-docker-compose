const $ = id => document.getElementById(id);

async function request(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : JSON.stringify(data.detail || data)
    );
  }

  return data;
}

async function generatePassword() {
  const result = $("passwordResult");
  result.textContent = "Генерация...";

  const payload = {
    length: Number($("length").value),
    uppercase: $("uppercase").checked,
    lowercase: $("lowercase").checked,
    digits: $("digits").checked,
    symbols: $("symbols").checked
  };

  try {
    const data = await request("/api/password/generate", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    result.textContent = data.password;
    await loadAudit();
  } catch (error) {
    result.textContent = "Ошибка: " + error.message;
  }
}

async function generateHash() {
  const result = $("hashResult");
  result.textContent = "Вычисление...";

  try {
    const data = await request("/api/hash/generate", {
      method: "POST",
      body: JSON.stringify({
        text: $("hashText").value,
        algorithm: $("algorithm").value
      })
    });

    result.textContent = data.hash;
    await loadAudit();
  } catch (error) {
    result.textContent = "Ошибка: " + error.message;
  }
}

async function loadAudit() {
  const body = $("auditBody");

  try {
    const logs = await request("/api/audit");
    body.replaceChildren();

    if (!logs.length) {
      const row = body.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 5;
      cell.textContent = "Журнал пуст";
      return;
    }

    for (const log of logs) {
      const row = body.insertRow();

      const values = [
        log.id,
        log.operation,
        log.algorithm || "—",
        log.status,
        new Date(log.created_at).toLocaleString("ru-RU")
      ];

      values.forEach((value, index) => {
        const cell = row.insertCell();

        if (index === 3) {
          const badge = document.createElement("span");
          badge.className =
            "status" + (value === "success" ? "" : " failed");
          badge.textContent = value;
          cell.appendChild(badge);
        } else {
          cell.textContent = value;
        }
      });
    }
  } catch (error) {
    body.replaceChildren();
    const row = body.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 5;
    cell.textContent = "Ошибка: " + error.message;
  }
}

async function clearAudit() {
  if (!confirm("Очистить журнал безопасности?")) return;

  try {
    await request("/api/audit", { method: "DELETE" });
    await loadAudit();
  } catch (error) {
    alert("Ошибка: " + error.message);
  }
}

async function copyResult(id, button) {
  const value = $(id).textContent;

  if (!value || value.startsWith("Результат") ||
      value.startsWith("Ошибка")) return;

  try {
    await navigator.clipboard.writeText(value);
    const original = button.textContent;
    button.textContent = "✓";

    setTimeout(() => {
      button.textContent = original;
    }, 1500);
  } catch (error) {
    alert("Не удалось скопировать результат");
  }
}

$("generatePassword").addEventListener("click", generatePassword);
$("generateHash").addEventListener("click", generateHash);
$("refreshAudit").addEventListener("click", loadAudit);
$("clearAudit").addEventListener("click", clearAudit);

document.querySelectorAll("[data-copy]").forEach(button => {
  button.addEventListener("click", () => {
    copyResult(button.dataset.copy, button);
  });
});

loadAudit();
