$.noConflict();
jQuery( document ).ready(function($) {
    $('#fetch_btn').click(function() {
        $('#fetch_spinner').css('display', 'inline-block');
    });

    $('.btn-check-header').click(function() {
        $('#filters_form').submit();
    });

    $('#load_more_btn').click(function(e) {
        e.preventDefault();

        params = {
            'page' : $(this).data('page')
        }
        $.get('', params, function(data) {
            $('#character_table tbody').append(data['html']);
            $('#load_more_btn').data('page', Number($('#load_more_btn').data('page')) + 1);
            if(!data['more']) $('#load_more_btn').hide();
        });
    });
});
