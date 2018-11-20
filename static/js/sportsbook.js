$(document).ready(function(){
    $('#first-half-bets-wrapper').addClass('bets-hidden');
    $("#bet-type-select").change(function() {
        if( $(this).val() == "game" ) {
            console.log("test")
            $('#first-half-bets-wrapper').addClass('bets-hidden');
            $('#full-game-bets-wrapper').removeClass('bets-hidden');
        } else if ( $(this).val() == "first-half" ) {
            console.log("test 1st half")
            $('#full-game-bets-wrapper').addClass('bets-hidden');
            $('#first-half-bets-wrapper').removeClass('bets-hidden');
        }
    });
});
