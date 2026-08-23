(function () {
  var btn = document.querySelector(".menu-btn");
  var links = document.querySelector(".primary-nav");
  if (btn && links) {
    btn.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var masthead = document.querySelector(".masthead-on-hero");
  if (!masthead) return;
  var hero = document.querySelector(".hero");
  if (!hero) return;

  var onScroll = function () {
    var passed = window.scrollY > hero.offsetHeight - 56;
    masthead.classList.toggle("is-solid", passed);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
})();
