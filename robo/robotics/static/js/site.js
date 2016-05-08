$(function() {
  $('a[href*=#]:not([href=#])').click(function() {
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

$(document).ready(function() {
  // messages timeout for 10 sec 
  setTimeout(function() {
    $('.message').fadeOut('slow');
  }, 3000); // <-- time in milliseconds, 1000 =  1 sec

  // delete message
  $(".del-msg").click(function() {
    $('.del-msg').parent().attr('style', 'display:none;');
  });


});