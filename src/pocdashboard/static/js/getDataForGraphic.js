let btns = document.querySelectorAll('callG');

for (i of btns) {
    i.addEventListener('click', function() {
      console.log(this);
    });
}


console.log("-------------------------------")

