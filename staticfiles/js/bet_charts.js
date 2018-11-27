$(document).ready(function(){
    var dynamicColors = function() {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
}

    function renderChart(id, data, labels, title){
        var ctx = document.getElementById(id).getContext('2d');
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)',
                        'rgba(30, 26, 186, 0.2)',
                        'rgba(75, 150, 92, 0.2)',
                        'rgba(53, 100, 255, 0.2)',
                        'rgba(25, 259, 64, 0.2)'

                    ],
                    borderColor: [
                        'rgba(255,99,132,1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(30, 26, 186, 1)',
                        'rgba(75, 150, 92, 1)',
                        'rgba(53, 100, 255, 1)',
                        'rgba(25, 259, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true
                        }
                    }]
                }
            }
        });
    }

//    var url = '/sportbook/event_values_charts';
//    var method = "GET";
//    var data = {};
//    $.ajax({
//        url: url,
//        method: method,
//        data: data,
//        success: function(responseData){
//            renderChart("h-sprd-val-chart", responseData.data, responseData.labels);
//        }, error: function(error){
//            console.log(error);
//        }
//    })

    function getBetData(id, type){
        var url = '/sportsbook/event_values_charts';
        var method = 'GET'
        var data = {"type": type}
        $.ajax({
            url: url,
            method: method,
            data: data,
            success: function(responseData){
                renderChart(id, responseData.data, responseData.labels, responseData.title);
            }, error: function(error){
                console.log(error);
            }
        })
    }
    var chartsToRender = $('.bet-value-chart')
    $.each(chartsToRender, function(index, html){
        var $this = $(this)
        if ( $this.attr('id') && $this.attr('data-type')){
            getBetData($this.attr('id'), $this.attr('data-type'))
        }
    })
})