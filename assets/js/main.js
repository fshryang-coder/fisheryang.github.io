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

// Research image carousel
document.addEventListener("DOMContentLoaded", function () {
  // Image lists per project (filenames inside researches/<project>/charts/)
  var charts = {
    capstone: ["aa_pp_plot.png", "educ_aa_plot.png", "educ_pp_plot.png"],
    gdp_convergence: (function () {
      var arr = [];
      for (var y = 1980; y <= 2017; y++) arr.push("plot_china_us_1_" + y + ".png");
      return arr;
    })(),
    labor_market: [
      "Average Overtime Pay per Employee.png",
      "Average Retirement Benefit by Organization Group.png",
      "Average Salary by Organization Group.png",
      "Organization_Resilience.png"
    ]
  };

  document.querySelectorAll(".r-carousel").forEach(function (root) {
    var key = root.getAttribute("data-carousel");
    var files = charts[key] || [];
    var track = root.querySelector(".carousel-track");
    var dotsWrap = root.querySelector(".carousel-dots");
    if (!track || !files.length) return;

    // Build slides + dots
    files.forEach(function (fname, i) {
      var slide = document.createElement("div");
      slide.className = "carousel-slide";

      var img = document.createElement("img");
      img.alt = key + " chart " + (i + 1);
      img.loading = "lazy";
      img.decoding = "async";
      // URL-encode the filename to handle spaces / special chars
      var parts = fname.split("/");
      var encoded = parts.map(encodeURIComponent).join("/");
      img.src = "researches/" + key + "/charts/" + encoded;
      slide.appendChild(img);
      track.appendChild(slide);

      var dot = document.createElement("button");
      dot.className = "carousel-dot" + (i === 0 ? " active" : "");
      dot.setAttribute("aria-label", "Go to image " + (i + 1));
      dot.addEventListener("click", function () {
        slide.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
      });
      dotsWrap.appendChild(dot);
    });

    var dots = dotsWrap.querySelectorAll(".carousel-dot");
    var slides = track.querySelectorAll(".carousel-slide");

    // Active dot tracking on scroll
    var scrollTimer = null;
    track.addEventListener("scroll", function () {
      if (scrollTimer) return;
      scrollTimer = setTimeout(function () {
        var slideW = slides[0].offsetWidth + 12; // width + gap
        var idx = Math.round(track.scrollLeft / slideW);
        if (idx < 0) idx = 0;
        if (idx > dots.length - 1) idx = dots.length - 1;
        dots.forEach(function (d, i) { d.classList.toggle("active", i === idx); });
        scrollTimer = null;
      }, 80);
    });

    // Prev / next buttons
    var prevBtn = root.querySelector(".carousel-btn.prev");
    var nextBtn = root.querySelector(".carousel-btn.next");
    if (prevBtn) prevBtn.addEventListener("click", function () {
      var slideW = slides[0].offsetWidth + 12;
      track.scrollBy({ left: -slideW, behavior: "smooth" });
    });
    if (nextBtn) nextBtn.addEventListener("click", function () {
      var slideW = slides[0].offsetWidth + 12;
      track.scrollBy({ left: slideW, behavior: "smooth" });
    });
  });
});
