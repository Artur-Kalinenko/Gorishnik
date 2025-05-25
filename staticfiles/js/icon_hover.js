document.querySelectorAll('.category-icon').forEach(icon => {
    const originalSrc = icon.getAttribute("src");
    const hoverSrc = icon.dataset.hover;

    if (hoverSrc) {
        icon.closest("a").addEventListener("mouseenter", () => {
            icon.setAttribute("src", hoverSrc);
        });
        icon.closest("a").addEventListener("mouseleave", () => {
            icon.setAttribute("src", originalSrc);
        });
    }
});