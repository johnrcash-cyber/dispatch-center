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
