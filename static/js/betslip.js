$(document).ready(function(){

    function updateTotalInputs(totalRisk, totalWin) {
        $("#betlsip-total-risk").val(totalRisk);
        $("#betlsip-total-win").val(totalWin);
        $("#betlsip-total-risk-model").val(totalRisk);
        $("#betlsip-total-win-model").val(totalWin);
    }

    function loadValsFromStorage() {
        var totalRisk = 0;
        var totalWin = 0;
        $.each($('.bet-input'), function(index, html){
            var betVal = localStorage.getItem($(this).attr("id"));
            if( betVal ) {
                if( $(this).hasClass("risk-input") ) {
                    totalRisk += Number(betVal);
                } else if ( $(this).hasClass("win-input") ) {
                    totalWin += Number(betVal);
                }
                $(this).val(betVal);
                $("#" + $(this).attr("id") + "-modal").val(betVal);
            }
        })
        updateTotalInputs(totalRisk, totalWin);
        localStorage.clear();
    }

    loadValsFromStorage();

    function updateWinValue(risk, multiplier, oddId) {

        var win = parseFloat(risk * multiplier).toFixed(2);
        $("#win-" + oddId).val(win);
        $("#win-" + oddId + "-model").val(win); // update model bet values
        return win
    }

    function addValuesToStorage(risk, win, oddId) {
        localStorage.setItem('risk-' + oddId, risk);
        localStorage.setItem('win-' + oddId, win);

    }

    // for every risk input that isn't null update win
    // and calculate total win and totalRisk
    function calcAllInputs(){
        var inputs = $('.risk-input');
        var totalRisk = 0;
        var totalWin = 0;
        $.each(inputs, function(index, html){
            var risk = $(this).val();
            var multiplier = $(this).attr("data-odds");
            var oddId = $(this).attr("data-id");
            if( risk ) {
                totalRisk += parseFloat(risk);
                var win = updateWinValue(risk, multiplier, oddId);
                totalWin += parseFloat(win);
                addValuesToStorage(risk, win, oddId);
                $("#" + $(this).attr("id") + "-model").val(risk);
            } else {
                $("#win-" + oddId).val(null);
                $("#win-" + oddId + "-model").val(null);
                $("#" + $(this).attr("id") + "-model").val(null);
            }
        })
        return [totalRisk.toFixed(2), totalWin.toFixed(2)]
    }

    // for every risk-input change run the update win and tatal risk/win inputs
    $('#slip-bets').on("keyup", '.risk-input', function() {
        var totalValues = calcAllInputs(); // 0 => risk 1 => won
        updateTotalInputs(totalValues[0], totalValues[1]);
        // $('#betlsip-total-risk').val(totalValues[0]);
        // $('#betlsip-total-risk-model').val(totalValues[0]);
        // $('#betlsip-total-win').val(totalValues[1]);
        // $('#betlsip-total-win-model').val(totalValues[1]);
    });

    $('#slip-bets').on('blur', '.risk-input', function() {
        var val = 0;
        if( $(this).val() ) {
            val = parseFloat($(this).val()).toFixed(2);
            $(this).val(val);
            $("#" + $(this).attr("id") + "-model").val(val);
        }
    });

    $('#betslip-model').on('show.bs.modal', function (e) {
        var button = e.relatedTarget;
        if($(button).hasClass('no-modal')) {
            e.stopPropagation();
        }
    });

    // validate Bet
    $('#bet-form-review').click(function() {
        var inputs = $('.risk-input');
        $.each(inputs, function(index, html){
            var maxBet = Number($(this).attr("data-max-bet"))
            var betVal = Number($(this).val())
            if( !betVal ) {
                alert("Please fill out all bet boxes");

                return false;
            } else if ( maxBet < betVal ) {
                alert("Exceded Max Bet of " + maxBet);
                return false;
            }
        });
        // update model values for betslip check
        var totalValues = calcAllInputs(); // 0 => risk 1 => won
        updateTotalInputs(totalValues[0], totalValues[1]);
    });
})
