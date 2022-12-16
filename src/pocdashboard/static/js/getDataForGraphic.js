const btns = document.querySelectorAll(".callG");
const ctx = document.getElementById('mainChart');
let instance_chart;

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
        // const newData = listoflist_to_dict(response["data"])
        if (instance_chart != undefined) instance_chart.destroy(); 
        switch(response["graph"]) {
          case "pr":
            barChart(_data = Object.values(response["data"]), 
                     _label = Object.keys(response["data"]), 
                     title = "TOP 10 des ventes par produit")
            break;
          case "pa":
            polarAreaChart(_data = Object.values(response["data"]), 
                           _label = Object.keys(response["data"]), 
                           title = "Vente par pays")
            break;
          case "prpa":
            polarAreaChart(_data = Object.values(response["dataPa"]), 
                           _label = Object.keys(response["dataPa"]), 
                           title = "test")
            break;
          default:
            pass
        }


        console.log(response)
        console.log(typeof(response))
      },
      failure: function () {
          alert("failure");
      }
  })
}

function barChart(_data, _label, title){

  instance_chart = new Chart(ctx, {
    type: 'bar',
    data: {
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
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

function polarAreaChart(_data,  _label, title){
 
  instance_chart = new Chart(ctx, {
    type: 'polarArea',
    data: {
      labels: _label,
      datasets: [{
        label: title,
        data: _data,
        backgroundColor: [
          'rgb(255, 99, 132)',
          'rgb(75, 192, 192)',
          'rgb(255, 205, 86)',
          'rgb(201, 203, 207)',
          'rgb(54, 162, 235)'
        ]
      }]
    },
    options: {}
  })

}

function getTop(ll, x){}
function getFlop(ll, x){}

function listoflist_to_dict(ll){
  return(ll.map(x => {
    let res = {}
    res[x[0]] = x[1]
    return(res);
  }))
}