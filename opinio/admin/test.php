<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Chart.js Demo</title>
  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/1.0.2/Chart.min.js"></script>
</head>
<body>

  <canvas id="piechart" width="400" height="400"></canvas>
  
  <script type="text/javascript">
    // Get the context of the canvas element we want to select
    var ctx = document.getElementById("piechart").getContext("2d");
    var data = [{
        value: 300,
        color:"#F7464A",
        highlight: "#FF5A5E",
        label: "Food"
    },
    {
        value: 50,
        color: "#46BFBD",
        highlight: "#5AD3D1",
        label: "Beverages"
    },
    {
        value: 100,
        color: "#FDB45C",
        highlight: "#FFC870",
        label: "Grocery"
    },
	{
        value: 100,
        color: "#AAB34D",
        highlight: "#00CC33",
        label: "Hygine"
    }];
    
    var options = {
      animateScale: true
    };

    var myNewChart = new Chart(ctx).Pie(data,options);
  </script>
</body>
</html>