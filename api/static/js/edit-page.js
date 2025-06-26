header1 = document.querySelector("h1");

if (!header1.innerText.includes("New")) {
    document.addEventListener("DOMContentLoaded", function () {
        const inputs = document.querySelectorAll("input");
        const selects = document.querySelectorAll("select");
        const textareas = document.querySelectorAll("textarea");

        inputs.forEach((input) => {
            input.dataset.originalValue = input.value;
        });
        selects.forEach((select) => {
            select.dataset.originalValue = select.value;
        });
        textareas.forEach((select) => {
            select.dataset.originalValue = select.value;
        });

        selects.forEach((select) => {
            select.addEventListener("change", updateValue);
        });
        inputs.forEach((input) => {
            input.addEventListener("locChange", updateValue);
        });
        inputs.forEach((input) => {
            input.addEventListener("input", updateValue);
        });
        textareas.forEach((textarea) => {
            textarea.addEventListener("input", updateValue);
        });
    });

    function updateValue(event) {
        const element = event.target;
        const originalValue = element.dataset.originalValue;
        const currentValue = element.value;

        if (currentValue === originalValue) {
            element.style.removeProperty("border-color");
            element.style.removeProperty("border-width");
        } else {
            element.style.borderColor = "#ebaf09";
            element.style.borderWidth = "3px";
        }
    }
} else {
}
