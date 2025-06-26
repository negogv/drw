const mediaIdInput = document.getElementById("id_media");

var form = document.querySelector("form");
var mediaInput = document.getElementById("mediaInput");
var mediaId;

async function postImage(modelName, modelId) {
    event.preventDefault(); // I guess it's not necessary, since i already prevented default in event listener
    mediaInput = document.getElementById("mediaInput");

    if (!mediaInput.files || mediaInput.files.length === 0) {
        return true;
    }

    let bool = await fetch(`/api/post/media/${modelName}/${modelId}/`, {
        method: "POST",
        body: mediaInput.files[0],
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": mediaInput.files[0].type,
            "Content-Disposition": `attachment; filename=${mediaInput.files[0].name}`,
        },
    })
        .then((response) => {
            data = response.json();
            data.status = response.status;
            return data;
        })
        .then((data) => {
            if (data.status && data.status != 200) {
                const alertDiv = document.getElementById("alert");
                alertDiv.className += " alert-danger";
                alertDiv.style.removeProperty("display");
                document.getElementById("alertMsg").innerText =
                    data.error + "\n" + data.message;
                window.scrollTo({ top: 0, behavior: "smooth" });
            }

            mediaIdInput.value = data.mediaId;
            return true;
        })
        .catch((error) => {
            console.error("Fetch completely failed: ", error);
            return false;
        });
    return bool;
}

form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const customFunctionSuccess = await postImage(modelName, modelId);

    if (customFunctionSuccess == true) {
        form = document.querySelector("form");

        form.submit();
    }
});
