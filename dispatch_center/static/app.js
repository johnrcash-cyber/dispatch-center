document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy]");
    if (!button) return;

    const value = button.dataset.copy || "";
    await navigator.clipboard.writeText(value);
    const original = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => {
        button.textContent = original;
    }, 1000);
});

document.addEventListener("change", (event) => {
    const select = event.target.closest("[data-organization-switcher]");
    if (!select || !select.value) return;

    const form = select.closest("[data-switcher-form]");
    form.action = select.value;
    form.submit();
});

function applyAssetBrowserFilters(browser) {
    const search = (browser.querySelector("[data-asset-search]")?.value || "").toLowerCase();
    const type = browser.querySelector("[data-asset-type-filter]")?.value || "all";
    const approval = browser.querySelector("[data-asset-approval-filter]")?.value || "approved";
    const cards = [...browser.querySelectorAll("[data-asset-card]")];
    let visibleCount = 0;

    for (const card of cards) {
        const titleMatch = card.dataset.title.includes(search);
        const typeMatch = type === "all" || card.dataset.type === type;
        const approvalMatch = approval === "all" || card.dataset.approved === approval;
        const visible = titleMatch && typeMatch && approvalMatch;
        card.hidden = !visible;
        if (visible) visibleCount += 1;
    }

    const empty = browser.querySelector("[data-asset-empty]");
    if (empty) empty.hidden = visibleCount !== 0;
}

document.addEventListener("input", (event) => {
    const browser = event.target.closest("[data-asset-browser]");
    if (!browser || !event.target.matches("[data-asset-search]")) return;
    applyAssetBrowserFilters(browser);
});

document.addEventListener("change", (event) => {
    const browser = event.target.closest("[data-asset-browser]");
    if (!browser || !event.target.matches("[data-asset-type-filter], [data-asset-approval-filter]")) return;
    applyAssetBrowserFilters(browser);
});

document.querySelectorAll("[data-asset-browser]").forEach(applyAssetBrowserFilters);
