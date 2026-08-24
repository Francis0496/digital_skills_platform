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

function connectDashboardDrawer() {
    const button = document.querySelector(".dashboard-menu-button");
    const sidebar = document.getElementById("dashboard-sidebar");
    const backdrop = document.getElementById("dashboard-backdrop");
    if (!button || !sidebar || !backdrop) return;

    const close = () => {
        button.setAttribute("aria-expanded", "false");
        sidebar.classList.add("hidden");
        sidebar.classList.remove("block");
        backdrop.classList.add("hidden");
    };
    button.addEventListener("click", () => {
        const opening = button.getAttribute("aria-expanded") !== "true";
        if (!opening) return close();
        button.setAttribute("aria-expanded", "true");
        sidebar.classList.remove("hidden");
        sidebar.classList.add("block");
        backdrop.classList.remove("hidden");
        sidebar.querySelector("a, button")?.focus();
    });
    backdrop.addEventListener("click", close);
    sidebar.querySelectorAll("a").forEach((link) => link.addEventListener("click", close));
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && button.getAttribute("aria-expanded") === "true") {
            close();
            button.focus();
        }
    });
}

connectDashboardDrawer();

document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
        if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
});
