document.addEventListener("DOMContentLoaded", async function () {
    await fetch(`/api/endponit/`, {
        method: "GET",
        headers: {
            "X-CSRFToken": csrfToken,
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
            document.getElementById("id-of-one-some-p-tag").innerText =
                "The request was completed";
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });
    document.getElementById("id-of-one-some-p-tag").innerText =
        "The request wasn't completed";
});
document.getElementById("id-of-one-another-p-tag").innerText =
    "Some text, idk, just for example";
