/*

just saving here unused code

*/

// const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value,
//     modelName = window.location.href.match(/(?<=vacancy\/)\d+/)[0],
//     modelId = document.getElementById("modelId");

// async function postImage(event) {
//     event.preventDefault();

//     if (!mediaInput.files || mediaInput.files.length === 0) {
//         const alertDiv = document.getElementById("alert");
//         alertDiv.classname += "alert-warning";
//         alertDiv.style.removeProperty("display");
//         document.getElementById("alertMsg").innerText =
//             "Please select a file first";
//         return false;
//     }

//     var data = new FormData();
//     data.append("file", mediaInput.files[0]);
//     data.append("modelName", modelName);
//     data.append("modelId", modelId);

//     await fetch("/api/post/media/", {
//         method: "POST",
//         // body: mediaInput.files[0],
//         body: data,
//         headers: {
//             "X-CSRFToken": csrfToken,
//             // "Content-Type": mediaInput.files[0].type,
//             "Content-Type": "multipart/form-data",
//             "Content-Disposition": `attachment; filename=${mediaInput.files[0].name}`,
//         },
//     })
//         .then((response) => {
//             if (!response.ok) {
//                 const error = response.json();
//                 throw error;
//             }
//             const contentType = response.headers.get("content-type");
//             if (contentType && contentType.startsWith("image/")) {
//                 const blob = response.blob();
//                 const imageUrl = URL.createObjectURL(blob);
//                 return imageUrl;
//             } else {
//                 const data = response.json();
//                 console.log("Server response:", data);
//             }
//         })
//         .catch((error) => {
//             console.error("Error loading countries:", error);
//         });
// }

fetch("http://127.0.0.1:8000/api/post/media/", {
    body: JSON.stringify({
        modelName: "Employee",
        modelId: 15,
    }),
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": 4,
    },
}).then((response) => {
    console.log(response);
});
