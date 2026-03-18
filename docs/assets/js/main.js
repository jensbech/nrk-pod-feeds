const BASE_URL      = "https://jensbech.github.io/nrk-pod-feeds/rss/";
const NRK_BASE_URL  = "https://radio.nrk.no/podkast/";
const TITLE_RE      = /^De (\d+) siste fra (.+)$/;

function parseTitle(title) {
  const m = title.match(TITLE_RE);
  return m ? { count: m[1], name: m[2] } : { count: null, name: title };
}

function buildCard(feed, index) {
  const { count, name } = parseTitle(feed.title);
  const feedUrl = BASE_URL + feed.id + ".xml";

  let statusClass = "card-active";
  if (feed.ignore)         statusClass = "card-obsolete";
  else if (!feed.enabled)  statusClass = "card-inactive";

  const badge = count ? `<span class="ep-badge">${count} ep</span>` : "";

  return `
    <div class="card ${statusClass}" data-search="${name.toLowerCase()}">
      <div class="card-strip"></div>
      <div class="card-body">
        <div class="card-top">
          <a class="card-name" href="${NRK_BASE_URL}${feed.id}" target="_blank" rel="noopener">${name}</a>
          ${badge}
        </div>
        <div class="card-url-row">
          <input class="url-input" type="text" value="${feedUrl}" id="feed_url_${feed.id}" readonly tabindex="-1">
          <button class="copy-btn" onclick="copyToClipboard('${feed.id}', this)" aria-label="Kopier RSS-lenke">Kopier</button>
        </div>
      </div>
    </div>`;
}

function listFeeds() {
  const visible = feeds.filter(f => !f.hidden);
  const active  = visible.filter(f => f.enabled && !f.ignore);

  document.getElementById("count-active").textContent = active.length;
  document.getElementById("count-total").textContent  = visible.length;

  const html = visible.map((f, i) => buildCard(f, i)).join("");
  document.getElementById("feeds_list").innerHTML = html;
  updateSearchCount();
}

function copyToClipboard(id, btn) {
  const input = document.getElementById("feed_url_" + id);
  navigator.clipboard.writeText(input.value).then(() => {
    btn.textContent = "✓ Kopiert";
    btn.classList.add("copied");
    setTimeout(() => {
      btn.textContent = "Kopier";
      btn.classList.remove("copied");
    }, 2000);
  }).catch(() => {
    input.select();
    document.execCommand("copy");
  });
}

function updateSearchCount() {
  const cards   = document.querySelectorAll(".card");
  const visible = [...cards].filter(c => c.style.display !== "none");
  const total   = cards.length;
  const el      = document.getElementById("searchCount");
  const inp     = document.getElementById("searchInput");
  const empty   = document.getElementById("emptyState");

  if (inp.value.trim() === "") {
    el.textContent = "";
  } else {
    el.textContent = `${visible.length} av ${total}`;
  }

  if (empty) empty.hidden = visible.length > 0;
}

function searchFeeds() {
  const query = document.getElementById("searchInput").value.toLowerCase().trim();
  const cards = document.querySelectorAll(".card");

  cards.forEach(card => {
    const name = card.dataset.search || "";
    card.style.display = name.includes(query) ? "" : "none";
  });

  updateSearchCount();
}

listFeeds();
