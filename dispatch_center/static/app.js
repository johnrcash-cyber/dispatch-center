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

function setFieldIfEmpty(field, value) {
    if (!field || field.dataset.touched === "true") return;
    if (field.type === "checkbox") {
        field.checked = Boolean(value);
        return;
    }
    if ((field.value || "") === "" && value !== null && value !== undefined) {
        field.value = value;
    }
}

function applyPlatformPreset(form) {
    const select = form.querySelector("[data-platform-preset]");
    const preset = JSON.parse(form.dataset.platformPresets || "{}")[select.value] || {};
    const customField = form.querySelector("[data-custom-platform-field]");
    if (customField) customField.hidden = select.value !== "Custom";

    setFieldIfEmpty(form.elements.posting_method, preset.posting_method || "Manual");
    setFieldIfEmpty(form.elements.character_limit, preset.character_limit);
    setFieldIfEmpty(form.elements.default_hashtags, preset.default_hashtags);
    setFieldIfEmpty(form.elements.supports_markdown, preset.supports_markdown);
    setFieldIfEmpty(form.elements.supports_html, preset.supports_html);
    setFieldIfEmpty(form.elements.supports_images, preset.supports_images);

    const destination = form.elements.destination_url;
    if (destination) {
        const orgWebsite = form.dataset.organizationWebsite || "";
        const websitePreset = select.value === "Website / Blog" || select.value === "WordPress Blog";
        destination.placeholder = websitePreset && orgWebsite ? orgWebsite : (preset.destination_hint || "");
        setFieldIfEmpty(destination, websitePreset ? orgWebsite : "");
    }
}

document.addEventListener("input", (event) => {
    const form = event.target.closest("[data-platform-settings-form]");
    if (!form || event.target.matches("[data-platform-preset]")) return;
    event.target.dataset.touched = "true";
});

document.addEventListener("change", (event) => {
    const form = event.target.closest("[data-platform-settings-form]");
    if (!form) return;

    if (event.target.matches("[data-platform-preset]")) {
        applyPlatformPreset(form);
        return;
    }
    event.target.dataset.touched = "true";
});

document.querySelectorAll("[data-platform-settings-form]").forEach(applyPlatformPreset);
