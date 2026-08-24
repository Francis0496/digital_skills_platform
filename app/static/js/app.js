"use strict";

function connectMenu(buttonSelector, menuId, openDisplayClass) {
    const button = document.querySelector(buttonSelector);
    const menu = document.getElementById(menuId);
    if (!button || !menu) return;

    button.addEventListener("click", () => {
        const isOpen = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", String(!isOpen));
        menu.classList.toggle("hidden", isOpen);
        if (openDisplayClass) menu.classList.toggle(openDisplayClass, !isOpen);
        button.setAttribute("aria-label", isOpen ? "Open navigation menu" : "Close navigation menu");
        button.querySelector(".menu-icon-open")?.classList.toggle("hidden", !isOpen);
        button.querySelector(".menu-icon-close")?.classList.toggle("hidden", isOpen);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && button.getAttribute("aria-expanded") === "true") {
            button.click();
            button.focus();
        }
    });
}

connectMenu(".mobile-menu-button", "mobile-menu");
connectMenu(".dashboard-menu-button", "dashboard-sidebar", "block");

document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
        if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
});
