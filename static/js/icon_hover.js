document.querySelectorAll('img[data-hover]').forEach(icon => {
    const originalSrc = icon.getAttribute("src");
    const hoverSrc = icon.dataset.hover;

    const container = icon.closest("a, button");

    if (hoverSrc && container) {
        container.addEventListener("mouseenter", () => {
            icon.setAttribute("src", hoverSrc);
        });
        container.addEventListener("mouseleave", () => {
            icon.setAttribute("src", originalSrc);
        });
    }
});
