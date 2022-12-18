const btns = document.querySelectorAll(".callG");
const ctx = document.getElementById('mainChart');
const cty = document.getElementById('detailChart');
let instance_main_chart;
let instance_detail_chart;
let claim = ""
let value_from_click = ""
let _labels;

for (b of btns) {
    b.addEventListener('click', function() {
      dataRequest({"claim": this.name})
    });
}


function dataRequest(_claim){
  const csrf  = $('input[name="csrfmiddlewaretoken"]').val()   // collect token
  // ------------------- Send data to view -------------------
  $.ajax({
      type: "POST",
      url: 'getDataForChart', // Name of the django view that will retrieve the data
      data: {
          csrfmiddlewaretoken : csrf,
          "result": _claim,       // data to send
      },
      dataType: "json",
      // ------------------- Receiving data from the view -------------------
      success: function (response) { // if send successful 
        switch(response["graph"]) {

          case "pr":
            destroyChart(instance_main_chart, instance_detail_chart)
            barChart(_data = Object.values(response["data"]), 
                     _label = Object.keys(response["data"]), 
                     title = "TOP 10 des ventes par produit",
                     graph = ctx)
            break;

          case "pa":
            destroyChart(instance_main_chart, instance_detail_chart)
            polarAreaChart(_data = Object.values(response["data"]), 
                           _label = Object.keys(response["data"]), 
                           title = "TOP 10 des ventes par pays",
                           graph = ctx)
            break;

          case "prpa":
            if (instance_detail_chart != undefined){ instance_detail_chart.destroy() }
            polarAreaChart(_data = Object.values(response["data"]),
                           _label = Object.keys(response["data"]), 
                           title = "Quantité du produit vendu dans les pays",
                           graph = cty)
            break;

          case "papr":
            if (instance_detail_chart != undefined){ instance_detail_chart.destroy() }
            barChart(_data = Object.values(response["data"]),
                     _label = Object.keys(response["data"]), 
                     title = "Quantité des produits vendu dans le pays",
                     graph = cty)
            break;

          default:
            pass
        }
      },
      failure: function () {
          alert("failure");
      }
  })
}

function clickHandler(click){
  const points = instance_main_chart.getElementsAtEventForMode(click, 'nearest', {intersect: true}, true);
  if(points.length){
    const firstPoint = points[0];
    const value = _labels[firstPoint.index] //instance_main_chart.data.labels[firstPoint.index];
    dataRequest({"data": value, "claim": claim})
  }
}

function barChart(_data, _label, title, graph){

  config_bar_chart = {
    type: "bar",
    data: {
        labels: _label.map(x => {return x.split(" ");}),
        datasets: [
            {
                label: title,
                data: _data,
                backgroundColor: [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(255, 159, 64, 0.2)",
                    "rgba(255, 205, 86, 0.2)",
                    "rgba(75, 192, 192, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(153, 102, 255, 0.2)",
                    "rgba(201, 203, 207, 0.2)",
                ],
                borderColor: [
                    "rgb(255, 99, 132)",
                    "rgb(255, 159, 64)",
                    "rgb(255, 205, 86)",
                    "rgb(75, 192, 192)",
                    "rgb(54, 162, 235)",
                    "rgb(153, 102, 255)",
                    "rgb(201, 203, 207)",
                ],
                borderWidth: 1,
            }
        ],
    },
    options: {
      scales: {
        y: {beginAtZero: true},
        x: { 
          ticks: {
            stepSize: 1,
            autoSkip: false,
            font: { size: 9, }
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            title: (context) => {
              // console.log(context[0].label);
              return context[0].label.replaceAll(",", " ")
            }
          }
        }
      }
    },
}

  if(graph.id == "mainChart"){
    instance_main_chart = new Chart(graph, config_bar_chart);
    claim = "prpa"
    _labels = _label
    graph.onclick = clickHandler;
  } else{ instance_detail_chart = new Chart(graph, config_bar_chart); }

}

function polarAreaChart(_data,  _label, title, graph){
 
  config_polar_chart = {
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
    options: {
      scale: {
        ticks: { z: 1 }
      }
    }  
  }

  if(graph.id == "mainChart"){
    instance_main_chart = new Chart(graph, config_polar_chart);
    claim = "papr"
    graph.onclick = clickHandler;
  } else{ instance_detail_chart = new Chart(graph, config_polar_chart); }

}

function destroyChart(mc, dc){
  if (mc != undefined){ mc.destroy() }
  if (dc != undefined){ dc.destroy() }
}

