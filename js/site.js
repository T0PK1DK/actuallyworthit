(function () {
  var TAG = "actuallywo08c-20";
  var btn = document.querySelector(".menu-btn");
  var links = document.querySelector("nav.links");

  if (btn && links) {
    btn.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && links.classList.contains("open")) {
        links.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
        btn.setAttribute("aria-label", "Open menu");
        btn.focus();
      }
    });
  }

  var path = (window.location.pathname || "").replace(/\/+$/, "");
  var file = path.split("/").pop() || "index.html";
  if (file === "" || file === "/") file = "index.html";

  document.querySelectorAll("nav.links a").forEach(function (anchor) {
    var href = anchor.getAttribute("href") || "";
    var name = href.split("/").pop() || "";
    if (name === file || (file === "index.html" && (name === "index.html" || name === ""))) {
      if (href.indexOf("#") === -1) {
        anchor.setAttribute("aria-current", "page");
      }
    }
  });

  document.querySelectorAll("a.btn[data-asin]").forEach(function (anchor) {
    var asin = (anchor.getAttribute("data-asin") || "").trim();
    if (!asin) return;
    var href = anchor.getAttribute("href") || "";
    var expected = "https://www.amazon.com/dp/" + asin + "?tag=" + TAG;
    if (!href || href === "#" || href.indexOf("amazon.com/dp/") === -1 || href.indexOf("tag=" + TAG) === -1) {
      anchor.setAttribute("href", expected);
    }
    anchor.setAttribute("data-affiliate", "live");
    anchor.setAttribute("rel", "sponsored noopener noreferrer");
    if (!anchor.getAttribute("target")) anchor.setAttribute("target", "_blank");
  });

  var firstBuy = document.querySelector(".buybox .btn[data-asin]");
  var dock = document.querySelector(".buy-dock");
  if (firstBuy && dock && window.matchMedia("(max-width: 899px)").matches) {
    dock.removeAttribute("hidden");
    var dockBtn = dock.querySelector(".btn");
    if (dockBtn) {
      dockBtn.setAttribute("href", firstBuy.getAttribute("href"));
      dockBtn.setAttribute("data-asin", firstBuy.getAttribute("data-asin"));
      dockBtn.setAttribute("rel", "sponsored noopener noreferrer");
      dockBtn.setAttribute("target", "_blank");
    }
    document.body.classList.add("has-buy-dock");

    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) dock.classList.remove("is-visible");
          else dock.classList.add("is-visible");
        });
      }, { threshold: 0.15 });
      observer.observe(firstBuy.closest(".buybox") || firstBuy);
    }
  }
})();
