"use strict";
const motionStyle = getComputedStyle(document.documentElement);
const easeOut = motionStyle.getPropertyValue("--ease-out").trim();
const motionDuration = (name) =>
  parseFloat(motionStyle.getPropertyValue("--motion-" + name));
const reduce = matchMedia("(prefers-reduced-motion: reduce)");
document.documentElement.classList.add("motion-ready");
const menuButton = document.querySelector(".menu-toggle");
const menu = document.querySelector("#mobile-nav");
let pointerAction = false;
document.addEventListener(
  "pointerdown",
  () => {
    pointerAction = true;
  },
  true,
);
document.addEventListener(
  "keydown",
  () => {
    pointerAction = false;
  },
  true,
);
const running = new Set();
const seen = new WeakSet();
let sceneObserver;
function animateElement(el, frames, options = {}) {
  if (!el || reduce.matches || !el.animate) return null;
  const a = el.animate(frames, {
    duration: motionDuration("hero"),
    easing: easeOut,
    fill: "backwards",
    ...options,
  });
  running.add(a);
  a.finished
    .catch(() => {})
    .finally(() => {
      running.delete(a);
      if (options.fill !== "forwards") a.cancel();
    });
  return a;
}
function finishWithin(root) {
  if (!root) return;
  seen.add(root);
  root.querySelectorAll("[data-motion-scene]").forEach((el) => {
    seen.add(el);
    sceneObserver?.unobserve(el);
  });
  running.forEach((a) => {
    if (root.contains(a.effect.target)) a.cancel();
  });
}
// CSS transitions retain their current visual value when the target reverses.
let menuTimer;
function setMenu(open, animate = false) {
  clearTimeout(menuTimer);
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.textContent = open ? "Закрыть" : "Меню";
  menu.inert = !open;
  const instant = !animate || reduce.matches;
  menu.classList.toggle("motion-instant", instant);
  if (open) {
    if (menu.hidden) {
      menu.classList.add("motion-closed");
      menu.hidden = false;
      void menu.offsetWidth;
    }
    menu.classList.remove("motion-closed");
  } else if (instant) {
    menu.hidden = true;
    menu.classList.remove("motion-closed");
  } else {
    menu.classList.add("motion-closed");
    menuTimer = setTimeout(() => {
      menu.hidden = true;
    }, motionDuration("exit"));
  }
}
menuButton.addEventListener("click", (e) =>
  setMenu(menuButton.getAttribute("aria-expanded") !== "true", e.detail !== 0),
);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !menu.hidden) {
    setMenu(false);
    menuButton.focus();
  }
});
matchMedia("(min-width:1200px)").addEventListener("change", (e) => {
  if (e.matches) setMenu(false);
});
function appear(el, duration = motionDuration("reveal")) {
  if (!el || !pointerAction) return;
  const opacity = el.getAnimations().length
    ? getComputedStyle(el).opacity
    : 0.45;
  el.getAnimations().forEach((a) => a.cancel());
  animateElement(el, [{ opacity }, { opacity: 1 }], { duration });
}
// Native details retain their semantics; only pointer toggles interpolate size.
document.querySelectorAll("details:not(.service-card)").forEach((details) => {
  details.querySelector(":scope > summary")?.addEventListener("click", (event) => {
    details.toggleAttribute("data-accordion-instant", event.detail === 0 || reduce.matches);
    // Establish the collapsed style before the native default toggle.
    void details.offsetHeight;
  });
});
// Progressive enhancement: native details remain usable without JavaScript.
const serviceDialog = document.createElement("dialog");
serviceDialog.className = "service-dialog";
serviceDialog.setAttribute("aria-labelledby", "service-dialog-title");
serviceDialog.innerHTML =
  '<div class="dialog-header"><div><p class="dialog-eyebrow">КингМоторс / Услуги</p><h2 id="service-dialog-title"></h2></div><button type="button" class="dialog-close" aria-label="Закрыть услуги">×</button></div><div class="dialog-body"></div>';
document.body.append(serviceDialog);
let activeGroup = null,
  returnFocus = null,
  returnHash = "#services",
  returnScroll = 0;
