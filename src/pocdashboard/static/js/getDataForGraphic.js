let btns = document.querySelectorAll(".callG");

for (b of btns) {
    b.addEventListener('click', function() {
      dataRequest(this.name)
    });
}


function dataRequest(name_button){
  const csrf  = $('input[name="csrfmiddlewaretoken"]').val()   // collect token
  // ------------------- Send data to view -------------------
  $.ajax({
      type: "POST",
      url: 'getDataForChart', // Name of the django view that will retrieve the data
      data: {
          csrfmiddlewaretoken : csrf,
          "result": name_button,       // data to send
      },
      dataType: "json",
      // ------------------- Receiving data from the view -------------------
      success: function (data) { // if send successful
        data = data
      },
      failure: function () {
          alert("failure");
      }
  })
}

