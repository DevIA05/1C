const btns = document.querySelectorAll(".callG");     
const ph   = document.querySelectorAll(".bOpt");
const ctx  = document.getElementById('mainChart');     
const cty  = document.getElementById('detailChart');
const cty2  = document.getElementById('detailChart2');

let instance_main_chart   = []; 
let instance_detail_chart = [];
let choice = {}

let nameB = ""

// ================================= EVENT =================================

/** Adds the function to request the data from the server. */
for (b of btns) {
    b.addEventListener('click', function() {
      destroyCharts(instance_main_chart); destroyCharts(instance_detail_chart)
      choice = document.querySelector('input[name="choice"]:checked').value;   // ascending or descending
      limit  = document.getElementById("ph").value;                            // how much value we want to have
      nameB = this.name
      dataRequest({"claim": this.name, "choice": choice, "limit": limit})      // data request
    });
}

// =========================================================================
// ====================== Communication with server ========================
// =========================================================================

/** Ask the server for the data corresponding to the code and and process requests
 * 
 * @param {dict} d: contains the data request, if you want to sort in ascending or descending order and how much value we want to have
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
                         _label = Object.keys(response["data"]).map(x => {return x.split(" ");}), // cuts the description at each space so that each member 
                                                                                                  // composing the label is on one line when the graph is displayed
                         title  = "Vente par produit"),
                divGraph = ctx))
            break;

          case "pa":
            instance_main_chart.push(
              createGraph(
                polarAreaChart(_data  = Object.values(response["data"]),
                               _label = Object.keys(response["data"]), 
                               title  = "Vente par pays"),
                divGraph = ctx))
            break;

          case "_date":
            instance_main_chart.push(
              createGraph(
                barChart(_data  = Object.values(response["data"]),
                         _label = Object.keys(response["data"]), 
                         title  = "Vente par mois",
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
                               title  = "Vente d'un produit dans les pays"),
                divGraph = cty))
            break;

          case "papr":
            instance_detail_chart.push(
              createGraph(
                barChart(_data  = Object.values(response["data"]),
                         _label = Object.keys(response["data"]).map(x => {return x.split(" ");}), // cuts the description at each space so that each member 
                                                                                                  // composing the label is on one line when the graph is displayed
                         title  = "Vente d'un produits dans le pays"),
                divGraph = cty))
            break;

          case "dprpa":
            instance_detail_chart.push(
              createGraph(
                barChart(_data  = Object.values(response["data"][0]),
                         _label = Object.keys(response["data"][0]).map(x => {return x.split(" ");}), // cuts the description at each space so that each member 
                                                                                                     // composing the label is on one line when the graph is displayed
                         title  = "Vente dans le mois"),
                divGraph  = cty))
            instance_detail_chart.push(
              createGraph(
                polarAreaChart(_data  = Object.values(response["data"][1]),
                               _label = Object.keys(response["data"][1]),
                               title  = "Vente dans un mois dans un pays"),
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


//** allows you to click on elements of a graph to extract the value
function clickHandler(click){
  destroyCharts(instance_detail_chart)     // destroys the instance of the current detail chart to make room for a new one
  const points = instance_main_chart[0].getElementsAtEventForMode(click, 'nearest', {intersect: true}, true);
  if(points.length){
    const firstPoint = points[0];
    //const value =  instance_main_chart.data.labels[firstPoint.index]//.replaceAll(",", " "); //_labels[firstPoint.index]
    const lab = instance_main_chart[0].data.labels[firstPoint.index] // get the value of the element that was clicked on
    const value = Array.isArray(lab) ? lab.join(" ") : lab           // if the label comes from a list then we concatenate 
                                                                     // these values ​​to reconstitute it
    dataRequest({"data": value, 
                 "claim": switchDetailGraph(),
                 "choice": document.querySelector('input[name="choice"]:checked').value,
                 "limit": document.getElementById("ph").value})
  }
}

//** request given according to the button triggered beforehand
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

/** Destroys the instance of the current chart to make room for a new one
 *  @param {list} instance: chart instance list
 */ 
function destroyCharts(instance){
  if(instance.length > 0){
    instance.map(i => i.destroy())
    instance.length = 0 // Empty the vide
  }
}

/** Sets up a graph according to its location in the dom
 * @param {dict} config_chart: configuration element of a chart 
 * @param {HTML DOM Document} divGraph       : HTML DOM Document of canvas main chart or detail chart
 * @returns the instance of a chart
 */
function createGraph(config_chart, divGraph){
  const instance_chart = new Chart(divGraph, config_chart);
  if(divGraph.id == "mainChart"){ divGraph.onclick = clickHandler; } 
  return instance_chart
}