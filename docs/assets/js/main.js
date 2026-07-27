const BASE_URL     = "https://jensbech.github.io/nrk-pod-feeds/rss/";
const NRK_BASE_URL = "https://radio.nrk.no/podkast/";

function buildCard(feed) {
  const feedUrl = BASE_URL + feed.id + ".xml";

  let statusClass = feed.enabled ? "card-active" : "card-inactive";

  const epCount = feed.episodes === 0 ? "Alle" : (feed.episodes ? feed.episodes + " ep" : "");
  const badge   = epCount ? `<span class="ep-badge">${epCount}</span>` : "";

  const cover = feed.image
    ? `<img src="${feed.image}" alt="" loading="lazy">`
    : `<span class="cover-fallback">${feed.title.charAt(0)}</span>`;

  return `
    <div class="feed-card ${statusClass}" data-search="${feed.title.toLowerCase()}">
      <a class="cover" href="${NRK_BASE_URL}${feed.id}" target="_blank" rel="noopener" aria-label="${feed.title}">
        ${cover}
        <span class="status-dot"></span>
      </a>
      <div class="card-body">
        <a class="feed-name" href="${NRK_BASE_URL}${feed.id}" target="_blank" rel="noopener" title="${feed.title}">${feed.title}</a>
        <div class="card-meta">
          ${badge}
          <input class="url-hidden" type="text" value="${feedUrl}" id="feed_url_${feed.id}" readonly tabindex="-1" aria-hidden="true">
          <button class="copy-btn" onclick="copyToClipboard('${feed.id}', this)">Kopier</button>
        </div>
      </div>
    </div>`;
}

function listFeeds() {
  const visible = feeds;
  const active  = visible.filter(f => f.enabled);

  document.getElementById("count-active").textContent = active.length;
  document.getElementById("count-total").textContent  = visible.length;

  document.getElementById("feeds_list").innerHTML = visible.map(buildCard).join("");
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
  const cards   = document.querySelectorAll(".feed-card");
  const visible = [...cards].filter(c => c.style.display !== "none").length;
  const inp     = document.getElementById("searchInput").value.trim();
  const el      = document.getElementById("searchCount");
  const empty   = document.getElementById("emptyState");

  el.textContent  = inp ? `${visible} av ${cards.length}` : "";
  if (empty) empty.hidden = visible > 0;
}

function searchFeeds() {
  const query = document.getElementById("searchInput").value.toLowerCase().trim();
  document.querySelectorAll(".feed-card").forEach(card => {
    card.style.display = card.dataset.search.includes(query) ? "" : "none";
  });
  updateSearchCount();
}

listFeeds();
