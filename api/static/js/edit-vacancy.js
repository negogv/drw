const vacancyId = window.location.href.match(/(?<=edit\/)\d+/)[0];
const mediaDiv = document.getElementById("media");

async function loadMedia() {
    const [medias, urls] = await getMediaUrlList("vacancy", vacancyId);

    if (medias && urls) {
        mediaDiv.innerHTML = "";
        urls.forEach((url, i) => {
            mediaDiv.insertAdjacentHTML(
                "beforeend",
                `<div class="image-container">
                    <img src="${url}" class="rounded-3 p-3 border border-2 m-1 hoverable-image" alt="error"
                    style="height: 200px; width: 300px;" id=${medias[i]}>
                    <div class="image-text">Delete</div>
                </div>`
            );
        });
        document.querySelectorAll("img").forEach((element) => {
            element.addEventListener("click", function (event) {
                delImage(this);
            });
        });
    }
}
async function postMediaBtn() {
    const isUploaded = await postAllImages("vacancy", vacancyId);
    if (isUploaded) {
        loadMedia();
    } else {
        displayAlert("danger", "Error occured while uploading the media files");
    }
}
function delImage(button) {
    fetch(`/post/media/many/vacancy/${vacancyId}/`, {
        method: "DELETE",
        body: JSON.stringify({
            mediaId: button.id,
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
            } else if (response.status === 204) {
                document.getElementById(button.id).remove();
                return;
            }
        })
        .catch((error) => {
            console.error(error);
        });
}

window.onload = loadMedia;
