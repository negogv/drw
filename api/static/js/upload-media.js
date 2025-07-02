// const mediaIdInput = document.getElementById("id_media");

var form = document.querySelector("form");
var mediaInput = document.getElementById("mediaInput");

async function postAllImages(modelName, modelId) {
    mediaInput = document.getElementById("mediaInput");

    if (!mediaInput.files || mediaInput.files.length === 0) {
        return true;
    } else if (mediaInput.files.length > 1) {
        for (mediaFile of mediaInput.files) {
            let bool = await postImage(modelName, modelId, mediaFile, "/many");
            if (!bool) {
                return false;
            }
        }
        return true;
    } else {
        let b = await postImage(modelName, modelId, mediaInput.files[0]);
        return b;
    }
}

async function postImage(modelName, modelId, file = undefined, isManyArg = "") {
    let url;
    if (!modelName || !modelId) {
        url = "/post/media/reg/";
    } else {
        url = `/post/media${isManyArg}/${modelName}/${modelId}/`;
    }
    let file_name = encodeURI(file.name);
    file.new_name = file_name;

    let bool = await fetch(url, {
        method: "POST",
        body: file,
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": file.type,
            "Content-Disposition": `attachment; filename=${file.new_name}`,
        },
    })
        .then(async (response) => {
            let data = await response.json();
            data.status = response.status;
            return data;
        })
        .then(async (data) => {
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

async function uploadMediaSubmit() {
    let customFunctionSuccess;
    const modelId = document.getElementById("modelId").textContent;
    if (!modelName || !modelId) {
        customFunctionSuccess = await postAllImages(undefined, undefined);
    } else {
        customFunctionSuccess = await postAllImages(modelName, modelId);
    }

    if (customFunctionSuccess) {
        form = document.querySelector("form");

        return true;
    } else {
        displayAlert("danger", "Error occured while uploading the media files");
    }
}
submitHandlers.push(uploadMediaSubmit);

// form.addEventListener("submit", async function (event) {
//     const modelId = document.getElementById("modelId").textContent;
//     const customFunctionSuccess = await postAllImages(modelName, modelId);

//     if (customFunctionSuccess) {
//         form = document.querySelector("form");
//         console.log("upload success");

//         return true;
//     } else {
//         displayAlert("danger", "Error occured while uploading the media files");
//     }
// });
