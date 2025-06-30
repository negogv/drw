const mediaIdInput = document.getElementById("id_media");

var form = document.querySelector("form");
var mediaInput = document.getElementById("mediaInput");

async function postAllImages(modelName, modelId) {
    event.preventDefault();
    mediaInput = document.getElementById("mediaInput");

    // let postTracking = [];
    if (!mediaInput.files || mediaInput.files.length === 0) {
        return true;
    } else if (mediaInput.files.length > 1) {
        for (mediaFile of mediaInput.files) {
            let bool = await postImage(modelName, modelId, mediaFile, "/many");
            console.log(bool);
            if (!bool) {
                return false;
            }
            // postTracking.push(bool);
        }
        return true;
    } else {
        let b = await postImage(modelName, modelId, mediaInput.files[0]);
        return b;
    }
}

async function postImage(modelName, modelId, file = undefined, isManyArg = "") {
    let bool = await fetch(
        `/api/post/media${isManyArg}/${modelName}/${modelId}/`,
        {
            method: "POST",
            body: file,
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": file.type,
                "Content-Disposition": `attachment; filename=${file.name}`,
            },
        }
    )
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
    const modelId = document.getElementById("modelId").textContent;
    const customFunctionSuccess = await postAllImages(modelName, modelId);

    if (customFunctionSuccess) {
        form = document.querySelector("form");

        form.submit();
    } else {
        displayAlert("danger", "Error occured while uploading the media files");
    }
});
