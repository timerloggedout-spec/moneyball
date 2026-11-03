/* MoneyBall install kit (Dispatch #2, annex §1): registers the
 * service worker and offers installation without nagging.
 * Chromium gets the beforeinstallprompt pill; iOS Safari has no
 * prompt API, so it gets one manual line (Share -> Add to Home
 * Screen). A dismissed or accepted prompt is remembered and
 * never re-asked. */
(function () {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(function () {});
  }
  var KEY = "mb-install-choice";
  try {
    if (localStorage.getItem(KEY)) return;
  } catch (e) {}
  function remember() {
    try {
      localStorage.setItem(KEY, "1");
    } catch (e) {}
  }
  function note(text, onTap) {
    var el = document.createElement("button");
    el.textContent = text;
    el.setAttribute(
      "style",
      "position:fixed;right:14px;bottom:14px;z-index:60;" +
        "background:#21262d;color:#e6edf3;border:1px solid #d29922;" +
        "border-radius:999px;padding:9px 16px;font:600 14px system-ui;" +
        "cursor:pointer;box-shadow:0 4px 18px rgba(0,0,0,.45)"
    );
    el.addEventListener("click", function () {
      remember();
      el.remove();
      if (onTap) onTap();
    });
    document.body.appendChild(el);
  }
  var deferred = null;
  window.addEventListener("beforeinstallprompt", function (event) {
    event.preventDefault();
    deferred = event;
    note("Install MoneyBall", function () {
      if (!deferred) return;
      deferred.prompt();
      deferred.userChoice.then(function () {
        deferred = null;
      });
    });
  });
  window.addEventListener("appinstalled", remember);
  var isIOS =
    /iphone|ipad|ipod/i.test(navigator.userAgent) &&
    !window.MSStream;
  var standalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    navigator.standalone;
  if (isIOS && !standalone) {
    note("Add MoneyBall: Share → Add to Home Screen", null);
  }
})();
