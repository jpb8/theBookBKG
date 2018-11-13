$(document).ready(function(){
    var betForm = $(".form-betslip-ajax")
/* Need to Change for Parlay Logic */
    betForm.submit(function(event){
        event.preventDefault();
        var thisForm = $(this)
        var actionEndpoint = thisForm.attr("action");
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serialize();
        // Send Odd id and get back new side bar HTML as string
        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            success: function(data){
                dataSlipBets = JSON.parse(data.slipBets)
                var slipSideBar = document.getElementById('bets')
                slipSideBar.html(data);

                // for (i = 0; i < dataSlipBets.length; i++) {
                //     betNumb = i + 1
                //     tableBet = dataSlipBets[i]
                //     slipBetsHtml += "<tr><th scope='row'>" + betNumb +"</th><td><a href='#'>" + tableBet.fields.home + ": " + tableBet.fields.type + "</a></td><td>" + tableBet.fields.price + "</td><td></td></tr>"
                // };
                // slipBetsHtml += "<tr><th scope='row'></th><td>Total: " + data.slipTotal + "</td><td>Parlay Odds: " + data.slipOdds + "</td><td>Due: " + data.slipDue + "</tr>"
                // $('#slip-table-body').html(slipBetsHtml)
            },
            error: function(errorData){
                console.log(errorData)
            }
        })
    })

    var betForm = $(".form-parley-ajax");

    betForm.submit(function(event){
        event.preventDefault();
        var thisForm = $(this);
        var actionEndpoint = thisForm.attr("action");
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serialize();

        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            dataType: 'json',
            success: function(data){
                var slipOdds = $(".betslip-span")
                var options, index, select, option;

                slipOdds.text(data.slipOdds + " $" + data.slipDue);
                select = document.getElementById('bet_id');
                select.options.length = 0;

                dataBet = JSON.parse(data.oddsRemain); // Or whatever source information you're working with
                for (i = 0; i < dataBet.length; i++) {
                    option = dataBet[i];
                    select.options.add(new Option(option.fields.price, option.pk));
                };

                dataSlipBets = JSON.parse(data.slipBets);
                var slipTableHtml = ""
                var tableBet, table, betNumb
                table = document.getElementById('slip-table-body')
                for (i = 0; i < dataSlipBets.length; i++) {
                    betNumb = i + 1
                    tableBet = dataSlipBets[i]
                    slipTableHtml += "<tr><th scope='row'>" + betNumb +"</th><td><a href='#'>" + tableBet.fields.home + ": " + tableBet.fields.type + "</a></td><td>" + tableBet.fields.price + "</td></tr>"
                    $('#slip-table-body').html(slipTableHtml)
                };

            },
            error: function(errorData){
                console.log(errorData)
            }
        });
    });

    $('[data-toggle="offcanvas"]').click(function () {
        $('.row-offcanvas').toggleClass('active')
    });

});
