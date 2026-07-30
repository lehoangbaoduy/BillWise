jQuery(window).on("load", function () {
    $('#preloader').fadeOut(500);
    $('#main-wrapper').addClass('show');
});



$(function () {
    $(window).on('scroll', function () {
        var WindowTop = $(window).scrollTop();
        $('section').each(function (i) {
            if (WindowTop > $(this).offset().top - 50 &&
                WindowTop < $(this).offset().top + $(this).outerHeight(true)
            ) {
                $('.menu > ul>  li > a').removeClass('active');
                $('.menu > ul>  li').eq(i).find('a').addClass('active');
            }
        });
    });

    $('a[href*=#]:not([href=#])').click(function () {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html,body').animate({
                    scrollTop: target.offset().top
                }, 1000);
                return false;
            }
        }
    });



});




// first, find all the div.code blocks
document.querySelectorAll('div.code').forEach(el => {
    // then highlight each
    hljs.highlightElement(el);
});

