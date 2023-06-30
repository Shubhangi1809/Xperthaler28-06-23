
let key = "bd2eaf9116a3841621ec469b11672329"
var button = document.querySelector('.search');
var inputValue = document.querySelector('.search-box');
var name = document.querySelector('.name');
var temp = document.querySelector('.temp');
var desc = document.querySelector('.desc');
var wind = document.querySelector('.wind');
var coord = document.querySelector('.coord');
button.addEventListener('click',function(){
	
	fetch('https://api.openweathermap.org/data/2.5/weather?q='+inputValue.value+'&units=metric&APPID='+key)
	
	.then(response => response.json())
	.then(data => {
		var nameValue = data['name'];
		var tempValue = data['main']['temp'];
		var descValue = data['weather'][0]['description'];
    var windValue = data['wind']['speed'];
    var coordValue= data['coord']['lon'];

		name.innerHTML = nameValue;
		temp.innerHTML = "Temperature: "+tempValue+"°C";
		desc.innerHTML = "Weather: "+ descValue;
    wind.innerHTML = "Wind: "+ windValue;
    coord.innerHTML="Longitude:"+ coordValue+"°";
	})

	.catch(err => alert("Wrong City Name!"))
})

// var lat="";
// var log="";

function geoFindMe() {

  const status = document.querySelector('#status');
  const mapLink = document.querySelector('#map-link');

  mapLink.href = '';
  mapLink.textContent = '';

  function success(position) {
    const latitude  = position.coords.latitude;
    const longitude = position.coords.longitude;

    status.textContent = '';
    mapLink.href = `https://www.openstreetmap.org/#map=18/${latitude}/${longitude}`;
    mapLink.textContent = `Latitude: ${latitude} °, Longitude: ${longitude} °`;
  }

  function error() {
    status.textContent = 'Unable to retrieve your location';
  }

  if(!navigator.geolocation) {
    status.textContent = 'Geolocation is not supported by your browser';
  } else {
    status.textContent = 'Locating…';
    navigator.geolocation.getCurrentPosition(success, error);
  }

}

document.querySelector('.find-me').addEventListener('click', geoFindMe);

