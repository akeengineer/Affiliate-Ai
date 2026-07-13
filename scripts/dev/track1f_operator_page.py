#!/usr/bin/env python3
from __future__ import annotations


def render_operator_page() -> str:
    return """<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ตัวจัดการ Affiliate Product — Local Demo</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f4ed;
      --card: #fffefa;
      --ink: #222018;
      --muted: #756f63;
      --line: #ded6c7;
      --soft: #f0eadf;
      --accent: #2f6f5e;
      --accent-ink: #ffffff;
      --warn-bg: #fff7dc;
      --warn-line: #e0a82e;
      --error-bg: #fff2ee;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Noto Sans Thai", "Sarabun", "Tahoma", sans-serif;
      background: linear-gradient(180deg, #fbfaf6 0%, var(--bg) 100%);
      color: var(--ink);
    }
    main {
      max-width: 68rem;
      margin: 0 auto;
      padding: 2rem 1rem 3rem;
    }
    header {
      margin-bottom: 1.25rem;
    }
    h1 {
      margin: 0 0 0.4rem;
      font-size: clamp(1.8rem, 4vw, 3rem);
      letter-spacing: -0.03em;
    }
    h2 {
      margin: 0 0 0.75rem;
      font-size: 1.2rem;
    }
    p {
      margin: 0 0 0.8rem;
      line-height: 1.6;
      color: var(--muted);
    }
    .notice, .panel {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 1rem;
      box-shadow: 0 0.5rem 1.5rem rgba(34, 32, 24, 0.05);
    }
    .notice {
      padding: 1rem;
      border-left: 0.35rem solid var(--warn-line);
      background: var(--warn-bg);
    }
    .status-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 0.75rem;
      align-items: start;
      margin: 1rem 0;
    }
    .grid {
      display: grid;
      grid-template-columns: minmax(17rem, 0.85fr) minmax(18rem, 1.15fr);
      gap: 1rem;
      margin-top: 1rem;
    }
    .panel {
      padding: 1rem;
    }
    .compact {
      margin-top: 1rem;
    }
    label {
      display: grid;
      gap: 0.3rem;
      margin-bottom: 0.75rem;
      color: var(--muted);
      font-size: 0.94rem;
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
      min-height: 5rem;
      resize: vertical;
    }
    button {
      border: 0;
      border-radius: 999px;
      padding: 0.72rem 1rem;
      background: var(--accent);
      color: var(--accent-ink);
      cursor: pointer;
      font-weight: 700;
    }
    button.secondary {
      background: var(--soft);
      color: var(--ink);
    }
    .section-head {
      display: flex;
      gap: 0.75rem;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.6rem;
    }
    .helper {
      font-size: 0.9rem;
      color: var(--muted);
    }
    .list {
      display: grid;
      gap: 0.65rem;
    }
    .item {
      border: 1px solid var(--line);
      border-radius: 0.8rem;
      padding: 0.75rem;
      background: #fff;
    }
    .item strong {
      display: block;
      margin-bottom: 0.25rem;
    }
    .meta {
      display: grid;
      gap: 0.2rem;
      color: var(--muted);
      font-size: 0.9rem;
    }
    details {
      margin-top: 0.75rem;
    }
    summary {
      cursor: pointer;
      color: var(--accent);
      font-weight: 700;
    }
    pre {
      margin: 0.65rem 0 0;
      padding: 0.75rem;
      border-radius: 0.75rem;
      border: 1px solid var(--line);
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      background: #fbfaf7;
      font-family: "Courier New", monospace;
      font-size: 0.82rem;
    }
    #operator-error-panel {
      background: var(--error-bg);
    }
    @media (max-width: 760px) {
      main { padding: 1.25rem 0.8rem 2rem; }
      .status-row, .grid { grid-template-columns: 1fr; }
      .section-head { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>ตัวจัดการ Affiliate Product — Local Demo</h1>
      <p>ใช้สำหรับทดสอบ Product และ Affiliate Offer บนเครื่อง local เท่านั้น</p>
      <div class="notice">
        <strong>โหมด Local เท่านั้น:</strong>
        หน้านี้ใช้สำหรับทดสอบในเครื่อง ไม่ใช่ระบบ Production และยังไม่มี Authentication, RBAC หรือ Deployment สำหรับใช้งานจริง
      </div>
    </header>

    <section class="panel status-row">
      <div>
        <h2>สถานะระบบ</h2>
        <p class="helper">ตรวจสอบ runtime, storage และ boundary ของ Track 1 local demo</p>
        <div id="runtime-status-summary" class="meta">กำลังโหลดสถานะระบบ...</div>
        <details>
          <summary>ดู JSON รายละเอียด</summary>
          <pre id="runtime-status-panel">กำลังโหลดสถานะระบบ...</pre>
        </details>
      </div>
      <button type="button" class="secondary" onclick="loadRuntimeStatus()">รีเฟรชสถานะ</button>
    </section>

    <section class="grid">
      <div class="panel">
        <h2>เพิ่มสินค้า</h2>
        <form id="product-form">
          <label>ชื่อสินค้า
            <input id="product-name" name="name" value="สินค้า Local Demo">
          </label>
          <label>หมวดหมู่
            <input id="product-category" name="category" value="productivity">
          </label>
          <label>รายละเอียด
            <textarea id="product-description" name="description">สร้างจากหน้า operator local demo</textarea>
          </label>
          <button type="submit">สร้างสินค้า</button>
        </form>
      </div>

      <div class="panel">
        <div class="section-head">
          <h2>รายการสินค้า</h2>
          <button type="button" class="secondary" onclick="loadProducts()">รีเฟรชรายการสินค้า</button>
        </div>
        <div id="product-list-panel" class="list">กำลังโหลดรายการสินค้า...</div>
        <details>
          <summary>ดู JSON รายละเอียด</summary>
          <pre id="product-list-json">กำลังโหลดรายการสินค้า...</pre>
        </details>
      </div>
    </section>

    <section class="grid">
      <div class="panel">
        <h2>เพิ่ม Affiliate Offer</h2>
        <p class="helper">สร้าง Product ก่อน แล้วนำ Product ID มาใช้สร้าง Affiliate Offer</p>
        <p class="helper">ใช้ Source ID ตัวอย่าง: <code>demo-source-track1d</code></p>
        <form id="affiliate-offer-form">
          <label>Product ID
            <input id="offer-product-id" name="product_id" value="demo-product-track1e">
          </label>
          <label>Source ID
            <input id="offer-source-id" name="source_id" value="demo-source-track1d">
          </label>
          <label>Offer URL
            <input id="offer-url" name="offer_url" value="https://example.com/operator-offer">
          </label>
          <label>ชื่อ Offer
            <input id="offer-title" name="title" value="Local Demo Offer">
          </label>
          <button type="submit">สร้าง Affiliate Offer</button>
        </form>
      </div>

      <div class="panel">
        <div class="section-head">
          <h2>รายการ Affiliate Offer</h2>
          <button type="button" class="secondary" onclick="loadAffiliateOffers()">รีเฟรชรายการ Offer</button>
        </div>
        <div id="affiliate-offer-list-panel" class="list">กำลังโหลดรายการ Offer...</div>
        <details>
          <summary>ดู JSON รายละเอียด</summary>
          <pre id="affiliate-offer-list-json">กำลังโหลดรายการ Offer...</pre>
        </details>
      </div>
    </section>

    <section class="grid compact">
      <div class="panel">
        <h2>ผลลัพธ์ล่าสุด</h2>
        <pre id="operator-result-panel">ยังไม่มีผลลัพธ์ล่าสุด</pre>
      </div>
      <div class="panel">
        <h2>ข้อผิดพลาดล่าสุด</h2>
        <pre id="operator-error-panel">ยังไม่มีข้อผิดพลาด</pre>
      </div>
    </section>
  </main>

  <script>
    async function requestJson(path, options) {
      const response = await fetch(path, options);
      const text = await response.text();
      let data = {};
      try {
        data = text ? JSON.parse(text) : {};
      } catch (error) {
        data = { error: "invalid_json_response", message: text };
      }
      if (!response.ok) {
        throw data;
      }
      return data;
    }

    function formatJson(data) {
      return JSON.stringify(data, null, 2);
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function showResult(data) {
      document.getElementById("operator-result-panel").textContent = formatJson(data);
      document.getElementById("operator-error-panel").textContent = "ยังไม่มีข้อผิดพลาด";
    }

    function showError(error) {
      document.getElementById("operator-error-panel").textContent = formatJson(error);
    }

    function renderRuntimeSummary(data) {
      document.getElementById("runtime-status-summary").innerHTML = [
        "Runtime: " + escapeHtml(data.runtime_mode || "-"),
        "Storage: " + escapeHtml(data.storage_runtime || "-"),
        "Product API: " + escapeHtml(data.product_core_api_status || "-"),
        "Operator: " + escapeHtml(data.minimal_operator_flow_status || "-"),
        "Production: " + escapeHtml(data.production_deployment_status || "-")
      ].map(function (line) { return "<span>" + line + "</span>"; }).join("");
    }

    function renderProducts(data) {
      const products = data.products || [];
      const panel = document.getElementById("product-list-panel");
      document.getElementById("product-list-json").textContent = formatJson(data);
      if (!products.length) {
        panel.textContent = "ยังไม่มีข้อมูลสินค้า";
        return;
      }
      panel.innerHTML = products.map(function (product) {
        return '<article class="item">'
          + '<strong>' + escapeHtml(product.name || product.id) + '</strong>'
          + '<div class="meta">'
          + '<span>Product ID: ' + escapeHtml(product.id) + '</span>'
          + '<span>หมวดหมู่: ' + escapeHtml(product.category || "-") + '</span>'
          + '<span>Status: ' + escapeHtml(product.status || "-") + '</span>'
          + '</div>'
          + '</article>';
      }).join("");
    }

    function renderAffiliateOffers(data) {
      const offers = data.affiliate_offers || [];
      const panel = document.getElementById("affiliate-offer-list-panel");
      document.getElementById("affiliate-offer-list-json").textContent = formatJson(data);
      if (!offers.length) {
        panel.textContent = "ยังไม่มี Affiliate Offer";
        return;
      }
      panel.innerHTML = offers.map(function (offer) {
        return '<article class="item">'
          + '<strong>' + escapeHtml(offer.title || offer.id) + '</strong>'
          + '<div class="meta">'
          + '<span>Offer ID: ' + escapeHtml(offer.id) + '</span>'
          + '<span>Product ID: ' + escapeHtml(offer.product_id) + '</span>'
          + '<span>Source ID: ' + escapeHtml(offer.source_id) + '</span>'
          + '<span>Offer URL: ' + escapeHtml(offer.offer_url || "-") + '</span>'
          + '<span>Status: ' + escapeHtml(offer.status || "-") + '</span>'
          + '</div>'
          + '</article>';
      }).join("");
    }

    async function loadRuntimeStatus() {
      const data = await requestJson("/runtime/status", { method: "GET" });
      renderRuntimeSummary(data);
      document.getElementById("runtime-status-panel").textContent = formatJson(data);
      return data;
    }

    async function loadProducts() {
      const data = await requestJson("/products", { method: "GET" });
      renderProducts(data);
      return data;
    }

    async function loadAffiliateOffers() {
      const data = await requestJson("/affiliate-offers", { method: "GET" });
      renderAffiliateOffers(data);
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
        document.getElementById("offer-product-id").value = data.id || document.getElementById("offer-product-id").value;
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
