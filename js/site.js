(function () {
  var btn = document.querySelector(".menu-btn");
  var nav = document.querySelector(".site-nav");
  var head = document.querySelector(".masthead");
  if (btn && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      if (head) head.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    };
    btn.addEventListener("click", function () {
      setOpen(!nav.classList.contains("is-open"));
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setOpen(false);
      });
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setOpen(false);
    });
  }
})();

/* Reviewed market — category filter.
   Nav links (/#earbuds) and the chip row drive the same filter, so a
   category link from any page lands on a filtered browse. */
(function () {
  var masonry = document.getElementById("masonry");
  if (!masonry) return;

  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var tiles = Array.prototype.slice.call(masonry.querySelectorAll(".tile"));
  var empty = document.getElementById("market-empty");
  var valid = chips.map(function (c) { return c.getAttribute("data-filter"); });

  function apply(filter, scroll) {
    if (valid.indexOf(filter) === -1) filter = "all";
    var shown = 0;
    tiles.forEach(function (tile) {
      var on = filter === "all" || tile.getAttribute("data-cat") === filter;
      tile.hidden = !on;
      if (on) shown++;
    });
    chips.forEach(function (chip) {
      chip.setAttribute("aria-pressed", String(chip.getAttribute("data-filter") === filter));
    });
    if (empty) empty.hidden = shown !== 0;
    if (scroll && filter !== "all") {
      masonry.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var f = chip.getAttribute("data-filter");
      apply(f, false);
      history.replaceState(null, "", f === "all" ? location.pathname : "#" + f);
    });
  });

  window.addEventListener("hashchange", function () {
    apply(location.hash.replace("#", ""), true);
  });

  if (location.hash) apply(location.hash.replace("#", ""), true);
})();
