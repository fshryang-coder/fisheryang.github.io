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

    // Click image to open lightbox
    var imgList = track.querySelectorAll("img");
    imgList.forEach(function (img, i) {
      img.style.cursor = "zoom-in";
      img.addEventListener("click", function () {
        openLightbox(files, key, i);
      });
    });
  });
});

// ---- Lightbox (full-screen image viewer with manual playback) ----
var lightbox = null;
var lbImg = null;
var lbCounter = null;
var lbPrev = null;
var lbNext = null;
var lbPlay = null;
var lbClose = null;
var lbState = { urls: [], idx: 0, playing: false, timer: null };

function buildLightbox() {
  if (lightbox) return;
  lightbox = document.createElement("div");
  lightbox.className = "lightbox";
  lightbox.innerHTML =
    '<button class="lb-close" aria-label="Close">&times;</button>' +
    '<button class="lb-nav lb-prev" aria-label="Previous">&#8249;</button>' +
    '<img class="lb-img" alt="Full view" />' +
    '<button class="lb-nav lb-next" aria-label="Next">&#8250;</button>' +
    '<div class="lb-controls">' +
      '<button class="lb-play" aria-label="Play/Pause">&#9654;</button>' +
      '<span class="lb-counter">1 / 1</span>' +
    '</div>';
  document.body.appendChild(lightbox);

  lbImg = lightbox.querySelector(".lb-img");
  lbCounter = lightbox.querySelector(".lb-counter");
  lbPrev = lightbox.querySelector(".lb-prev");
  lbNext = lightbox.querySelector(".lb-next");
  lbPlay = lightbox.querySelector(".lb-play");
  lbClose = lightbox.querySelector(".lb-close");

  lbPrev.addEventListener("click", function (e) { e.stopPropagation(); lbShow(lbState.idx - 1); });
  lbNext.addEventListener("click", function (e) { e.stopPropagation(); lbShow(lbState.idx + 1); });
  lbPlay.addEventListener("click", function (e) { e.stopPropagation(); lbTogglePlay(); });
  lbClose.addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", function (e) { if (e.target === lightbox || e.target === lbImg) closeLightbox(); });

  // Keyboard controls
  document.addEventListener("keydown", function (e) {
    if (!lightbox.classList.contains("open")) return;
    if (e.key === "ArrowLeft") { e.preventDefault(); lbShow(lbState.idx - 1); }
    else if (e.key === "ArrowRight") { e.preventDefault(); lbShow(lbState.idx + 1); }
    else if (e.key === " ") { e.preventDefault(); lbTogglePlay(); }
    else if (e.key === "Escape") { e.preventDefault(); closeLightbox(); }
  });
}

function openLightbox(files, key, startIdx) {
  buildLightbox();
  lbState.urls = files.map(function (fname) {
    var parts = fname.split("/");
    var encoded = parts.map(encodeURIComponent).join("/");
    return "researches/" + key + "/charts/" + encoded;
  });
  lbState.idx = startIdx || 0;
  lightbox.classList.add("open");
  document.body.style.overflow = "hidden";
  lbShow(lbState.idx);
}

function lbShow(idx) {
  if (lbState.urls.length === 0) return;
  // Wrap around
  if (idx < 0) idx = lbState.urls.length - 1;
  if (idx > lbState.urls.length - 1) idx = 0;
  lbState.idx = idx;
  lbImg.src = lbState.urls[idx];
  lbCounter.textContent = (idx + 1) + " / " + lbState.urls.length;
  // If playing, keep advancing
  if (lbState.playing) {
    lbRestartTimer();
  }
}

function lbTogglePlay() {
  lbState.playing = !lbState.playing;
  if (lbState.playing) {
    lbPlay.innerHTML = "&#10074;&#10074;"; // pause icon
    lbPlay.setAttribute("aria-label", "Pause");
    lbRestartTimer();
  } else {
    lbPlay.innerHTML = "&#9654;"; // play icon
    lbPlay.setAttribute("aria-label", "Play");
    clearTimeout(lbState.timer);
  }
}

function lbRestartTimer() {
  clearTimeout(lbState.timer);
  lbState.timer = setTimeout(function () {
    lbShow(lbState.idx + 1);
  }, 2500);
}

function closeLightbox() {
  if (!lightbox) return;
  lightbox.classList.remove("open");
  document.body.style.overflow = "";
  lbState.playing = false;
  clearTimeout(lbState.timer);
  if (lbPlay) {
    lbPlay.innerHTML = "&#9654;";
    lbPlay.setAttribute("aria-label", "Play");
  }
  if (lbImg) lbImg.src = "";
}
