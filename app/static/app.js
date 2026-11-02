// DentalClin: small progressive enhancements. The page works fully without this file.
(function () {
  var root = document.documentElement;
  root.classList.add("js");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.addEventListener("DOMContentLoaded", function () {
    // Hero: masked line reveal, then the rest rises.
    requestAnimationFrame(function () { requestAnimationFrame(function () { root.classList.add("ready"); }); });

    // Entrance for the parts of every section, staggered, once.
    var items = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
    items.forEach(function (el) {
      var siblings = el.parentElement.querySelectorAll(":scope > .reveal");
      el.style.setProperty("--d", Array.prototype.indexOf.call(siblings, el) * 80 + "ms");
    });
    if ("IntersectionObserver" in window && !reduce) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
      items.forEach(function (el) { io.observe(el); });
    } else {
      items.forEach(function (el) { el.classList.add("is-in"); });
    }

    // Slow drift on the night photograph while the panel scrolls past (transform only).
    var pic = document.querySelector(".clinica__pic img");
    if (pic && !reduce) {
      var ticking = false;
      var update = function () {
        var r = pic.getBoundingClientRect(), vh = window.innerHeight;
        var p = Math.max(-1, Math.min(1, (r.top + r.height / 2 - vh / 2) / vh));
        pic.style.transform = "translateY(" + (p * -18).toFixed(1) + "px) scale(1.08)";
        ticking = false;
      };
      window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
      update();
    }

    // The live thing: the coupon builds the WhatsApp message from the visitor's choices.
    var base = document.body.getAttribute("data-wa");
    var go = document.getElementById("wa-go");
    var a = document.getElementById("f-interesse"), b = document.getElementById("f-quando");
    var form = document.getElementById("wa-form");
    if (base && go && a && b) {
      var build = function () {
        var what = a.options[a.selectedIndex].text.toLowerCase();
        var msg = "Olá! Tenho interesse em: " + what + ". Gostaria de atendimento " + b.value + ".";
        go.href = base + "?text=" + encodeURIComponent(msg);
      };
      a.addEventListener("change", build); b.addEventListener("change", build); build();
      form.addEventListener("submit", function (e) { e.preventDefault(); go.click(); });
    }
  });
})();
