// Mobile navigation toggle
document.addEventListener("DOMContentLoaded", function () {
  var btn = document.querySelector(".menu-btn");
  var nav = document.querySelector("nav.site-nav");
  if (!btn || !nav) return;
  btn.addEventListener("click", function () {
    nav.classList.toggle("open");
  });
  // Close menu when a link is clicked (mobile)
  nav.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () { nav.classList.remove("open"); });
  });
});
