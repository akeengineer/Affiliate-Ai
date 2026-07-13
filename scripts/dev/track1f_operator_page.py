#!/usr/bin/env python3
from __future__ import annotations


def render_operator_page() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Affiliate AI Operator</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f2e8;
      --panel: #fffdf8;
      --ink: #1d1b16;
      --muted: #6b6352;
      --line: #d9cfbe;
      --accent: #b65f2a;
      --accent-ink: #fff9f3;
      --warn: #fff4d8;
      --result: #f3f7ed;
      --error: #fff0ea;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, rgba(182, 95, 42, 0.14), transparent 28rem),
        linear-gradient(180deg, #fbf7ef 0%, var(--bg) 100%);
      color: var(--ink);
    }
    main {
      max-width: 72rem;
      margin: 0 auto;
      padding: 2rem 1.25rem 3rem;
    }
    h1, h2 {
      margin: 0 0 0.75rem;
      line-height: 1.1;
    }
    p {
      margin: 0 0 1rem;
      line-height: 1.5;
    }
    .hero, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 1rem;
      box-shadow: 0 0.75rem 2rem rgba(29, 27, 22, 0.06);
    }
    .hero {
      padding: 1.5rem;
      margin-bottom: 1rem;
    }
    .boundary {
      background: var(--warn);
      border-left: 0.35rem solid var(--accent);
      padding: 1rem 1rem 1rem 1.25rem;
      margin-top: 1rem;
      border-radius: 0.75rem;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
      gap: 1rem;
      margin-top: 1rem;
    }
    .panel {
      padding: 1rem;
    }
    .panel-actions {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-bottom: 0.75rem;
    }
    form {
      display: grid;
      gap: 0.65rem;
    }
    label {
      display: grid;
      gap: 0.25rem;
      font-size: 0.95rem;
      color: var(--muted);
    }
    input, textarea, button {
      font: inherit;
    }
    input, textarea {
      width: 100%;
      padding: 0.7rem 0.8rem;
      border: 1px solid var(--line);
      border-radius: 0.7rem;
      background: #fff;
      color: var(--ink);
    }
    textarea {
      min-height: 6rem;
      resize: vertical;
    }
    button {
      border: 0;
      border-radius: 999px;
      padding: 0.7rem 1rem;
      background: var(--accent);
      color: var(--accent-ink);
      cursor: pointer;
    }
    button.secondary {
      background: #efe5d6;
      color: var(--ink);
    }
    pre {
      margin: 0;
      padding: 0.85rem;
      border-radius: 0.85rem;
      border: 1px solid var(--line);
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "Courier New", monospace;
      font-size: 0.9rem;
    }
    #runtime-status-panel, #product-list-panel, #affiliate-offer-list-panel {
      background: #fbfaf7;
    }
    #operator-result-panel {
      background: var(--result);
    }
    #operator-error-panel {
      background: var(--error);
    }
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>Track 1F Operator Surface</h1>
      <p>Track 1F provides a local-only operator flow for Product and AffiliateOffer usage.</p>
      <div class="boundary">
        <p><strong>Local-only boundary notice:</strong> this page stays inside the Track 1C/1D/1E local runtime and uses existing Track 1E APIs only. No production frontend deployment, auth, RBAC, signing, verifier runtime, key custody runtime, cloud infrastructure, or CI/CD deployment pipeline is introduced.</p>
        <p>Use the deterministic demo source id <code>demo-source-track1d</code> for local AffiliateOffer creation when working from seeded local demo data.</p>
      </div>
    </section>

    <div class="grid">
      <section class="panel">
        <h2>Runtime Status</h2>
        <div class="panel-actions">
          <button type="button" class="secondary" onclick="loadRuntimeStatus()">Refresh Runtime Status</button>
        </div>
        <pre id="runtime-status-panel">Loading runtime status...</pre>
      </section>

      <section class="panel">
        <h2>Result Panel</h2>
        <pre id="operator-result-panel">No operator action has been run yet.</pre>
      </section>

      <section class="panel">
        <h2>Error Panel</h2>
        <pre id="operator-error-panel">No operator error has been returned.</pre>
      </section>
    </div>

    <div class="grid">
      <section class="panel">
        <h2>Add Product</h2>
        <form id="product-form">
          <label>Name
            <input id="product-name" name="name" value="Track 1F Demo Product">
          </label>
          <label>Category
            <input id="product-category" name="category" value="productivity">
          </label>
          <label>Description
            <textarea id="product-description" name="description">Created from the Track 1F operator page.</textarea>
          </label>
          <button type="submit">Create Product</button>
        </form>
      </section>

      <section class="panel">
        <h2>Product List</h2>
        <div class="panel-actions">
          <button type="button" class="secondary" onclick="loadProducts()">Refresh Product List</button>
        </div>
        <pre id="product-list-panel">Loading products...</pre>
      </section>
    </div>

    <div class="grid">
      <section class="panel">
        <h2>Add Affiliate Offer</h2>
        <form id="affiliate-offer-form">
          <label>Product Id
            <input id="offer-product-id" name="product_id" value="demo-product-track1e">
          </label>
          <label>Source Id
            <input id="offer-source-id" name="source_id" value="demo-source-track1d">
          </label>
          <label>Offer URL
            <input id="offer-url" name="offer_url" value="https://example.com/operator-offer">
          </label>
          <label>Title
            <input id="offer-title" name="title" value="Track 1F Demo Offer">
          </label>
          <button type="submit">Create Affiliate Offer</button>
        </form>
      </section>

      <section class="panel">
        <h2>Affiliate Offer List</h2>
        <div class="panel-actions">
          <button type="button" class="secondary" onclick="loadAffiliateOffers()">Refresh Affiliate Offer List</button>
        </div>
        <pre id="affiliate-offer-list-panel">Loading affiliate offers...</pre>
      </section>
    </div>
  </main>

  <script>
    async function requestJson(path, options) {
      const response = await fetch(path, options);
      const text = await response.text();
      const data = text ? JSON.parse(text) : {};
      if (!response.ok) {
        throw data;
      }
      return data;
    }

    function showResult(data) {
      document.getElementById("operator-result-panel").textContent = JSON.stringify(data, null, 2);
      document.getElementById("operator-error-panel").textContent = "No operator error has been returned.";
    }

    function showError(error) {
      document.getElementById("operator-error-panel").textContent = JSON.stringify(error, null, 2);
    }

    async function loadRuntimeStatus() {
      const data = await requestJson("/runtime/status", { method: "GET" });
      document.getElementById("runtime-status-panel").textContent = JSON.stringify(data, null, 2);
      return data;
    }

    async function loadProducts() {
      const data = await requestJson("/products", { method: "GET" });
      document.getElementById("product-list-panel").textContent = JSON.stringify(data, null, 2);
      return data;
    }

    async function loadAffiliateOffers() {
      const data = await requestJson("/affiliate-offers", { method: "GET" });
      document.getElementById("affiliate-offer-list-panel").textContent = JSON.stringify(data, null, 2);
      return data;
    }

    document.getElementById("product-form").addEventListener("submit", async function (event) {
      event.preventDefault();
      try {
        const payload = {
          name: document.getElementById("product-name").value,
          category: document.getElementById("product-category").value,
          description: document.getElementById("product-description").value,
        };
        const data = await requestJson("/products", {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify(payload),
        });
        showResult(data);
        await loadProducts();
      } catch (error) {
        showError(error);
      }
    });

    document.getElementById("affiliate-offer-form").addEventListener("submit", async function (event) {
      event.preventDefault();
      try {
        const payload = {
          product_id: document.getElementById("offer-product-id").value,
          source_id: document.getElementById("offer-source-id").value,
          offer_url: document.getElementById("offer-url").value,
          title: document.getElementById("offer-title").value,
        };
        const data = await requestJson("/affiliate-offers", {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify(payload),
        });
        showResult(data);
        await loadAffiliateOffers();
      } catch (error) {
        showError(error);
      }
    });

    Promise.all([loadRuntimeStatus(), loadProducts(), loadAffiliateOffers()]).catch(showError);
  </script>
</body>
</html>
"""
