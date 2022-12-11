const dwf = document.getElementById("dwf");
if(!dwf.disabled){
    dwf.addEventListener('mouseover', mh)
    dwf.addEventListener('mouseout', mo)

    function mh(e){
        dwf.style.animation = "pause";
        dwf.style.backgroundColor = "#277813";
        dwf.style.transform = "scale(1)";
    };

    function mo(e){
        dwf.style.backgroundColor = "#3cb371"
    }
}