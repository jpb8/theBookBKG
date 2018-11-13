$(document).ready(function(){

    function updateWinValue(risk, multiplier, oddId) {

        var win = parseFloat(risk * multiplier).toFixed(2);
        $("#win-" + oddId).val(win);
        return win
    }

    // for every risk input that isn't null update win
    // and calculate total win and totalRisk
    function calcAllInputs(){
        var inputs = $('.risk-input');
        var totalRisk = 0;
        var totalWin = 0;
        $.each(inputs, function(index, html){
            if( $(this).val() ) {
                var risk = $(this).val();
                var multiplier = $(this).attr("data-odds");
                var oddId = $(this).attr("data-id");
                totalRisk += parseFloat(risk);
                var win = updateWinValue(risk, multiplier, oddId);
                totalWin += parseFloat(win);
            }
        })
        return [totalRisk.toFixed(2), totalWin.toFixed(2)]
    }
    // for every risk-input change run the update win and tatal risk/win inputs
    $('input[type="number"].risk-input').on('keyup', function() {
        var totalValues;
        var totalRisk;
        var totalWin;
        totalValues = calcAllInputs("straight-bet-risk-input"); // 0 => risk 1 => wun
        $('#betlsip-total-risk').val(totalValues[0]);
        $('#betlsip-total-win').val(totalValues[1]);
    });

    $('input[type="number"].risk-input').blur(function() {
        var val = 0;
        if( $(this).val() ) {
            val = parseFloat($(this).val()).toFixed(2);
            $(this).val(val);
        }
    });


    $('#bet-form-review').click(function() {
        var inputs = $('.risk-input');
        $.each(inputs, function(index, html){
            if( !$(this).val() ) {
                alert("Please fill out all bet boxes");
                e.preventDefault();
                return false;
            }
        })
    });
})
