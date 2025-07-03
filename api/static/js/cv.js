const downloadCVBtn = document.getElementById("downloadCVBtn"),
    cvInput = document.getElementById("cvInput"),
    modelId = document.getElementById("modelId").textContent,
    deleteCVBtn = document.getElementById("deleteCVBtn");

const formCV = document.querySelector("form");

if (downloadCVBtn) {
    downloadCVBtn.addEventListener("click", function (ev) {
        downloadCV();
    });
}
if (deleteCVBtn) {
    deleteCVBtn.addEventListener("click", function (ev) {
        deleteCV();
    });
}

async function cvSubmit() {
    if (!cvId || cvInput.files.length < 1) {
        return;
    }
    let url;
    if (modelId) {
        url = `/api/cv/${modelId}/`;
    } else {
        url = `/api/cv/`;
    }
    let fileId = await fetch(url, {
        method: "POST",
        body: cvInput.files[0],
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": cvInput.files[0].type,
            "Content-Disposition": `attachment; filename=${cvInput.files[0].name}`,
        },
    })
        .then(async (response) => {
            if (!response.ok) {
                return response.json().then((err) => {
                    throw err;
                });
            }
            let data = await response.json();
            return data;
        })
        .then(async (data) => {
            cvId.value = data.fileId;
            return data.fileId;
        })
        .catch((error) => {
            console.error(error);
        });
    console.log(cvId.value);
}
submitHandlers.push(cvSubmit);

function downloadCV() {
    window.location.assign(`/api/cv/${modelId}/`);
}

async function deleteCV() {
    await fetch(`/api/cv/${modelId}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrfToken,
        },
    })
        .then((response) => {
            if (!response.ok) {
                return response.json().then((err) => {
                    throw err;
                });
            } else {
                return true;
            }
        })
        .catch((error) => {
            console.error(error);
        });
}
