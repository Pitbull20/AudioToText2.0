let buttonSend = document.querySelector(".button-send");
let loader = document.getElementById("loader");
let selectElement = document.querySelector(".ext-input");
let selectedValue;
selectElement.addEventListener("change", (event) => {
    selectedValue = event.target.value;
});

buttonSend.addEventListener("click", (e) => {
    let fileInput = document.querySelector(".button-input");
    let formData = new FormData();
    formData.append("myFile", fileInput.files[0]);
    formData.append("extension", selectedValue);

    loader.style.display = "block";
    fetch("/transkriber", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                alert("Сталася помилка, спробуйте ще раз");
                throw new Error("HTTP error " + response.status);
            }
            loader.style.display = "none";
            return response.text();
        })
        .then((data) => {
            loader.style.display = "none";
            // Отримання URL
            const downloadButton = document.querySelector(".button-download");

            // Формування URL-адреси для завантаження файлу
            const url = `/download/${data}`;
            console.log(url);
            // Встановлення URL-адреси для завантаження файлу
            downloadButton.setAttribute("href", url);
            downloadButton.style.pointerEvents = "all";
        })
        .catch((error) => {
            alert("Сталася помилка, спробуйте ще раз");
            loader.style.display = "none";
            console.log(error);
        });
});