const dialogBody = serviceDialog.querySelector(".dialog-body");
const dialogTitle = serviceDialog.querySelector("#service-dialog-title");
const dialogClose = serviceDialog.querySelector(".dialog-close");
document.querySelectorAll(".service-card").forEach((old) => {
  const group = document.createElement("article");
  group.className = old.className;
  group.id = old.id;
  group.append(...old.childNodes);
  old.replaceWith(group);
  const summary = group.querySelector(":scope > summary");
  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = "service-trigger";
  trigger.innerHTML = summary.innerHTML;
  trigger.setAttribute("aria-haspopup", "dialog");
  trigger.setAttribute("aria-controls", "service-dialog");
  summary.replaceWith(trigger);
  group.classList.add("modal-card");
  trigger.addEventListener("click", (e) => {
    const hash = "#" + group.id;
    if (location.hash !== hash) history.pushState(null, "", hash);
    openService(group, null, trigger, e.detail !== 0);
  });
});
serviceDialog.id = "service-dialog";
let dialogTimer;
function closeService({ restoreFocus = true, restoreLocation = true, animate = false } = {}) {
  clearTimeout(dialogTimer);
  if (!serviceDialog.open) return;
  if (animate && !reduce.matches) {
    serviceDialog.classList.remove("motion-instant");
    serviceDialog.classList.add("motion-closed");
    dialogTimer = setTimeout(
      () => closeService({ restoreFocus, restoreLocation }),
      motionDuration("dialog-exit"),
    );
    return;
  }
  serviceDialog.classList.add("motion-instant");
  serviceDialog.classList.remove("motion-closed");
  serviceDialog.getAnimations().forEach((a) => a.cancel());
  serviceDialog.close();
  document.documentElement.classList.remove("service-modal-open");
  if (activeGroup) {
    activeGroup.append(serviceDialog.querySelector(".service-content"));
    activeGroup = null;
  }
  if (
    restoreLocation &&
    (location.hash.startsWith("#service-") ||
    location.hash.startsWith("#detail-"))
  )
    history.replaceState(
      null,
      "",
      location.pathname + location.search + returnHash,
    );
  window.scrollTo({ top: returnScroll, behavior: "instant" });
  if (restoreFocus && returnFocus?.isConnected)
    returnFocus.focus({ preventScroll: true });
}
function openService(group, job = null, trigger = null, animate = false) {
  clearTimeout(dialogTimer);
  serviceDialog.classList.toggle("motion-instant", !animate || reduce.matches);
  if (activeGroup !== group) {
    if (activeGroup)
      activeGroup.append(serviceDialog.querySelector(".service-content"));
    if (!serviceDialog.open) {
      returnScroll = scrollY;
    }
    returnFocus = trigger || group.querySelector(".service-trigger");
    activeGroup = group;
    dialogTitle.textContent =
      group.querySelector("h3").textContent;
    dialogBody.append(group.querySelector(".service-content"));
    dialogBody.scrollTop = 0;
  }
  if (!serviceDialog.open) {
    serviceDialog.classList.add("motion-closed");
    serviceDialog.showModal();
    document.documentElement.classList.add("service-modal-open");
    dialogClose.focus();
    void serviceDialog.offsetWidth;
  }
  serviceDialog.classList.remove("motion-closed");
  if (job) {
    job.setAttribute("data-accordion-instant", "");
    job.open = true;
    requestAnimationFrame(() => {
      job.scrollIntoView({ block: "nearest" });
      job.querySelector("summary").focus({ preventScroll: true });
    });
  }
}
serviceDialog.addEventListener("keydown", (e) => {
  if (e.key !== "Tab") return;
  const nodes = [
    ...serviceDialog.querySelectorAll(
      'button,a[href],summary,input,textarea,select,[tabindex="0"]',
    ),
  ].filter((el) => !el.disabled && el.getClientRects().length);
  const first = nodes[0],
    last = nodes.at(-1);
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault();
    last.focus();
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault();
    first.focus();
  }
});
dialogClose.addEventListener("click", (e) => closeService({ animate: e.detail !== 0 }));
serviceDialog.addEventListener("cancel", (e) => {
  e.preventDefault();
  closeService();
});
let backdropDown = false;
function outsideDialog(e) {
  const r = serviceDialog.getBoundingClientRect();
  return (
    e.clientX < r.left ||
    e.clientX > r.right ||
    e.clientY < r.top ||
    e.clientY > r.bottom
  );
}
serviceDialog.addEventListener("pointerdown", (e) => {
  backdropDown = outsideDialog(e);
});
serviceDialog.addEventListener("click", (e) => {
  if (backdropDown && outsideDialog(e)) closeService({ animate: e.detail !== 0 });
  backdropDown = false;
});
let scrollTarget = null;
function cancelSectionScroll() {
  if (!scrollTarget) return;
  scrollTarget = null;
  window.scrollTo({ top: scrollY, left: scrollX, behavior: "instant" });
}
window.addEventListener("scrollend", () => { scrollTarget = null; });
window.addEventListener("wheel", cancelSectionScroll, { passive: true });
window.addEventListener("touchstart", cancelSectionScroll, { passive: true });
document.addEventListener("keydown", cancelSectionScroll);
function revealHash({ smooth = false } = {}) {
  cancelSectionScroll();
  let id;
  try {
    id = decodeURIComponent(location.hash.slice(1));
  } catch {
    return;
  }
  const target = id && document.getElementById(id);
  if (!target) {
    if (!id) returnHash = "#services";
    closeService({ restoreFocus: false, restoreLocation: false });
    return;
  }
  finishWithin(target);
  const group = target.matches(".service-card")
    ? target
    : target.closest(".service-card") ||
      (target.closest(".service-dialog") ? activeGroup : null);
  if (group) {
    openService(group, target.matches(".job") ? target : null);
    return;
  }
  // URL navigation already selected its history entry; closing must not rewrite it.
  closeService({ restoreFocus: false, restoreLocation: false });
  returnHash = location.hash;
  let el = target;
  while (el) {
    if (el.tagName === "DETAILS") {
      el.setAttribute("data-accordion-instant", "");
      el.open = true;
    }
    el = el.parentElement;
  }
  requestAnimationFrame(() => {
    if (!target.matches("input,button,a,summary")) target.tabIndex = -1;
    target.focus({ preventScroll: true });
    scrollTarget = smooth && !reduce.matches ? target : null;
    target.scrollIntoView({ block: "start", behavior: scrollTarget ? "smooth" : "instant" });
  });
}
// Prevent the browser's initial hash jump. pushState keeps Back/Forward native.
document.addEventListener("click", (event) => {
  const link = event.target.closest('a[href^="#"]');
  if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey ||
      event.ctrlKey || event.shiftKey || event.altKey || link.hasAttribute("download") ||
      link.target && link.target !== "_self") return;
  let target;
  try { target = document.getElementById(decodeURIComponent(link.hash.slice(1))); }
  catch { return; }
  if (!target) return;
  event.preventDefault();
  closeService({ restoreFocus: false, restoreLocation: false });
  setMenu(false);
  stopIntro();
  if (location.hash !== link.hash) history.pushState(null, "", link.hash);
  revealHash({ smooth: event.detail !== 0 });
});
window.addEventListener("hashchange", revealHash);
revealHash();
const form = document.querySelector("#booking-form"),
  phone = form.querySelector("#phone"),
  consent = form.querySelector("#consent"),
  message = form.querySelector(".form-message"),
  submit = form.querySelector("[type=submit]");
