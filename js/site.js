(function () {
  var btn = document.querySelector(".menu-btn");
  var links = document.querySelector("nav.links");
  if (!btn || !links) return;
  btn.addEventListener("click", function () {
    var open = links.classList.toggle("open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();
