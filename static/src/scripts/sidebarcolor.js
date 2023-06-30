// Selection of id's and classes from html document
const bgsideclr = document.getElementById("sideclr");
const sidebar = document.querySelector(".left-side-bar");
  
// Here we are adding event listener which 
// is used to detect the mouse movement
bgsideclr.addEventListener("input", () => {
  // This updates the background color which is 
  // picked by the user from the picker
  // document.body.style.backgroundColor = bgclr.value;
   sidebar.style.backgroundColor = bgsideclr.value;
  
  // This is the conditional statement that is used
  // to change the text color from BLACK to WHITE
  // when the background color changes to dark!
  if (
    bgsideclr.value.includes("00") ||
    bgsideclr.value.includes("0a") ||
    bgsideclr.value.includes("0b") ||
    bgsideclr.value.includes("0c") ||
    bgsideclr.value.includes("0d") ||
    bgsideclr.value.includes("0e") ||
    bgsideclr.value.includes("0f")
  ) {
    sidebar.style.color = "#fff";
  } else {
    sidebar.style.color= '#fff';
  }
});
// var colorPick = $('#clr');
// var styleElt =  '<style></style>';
// colorPick.on('change', function(){
//     console.log($(this).val());
//     var selectedVal = $(this).val();
//     $('div').html('<style>.header{background-color:'+ selectedVal +'}</style>');
// });