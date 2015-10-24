d3.json('/polls/getdata', function(error, data)
{
    if(error) {console.log(error); return}

    var today = new Date();

    var chart;
    chart = d3.select('.chart')
        .data();
});