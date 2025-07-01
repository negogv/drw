const resultDiv = document.getElementById("resultDiv");
const form = document.querySelector("form");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const data = new URLSearchParams(new FormData(form));
    let instances = await fetch(form.action, {
        method: "POST",
        body: data,
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    })
        .then((response) => {
            if (!response.ok) {
                return response.json().then((err) => {
                    throw err;
                });
            }
            return response.json();
        })
        .then((data) => {
            displaySearchResult(data);
        })
        .catch((error) => {
            console.error(error);
        });
    tagsInput.value += "-";
});
