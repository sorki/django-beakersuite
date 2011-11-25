$(document).ready(function() {
  $('.expand').click(function() {
    var c = $(this).parent().find('div.to_expand');
    if(c.is(':hidden')) {
      $(this).find('.icon').css('background-position', '-64px -16px');
      c.slideDown('fast').show();
    } else {
      $(this).find('.icon').css('background-position', '-32px -16px');
      c.slideUp('fast');
    }
  });
  var tabs = $( ".tabs" ).tabs();

  var hash= window.location.hash;
  var eid = hash.split('#')[2];
  var elem = $("#" + eid);
  var exp = elem.parents('td').find('.expand');
  exp.click();
  tabs.tabs('select', '#' + eid);
});
