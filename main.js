(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------- mobile nav ---------------- */
  const navToggle = document.getElementById("navToggle");
  const mainNav = document.getElementById("mainNav");
  if (navToggle && mainNav) {
    navToggle.addEventListener("click", () => {
      const isOpen = mainNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });
    mainNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mainNav.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------------- theme picker ---------------- */
  const heroMock = document.getElementById("heroMock");
  const chips = document.querySelectorAll(".theme-chip");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const theme = chip.getAttribute("data-theme");
      if (heroMock) heroMock.setAttribute("data-theme", theme);
      chips.forEach((c) => c.classList.toggle("is-active", c === chip));
    });
  });

  /* ---------------- hero smooth-caret demo ---------------- */
  // Positions expressed in "ch" units along the sample line, mirroring
  // how the real editor's caret glides between character columns.
  const heroCaret = document.getElementById("heroCaret");
  if (heroCaret && !reduceMotion) {
    const stops = [44, 30, 18, 4, 44];
    let i = 0;
    setInterval(() => {
      i = (i + 1) % stops.length;
      heroCaret.classList.add("is-still");
      heroCaret.style.left = stops[i] + "ch";
      window.setTimeout(() => heroCaret.classList.remove("is-still"), 550);
    }, 1900);
  } else if (heroCaret) {
    heroCaret.classList.add("is-still");
  }

  /* ---------------- console typing demo (plays once, on scroll) ---------------- */
  const terminal = document.getElementById("terminalDemo");
  const typedEl = document.getElementById("terminalTyped");
  const caretEl = document.getElementById("terminalCaret");
  const replyEl = document.getElementById("terminalReply");
  const doneEl = document.getElementById("terminalDone");

  function playConsoleDemo() {
    const word = "Ada";
    if (reduceMotion) {
      typedEl.textContent = word;
      replyEl.hidden = false;
      doneEl.hidden = false;
      return;
    }
    let idx = 0;
    const typeNext = () => {
      if (idx < word.length) {
        typedEl.textContent += word[idx];
        idx += 1;
        window.setTimeout(typeNext, 160);
      } else {
        window.setTimeout(() => {
          if (caretEl) caretEl.style.visibility = "hidden";
          replyEl.hidden = false;
          window.setTimeout(() => { doneEl.hidden = false; }, 500);
        }, 400);
      }
    };
    window.setTimeout(typeNext, 700);
  }

  if (terminal && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            playConsoleDemo();
            observer.disconnect();
          }
        });
      },
      { threshold: 0.5 }
    );
    observer.observe(terminal);
  } else if (terminal) {
    playConsoleDemo();
  }

  /* ---------------- discord handle copy ---------------- */
  const discordBtn = document.getElementById("discordCopy");
  const discordText = document.getElementById("discordText");
  if (discordBtn && discordText) {
    discordBtn.addEventListener("click", async () => {
      const original = discordText.textContent;
      try {
        await navigator.clipboard.writeText("root_atez");
        discordText.textContent = "Copied!";
      } catch (err) {
        discordText.textContent = "root_atez";
      }
      window.setTimeout(() => { discordText.textContent = original; }, 1600);
    });
  }

  /* ---------------- footer year ---------------- */
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
})();