submit.disabled = false;
let formTimer;
function state(mode) {
  clearTimeout(formTimer);
  form.removeAttribute("aria-busy");
  submit.disabled = false;
  message.hidden = mode === "idle";
  message.dataset.state = mode;
  const texts = {
    sending: "Демонстрация: отправка заявки…",
    success:
      "Демонстрация успешного ответа. В рабочем сайте здесь появится подтверждение получения заявки. Сейчас ничего не отправлено.",
    error:
      "Демонстрация ошибки: связь с сервером прервана. Поля сохранены. Повторите попытку или позвоните в сервис.",
    checked:
      "Поля заполнены корректно. Это прототип: заявка не отправлена. Для записи позвоните 8 906 366 49 11.",
  };
  message.textContent = texts[mode] || "";
  if (mode === "sending") {
    form.setAttribute("aria-busy", "true");
    submit.disabled = true;
    formTimer = setTimeout(() => state("checked"), 800);
  }
  if (mode === "error") {
    const retry = document.createElement("button");
    retry.type = "button";
    retry.textContent = "Повторить демонстрацию";
    retry.className = "text-link retry";
    retry.addEventListener("click", () => state("sending"));
    message.append(document.createElement("br"), retry);
  }
  appear(message, motionDuration("status"));
}
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const valid = /^[78]\d{10}$/.test(phone.value.replace(/\D/g, ""));
  phone.setAttribute("aria-invalid", String(!valid));
  document.querySelector("#phone-error").hidden = valid;
  document.querySelector("#consent-error").hidden = consent.checked;
  consent.setAttribute("aria-invalid", String(!consent.checked));
  if (!valid) {
    phone.focus();
    return;
  }
  if (!consent.checked) {
    consent.focus();
    return;
  }
  state("checked");
});
document
  .querySelectorAll("[data-demo]")
  .forEach((b) => b.addEventListener("click", () => state(b.dataset.demo)));
