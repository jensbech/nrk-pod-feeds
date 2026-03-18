const BASE_URL     = "https://jensbech.github.io/nrk-pod-feeds/rss/";
const NRK_BASE_URL = "https://radio.nrk.no/podkast/";

function buildRow(feed) {
  const feedUrl = BASE_URL + feed.id + ".xml";

  let statusClass = feed.enabled ? "row-active" : "row-inactive";

  const epCount = feed.episodes === 0 ? "Alle" : (feed.episodes ? feed.episodes + " ep" : "");
  const badge   = epCount ? `<span class="ep-badge">${epCount}</span>` : "";

  return `
    <div class="feed-row ${statusClass}" data-search="${feed.title.toLowerCase()}">
      <span class="status-dot"></span>
      <div class="feed-info">
        <a class="feed-name" href="${NRK_BASE_URL}${feed.id}" target="_blank" rel="noopener">${feed.title}</a>
        <span class="feed-url">${feedUrl}</span>
      </div>
      <div class="feed-right">
        ${badge}
        <input class="url-hidden" type="text" value="${feedUrl}" id="feed_url_${feed.id}" readonly tabindex="-1" aria-hidden="true">
        <button class="copy-btn" onclick="copyToClipboard('${feed.id}', this)">Kopier</button>
      </div>
    </div>`;
}

function listFeeds() {
  const visible = feeds;
  const active  = visible.filter(f => f.enabled);

  document.getElementById("count-active").textContent = active.length;
  document.getElementById("count-total").textContent  = visible.length;

  document.getElementById("feeds_list").innerHTML = visible.map(buildRow).join("");
  updateSearchCount();
}

function copyToClipboard(id, btn) {
  const value = document.getElementById("feed_url_" + id).value;
  navigator.clipboard.writeText(value).then(() => {
    btn.textContent = "✓ Kopiert";
    btn.classList.add("copied");
    setTimeout(() => {
      btn.textContent = "Kopier";
      btn.classList.remove("copied");
    }, 2000);
  }).catch(() => {
    const input = document.getElementById("feed_url_" + id);
    input.select();
    document.execCommand("copy");
  });
}

function updateSearchCount() {
  const cards   = document.querySelectorAll(".feed-row");
  const visible = [...cards].filter(c => c.style.display !== "none").length;
  const inp     = document.getElementById("searchInput").value.trim();
  const el      = document.getElementById("searchCount");
  const empty   = document.getElementById("emptyState");

  el.textContent  = inp ? `${visible} av ${cards.length}` : "";
  if (empty) empty.hidden = visible > 0;
}

function searchFeeds() {
  const query = document.getElementById("searchInput").value.toLowerCase().trim();
  document.querySelectorAll(".feed-row").forEach(row => {
    row.style.display = row.dataset.search.includes(query) ? "" : "none";
  });
  updateSearchCount();
}

listFeeds();
