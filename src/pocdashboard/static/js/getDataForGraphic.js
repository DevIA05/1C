const btns = document.querySelectorAll(".callG");
const ctx = document.getElementById('myChart');

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
      success: function (response) { // if send successful
        barChart(_data = Object.values(response), 
                 _label = Object.keys(response), 
                 title = "TOP 10 Produit")
        console.log(response)
        console.log(typeof(response))
      },
      failure: function () {
          alert("failure");
      }
  })
}


function polarAreaChart(_data, titre){
 
  const data = {
    labels: [], //key
    datasets: [{
      label: titre,
      data: [11, 16, 7, 3, 14], // value
      backgroundColor: [
        'rgb(255, 99, 132)',
        'rgb(75, 192, 192)',
        'rgb(255, 205, 86)',
        'rgb(201, 203, 207)',
        'rgb(54, 162, 235)'
      ]
    }]
  };

  const config = {
    type: 'polarArea',
    data: data,
    options: {}
  };

  new Chart(ctx, {
    config
  })

}

function barChart(_data, _label, title){

  const data = {
    labels: _label,
    datasets: [{
      label: title,
      data: _data,
      backgroundColor: [
        'rgba(255, 99, 132, 0.2)',
        'rgba(255, 159, 64, 0.2)',
        'rgba(255, 205, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(201, 203, 207, 0.2)'
      ],
      borderColor: [
        'rgb(255, 99, 132)',
        'rgb(255, 159, 64)',
        'rgb(255, 205, 86)',
        'rgb(75, 192, 192)',
        'rgb(54, 162, 235)',
        'rgb(153, 102, 255)',
        'rgb(201, 203, 207)'
      ],
      borderWidth: 1
    }]
};

  const config = {
    type: 'bar',
    data: data,
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    },
  };

  new Chart(ctx, {
    config
  })

}