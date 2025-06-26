const modelName = window.location.href.match(/(?<=api\/)\w+(?=\/)/)[0],
    // modelId = document.getElementById("modelId").innerText,
    imgEl = document.getElementById("profilePic");

async function getMediaUrl(mediaId) {
    let imageUrl = await fetch(`/api/media/${mediaId}/`, {
        method: "GET",
        headers: {
            "X-CSRFToken": csrfToken,
        },
    })
        .then((response) => {
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.startsWith("image/")) {
                var blob = response.blob();
                return blob;
            }
        })
        .then((blob) => {
            var imageUrl = window.URL.createObjectURL(blob);
            return imageUrl;
        });
    console.log(imageUrl);
    return imageUrl;
}

async function getMediaArray(modelName, modelId) {
    var mediaArray = await fetch("/api/get/media-array/from-instance/", {
        method: "POST",
        body: JSON.stringify({
            modelName: modelName,
            modelId: modelId,
        }),
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
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
            return data;
        })
        .catch((error) => {
            console.error(error);
        });

    return mediaArray;
}

async function getMediaUrlList(modelName, modelId) {
    var mediaArray = await getMediaArray(modelName, modelId);
    if (mediaArray.length == 0) {
        return [false, false];
    }
    var urls = [];

    for (id of mediaArray) {
        let url = await getMediaUrl(id);
        urls.push(url);
    }
    console.log(mediaArray, urls);

    return [mediaArray, urls];
}
