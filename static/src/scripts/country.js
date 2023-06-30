$(function () {
   
    'use strict';
    
    var CountSelect = $('.countries'),
    
        myCountries = ['Africa', 'Antarctica', 'Asia', 'Europe'],
        
        Africa = ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burundi'],
        
        Antarctica = ['Amundsen-Scott'],
        
        Asia = ['Bangladesh', 'Bhutan', 'Brunei', 'Cambodia', 'China', 'East Timor', 'India'],
        
        Europe = ['Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia-Herzegovina', 'Bulgaria'];
        
    // Function Create Option    
    
    function CreateOption(valriable, elementToAppend) {
        
        var i;
        
        for (i = 0; i < valriable.length; i += 1) {
    
            $('<option>', {value: valriable[i], text: valriable[i], id: valriable[i]})
                .appendTo(elementToAppend);
        }
    }
    
    
    // Create Option myCountries
    CreateOption(myCountries, $('.countries'));
    
    // Create Option Africa
    CreateOption(Africa, $('.Africa'));
    
    // Create Option Africa
    CreateOption(Antarctica, $('.Antarctica'));
    
    // Create Option Africa
    CreateOption(Asia, $('.Asia'));
    
    // Create Option Africa
    CreateOption(Europe, $('.Europe'));
    
    // Hide All Select
    $('.option select').hide();
    
    // Show First Selected
    $('.Asia').show().css('display', 'inline-block');
    
    
    
    // Show List Option City Whene user Chosse Countries
    
    CountSelect.on('change', function () {
        
        // get Id option 
        var myId = $(this).find(':selected').attr('id');
        console.log($(this).val());
        // Show Select Has class = Id And Hide Siblings
        $('.option select').filter('.' + myId).fadeIn(400).siblings('select').hide();
        
    });
    
});