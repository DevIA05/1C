const btns = document.querySelectorAll(".callG");
const ph   = document.querySelectorAll(".bOpt");
const ctx  = document.getElementById('mainChart');
const cty  = document.getElementById('detailChart');
const cty2  = document.getElementById('detailChart2');

let instance_main_chart   = [];
let instance_detail_chart = [];
let choice = {}

let nameB = ""
// let _labels;
// let all_data = [];
// let all_detail_data = [];
// let title = ""

// ================================= EVENT =================================

/** Adds the function to request the data from the server. */
for (b of btns) {
    b.addEventListener('click', function() {
      destroyCharts(instance_main_chart); destroyCharts(instance_detail_chart)
      choice = document.querySelector('input[name="choice"]:checked').value;
      limit  = document.getElementById("ph").value;
      nameB = this.name
      dataRequest({"claim": this.name, "choice": choice, "limit": limit})
    });
}

// =========================================================================
// ====================== Communication with server ========================
// =========================================================================

/** Ask the server for the data corresponding to the code and and process requests
 * 
 * @param {dict} d: 
 */
function dataRequest(d){
  const csrf  = $('input[name="csrfmiddlewaretoken"]').val()   // collect token
  // ------------------- Send data to view -------------------
  $.ajax({
      type: "POST",
      url: 'getDataForChart', // Name of the django view that will retrieve the data
      data: {
          csrfmiddlewaretoken : csrf,
          "result": d,       // data to send
      },
      dataType: "json",
      // ------------------- Receiving data from the view -------------------
      success: function (response) { // if send successful 
        switch(response["claim"]) {

          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // ~~~~~~~~~~~~~~~~~~~~~ Graphe principal ~~~~~~~~~~~~~~~~~~~~~
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

          case "pr":
            instance_main_chart.push(
              createGraph(
                barChart(_data  = Object.values(response["data"]),
                         _label = Object.keys(response["data"]).map(x => {return x.split(" ");}),
                         title  = "Qauntité vendu par produit"),
                divGraph = ctx))
            break;

          case "pa":
            instance_main_chart.push(
              createGraph(
                polarAreaChart(_data  = Object.values(response["data"]),
                               _label = Object.keys(response["data"]), 
                               title  = "Qauntité vendu par pays"),
                divGraph = ctx))
            break;

          case "_date":
            instance_main_chart.push(
              createGraph(
                barChart(_data  = Object.values(response["data"]),
                         _label = Object.keys(response["data"]), 
                         title  = "Quantité des produits vendu par mois",
                         xsize  = 12),
                divGraph = ctx))
            break;

          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // ~~~~~~~~~~~~~~~~~~~~~ Graphe de detail ~~~~~~~~~~~~~~~~~~~~~
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

          case "prpa":
            instance_detail_chart.push(
              createGraph(
                polarAreaChart(_data  = Object.values(response["data"]),
                               _label = Object.keys(response["data"]),
                               title  = "Quantité du produit vendu dans les pays"),
                divGraph = cty))
            break;

          case "papr":
            instance_detail_chart.push(
              createGraph(
                barChart(_data  = Object.values(response["data"]),
                         _label = Object.keys(response["data"]).map(x => {return x.split(" ");}), 
                         title  = "Quantité des produits vendus dans le pays"),
                divGraph = cty))
            break;

          case "dprpa":
            instance_detail_chart.push(
              createGraph(
                barChart(_data  = Object.values(response["data"][0]),
                         _label = Object.keys(response["data"][0]).map(x => {return x.split(" ");}),
                         title  = "Quantité d'un produit vendus dans le mois"),
                divGraph  = cty))
            instance_detail_chart.push(
              createGraph(
                polarAreaChart(_data  = Object.values(response["data"][1]),
                               _label = Object.keys(response["data"][1]),
                               title  = "Quantité vendus dans le mois dans un pays"),
                divGraph  = cty2))
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

// ================================= GRAPH =================================

function barChart(_data, _label, title, xsize = 9){

  config_bar_chart = {
    type: "bar",
    data: {
        labels: _label,
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
            font: { size: xsize, }
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

  return config_bar_chart

}

function polarAreaChart(_data,  _label, title){
 
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

  return config_polar_chart

}

function clickHandler(click){
  destroyCharts(instance_detail_chart)
  const points = instance_main_chart[0].getElementsAtEventForMode(click, 'nearest', {intersect: true}, true);
  if(points.length){
    const firstPoint = points[0];
    //const value =  instance_main_chart.data.labels[firstPoint.index]//.replaceAll(",", " "); //_labels[firstPoint.index]
    const lab = instance_main_chart[0].data.labels[firstPoint.index]
    const value = Array.isArray(lab) ? lab.join(" ") : lab
    dataRequest({"data": value, 
                 "claim": switchDetailGraph(),
                 "choice": document.querySelector('input[name="choice"]:checked').value,
                 "limit": document.getElementById("ph").value})
  }
}

// function destroyChart(mc, dc){
//   if (mc != undefined){ mc.destroy() }
//   if (dc != undefined){ dc.destroy() }
// }

function switchDetailGraph(){
  claim = ""
  switch (nameB) {
    case 'pr':
      claim = "prpa"
      break;
    case 'pa':
      claim = "papr"
      break;
    case '_date':
      claim = "dprpa"
      break;
    default:
      console.log("Err: switchDetailGraph");
  }
  return claim
  
}

function destroyCharts(instance){
  if(instance.length > 0){
    instance.map(i => i.destroy())
    instance.length = 0
  }
}

function createGraph(config_chart, divGraph){
  const instance_chart = new Chart(divGraph, config_chart);
  if(divGraph.id == "mainChart"){ divGraph.onclick = clickHandler; } 
  return instance_chart
}