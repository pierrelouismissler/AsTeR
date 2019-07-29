// $('#simulation-btn').on('click', function(e) {
//
//     $(this).button('loading');
//
// });
//
// $(document).ready(function(){
//   $("simulation-btn").click(function(){
//     $(this).button('loading');
//   });
// });

// function startSimulation(elmnt) {
//
//     elmnt.button('loading');
//     setInterval("update_values();", 3000);
//     setInterval("display_markers();", 3000);
// }

$('#myButton').on('click', function () {
    var $btn = $(this);

    $btn.button('loading');
    $btn.button('dispose');

    $btn.button('reset')
});
