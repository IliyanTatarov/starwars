$.noConflict();
jQuery( document ).ready(function($) {
    $('#fetch_btn').click(function() {
        $('#fetch_spinner').css('display', 'inline-block');
    });

    $('.btn-check-header').click(function() {
        $('#filters_form').submit();
    });
});