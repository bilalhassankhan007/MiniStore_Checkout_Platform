// Why JS calls the API:
// - Keep payment logic server-side (safer).
// - Client just sends quantities and redirects to Stripe Checkout URL.

(function () {
  const buyBtn = document.getElementById("buyBtn");
  if (!buyBtn) return;

  // -----------------------------
  // CSRF helpers
  // -----------------------------
  function getCsrfFromMeta() {
    const el = document.querySelector('meta[name="csrf-token"]');
    const token = el ? (el.getAttribute("content") || "").trim() : "";
    // Django sometimes renders "NOTPROVIDED" if token isn't present in context
    if (!token || token === "NOTPROVIDED") return "";
    return token;
  }

  function getCookie(name) {
    // Why: cookie is the most reliable way to fetch csrftoken in Django.
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (let c of cookies) {
      c = c.trim();
      if (c.startsWith(name + "=")) {
        return decodeURIComponent(c.substring(name.length + 1));
      }
    }
    return "";
  }

  function getCsrfToken() {
    return getCsrfFromMeta() || getCookie("csrftoken");
  }

  // -----------------------------
  // UI helpers
  // -----------------------------
  function showError(msg) {
    const box = document.getElementById("checkoutError");
    if (!box) return;
    box.textContent = msg;
    box.classList.remove("d-none");
  }

  function clearError() {
    const box = document.getElementById("checkoutError");
    if (!box) return;
    box.textContent = "";
    box.classList.add("d-none");
  }

  function setLoading(isLoading) {
    buyBtn.disabled = isLoading;
    buyBtn.textContent = isLoading ? "Redirecting…" : "Buy";
  }

  async function safeReadJson(resp) {
    // Why: sometimes Django returns HTML error pages (non-JSON)
    const contentType = resp.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      return null;
    }
    try {
      return await resp.json();
    } catch {
      return null;
    }
  }

  // -----------------------------
  // Main click handler
  // -----------------------------
  buyBtn.addEventListener("click", async () => {
    clearError();

    // Collect quantities from UI
    const inputs = document.querySelectorAll(".qty-input");
    const quantities = {};
    let totalQty = 0;

    inputs.forEach((inp) => {
      const key = inp.dataset.productKey;
      const raw = (inp.value || "0").trim();

      // Make sure value is a safe integer
      let qty = parseInt(raw, 10);
      if (!Number.isFinite(qty) || qty < 0) qty = 0;
      if (qty > 99) qty = 99; // guard UI; backend also validates

      quantities[key] = qty;
      totalQty += qty;
    });

    // Edge case: no items selected
    if (totalQty === 0) {
      showError("Please select at least 1 item (quantity > 0).");
      return;
    }

    setLoading(true);

    try {
      const csrf = getCsrfToken();
      if (!csrf) {
        // This should rarely happen, but if it does: guide user.
        showError("CSRF token missing. Refresh the page and try again.");
        return;
      }

      const resp = await fetch("/api/checkout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrf,
        },
        credentials: "same-origin", // Why: ensure session cookie is sent
        body: JSON.stringify({ quantities }),
      });

      // If not logged in, redirect to login
      if (resp.status === 401 || resp.status === 403) {
        window.location.href = "/accounts/login/?next=/";
        return;
      }

      const data = await safeReadJson(resp);

      if (!resp.ok) {
        // Prefer backend error message, else generic
        showError(
          (data && data.detail) || "Checkout failed. Please try again.",
        );
        return;
      }

      if (!data || !data.checkout_url) {
        showError("Checkout URL missing. Check server logs.");
        return;
      }

      // Redirect user to Stripe Checkout
      window.location.href = data.checkout_url;
    } catch (e) {
      showError("Network error. Please try again.");
    } finally {
      // Note: if redirect happens, this won't matter, but safe anyway.
      setLoading(false);
    }
  });
})();
