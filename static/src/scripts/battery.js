  function battery(charge) {
  var index = 0;
  $(".battery .bar").each(function() {
    var power = Math.round(charge / 10);
    if (index != power) {
      $(this).addClass("active");
      index++;
    } else {
      $(this).removeClass("active");
    }
  });
}

$(".battery .bar").click(function() {
  battery(parseInt($(this).data("power")));
});

battery(67.15); // (67%) Any number 100 or lower will work, Including decimals.
// Battery 1
function battery1(charge) {
  var index = 0;
  $(".battery1 .bar1").each(function() {
    var power = Math.round(charge / 10);
    if (index != power) {
      $(this).addClass("active");
      index++;
    } else {
      $(this).removeClass("active");
    }
  });
}

$(".battery1 .bar1").click(function() {
  battery(parseInt($(this).data("power")));
});

battery1(67.15);
//Battery 2 
function battery2(charge) {
  var index = 0;
  $(".battery2 .bar2 ").each(function() {
    var power = Math.round(charge / 10);
    if (index != power) {
      $(this).addClass("active");
      index++;
    } else {
      $(this).removeClass("active");
    }
  });
}

$(".battery2 .bar2").click(function() {
  battery(parseInt($(this).data("power")));
});

battery2(67.15);