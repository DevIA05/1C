const modal = document.getElementById("container-modal");
const img2 = document.getElementById("img2");
const sf = document.getElementById("send-file")

sf.addEventListener('click', (event) => {
    img2.style.animation = "rotation 2s infinite linear";
    modal.style.display = "block"
})