document.querySelectorAll("[data-service]").forEach((a) =>
  a.addEventListener("click", () => {
    const ctx = form.querySelector(".form-context");
    ctx.hidden = false;
    ctx.querySelector("span").textContent = "Услуга: " + a.dataset.service;
  }),
);
document.querySelector("#clear-service").addEventListener("click", () => {
  form.querySelector(".form-context").hidden = true;
  phone.focus();
});
// One-shot marketing scenes. Unobserved content is never pre-hidden.
const easeInOut = motionStyle.getPropertyValue("--ease-in-out").trim();
const value = (name) =>
  motionStyle.getPropertyValue("--motion-" + name).trim();
function rise(el, delay = 0) {
  return animateElement(
    el,
    [
      { opacity: 0.25, transform: `translateY(${value("distance")})` },
      { opacity: 1, transform: "translateY(0)" },
    ],
    { delay },
  );
}
function revealPhoto(el, delay = 0) {
  return animateElement(
    el,
    [{ clipPath: "inset(0 0 100% 0)" }, { clipPath: "inset(0 0 0% 0)" }],
    { duration: motionDuration("scene"), easing: easeInOut, delay },
  );
}
const sceneTargets = [
  ...document.querySelectorAll(
    ".service-media,.about-image,.service-steps li,.featured-quote,.review-stack>.review-item",
  ),
];
sceneTargets.forEach((el) => (el.dataset.motionScene = ""));
if ("IntersectionObserver" in window) {
  sceneObserver = new IntersectionObserver(
    (entries) => {
      const batch = entries
        .filter((e) => e.isIntersecting)
        .sort(
          (a, b) =>
            sceneTargets.indexOf(a.target) - sceneTargets.indexOf(b.target),
        );
      const counts = {};
      batch.forEach(({ target: el }) => {
        sceneObserver.unobserve(el);
        if (seen.has(el)) return;
        seen.add(el);
        if (
          reduce.matches ||
          el.contains(document.activeElement) ||
          (document.activeElement.matches("section:focus") &&
            document.activeElement.contains(el))
        )
          return;
        const type = el.matches(".service-media")
          ? "catalog"
          : el.matches(".service-steps li")
            ? "steps"
            : el.matches(".about-image")
              ? "photo"
              : "reviews";
        const index = counts[type] || 0;
        counts[type] = index + 1;
        const delay =
          index * motionDuration(type === "steps" ? "step-stagger" : "stagger");
        if (type === "catalog") revealPhoto(el, delay);
        else if (type === "photo") revealPhoto(el.querySelector("img"));
        else {
          rise(el, delay);
          if (type === "steps")
            animateElement(
              el.querySelector(".step-line"),
              [{ transform: "scaleY(0)" }, { transform: "scaleY(1)" }],
              { duration: motionDuration("hero"), delay, easing: easeInOut },
            );
        }
      });
    },
    { threshold: 0, rootMargin: "0px 0px -32px 0px" },
  );
  sceneTargets.forEach((el) => sceneObserver.observe(el));
}
// Brand and hero share one 820ms scene; CTA and phone never participate.
const intro = document.querySelector(".brand-intro");
let introAnimations = [];
let introTimer;
function stopIntro() {
  clearTimeout(introTimer);
  introAnimations.forEach((a) => a?.cancel());
  introAnimations = [];
  intro.hidden = true;
}
function playIntro() {
  stopIntro();
  if (reduce.matches || !intro.animate) return;
  intro.hidden = false;
  const add = (el, frames, options) =>
    introAnimations.push(animateElement(el, frames, options));
  add(
    intro.querySelector(".intro-mark"),
    [
      { transform: `translateX(-${value("mark-distance")})`, opacity: 0 },
      { transform: "translateX(0)", opacity: 1 },
    ],
    { duration: motionDuration("mark") },
  );
  add(
    intro.querySelector(".intro-name"),
    [
      { clipPath: "inset(0 100% 0 0)", opacity: 0.3 },
      { clipPath: "inset(0 0% 0 0)", opacity: 1 },
    ],
    { delay: motionDuration("name-delay"), duration: motionDuration("name") },
  );
  add(intro, [{ opacity: 1 }, { opacity: 0 }], {
    delay: motionDuration("intro-fade"),
    duration: motionDuration("exit"),
    easing: "linear",
    fill: "forwards",
  });
  add(
    document.querySelector(".hero-photo"),
    [
      { transform: `scale(${value("photo-scale")})` },
      { transform: "scale(1)" },
    ],
    { duration: motionDuration("intro") },
  );
  document
    .querySelectorAll(".hero-title-part")
    .forEach((el, i) =>
      introAnimations.push(rise(el, i * motionDuration("stagger"))),
    );
  introAnimations.push(
    rise(document.querySelector(".hero-lead"), motionDuration("name-delay")),
  );
  add(
    document.querySelector(".hero-rule"),
    [{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }],
    { duration: motionDuration("scene"), easing: easeInOut },
  );
  introTimer = setTimeout(stopIntro, motionDuration("intro"));
}
try {
  if (!location.hash && !sessionStorage.getItem("km-intro-v2")) {
    sessionStorage.setItem("km-intro-v2", "1");
    playIntro();
  }
} catch {
  /* Storage denial skips intro. */
}
document.addEventListener("focusin", (e) => {
  const section = e.target.closest("section");
  if (section) finishWithin(section);
  if (section?.id === "top") stopIntro();
});
// Hash targets and keyboard navigation bypass decorative delays.
window.addEventListener("hashchange", () => {
  stopIntro();
  pointerAction = false;
});
reduce.addEventListener("change", () => {
  if (!reduce.matches) return;
  stopIntro();
  if (scrollTarget) {
    const target = scrollTarget;
    cancelSectionScroll();
    target.scrollIntoView({ block: "start", behavior: "instant" });
  }
  document.querySelectorAll("details").forEach(el => el.setAttribute("data-accordion-instant", ""));
  running.forEach((a) => a.cancel());
  setMenu(menuButton.getAttribute("aria-expanded") === "true");
  if (serviceDialog.classList.contains("motion-closed")) closeService();
  else {
    serviceDialog.classList.add("motion-instant");
    serviceDialog.getAnimations({ subtree: true }).forEach((a) => a.cancel());
  }
});
window.addEventListener("pagehide", () => {
  cancelSectionScroll();
  stopIntro();
  clearTimeout(formTimer);
  clearTimeout(menuTimer);
  clearTimeout(dialogTimer);
  running.forEach((a) => a.cancel());
  sceneObserver?.disconnect();
  setMenu(false);
  closeService({ restoreFocus: false, restoreLocation: false });
  document.getAnimations().forEach((a) => a.cancel());
});
window.addEventListener("pageshow", (e) => {
  if (e.persisted) {
    revealHash();
    sceneTargets.forEach((el) => {
      if (!seen.has(el)) sceneObserver?.observe(el);
    });
  }
});
