$(".tab-wizard").steps({
	headerTag: "h5",
	bodyTag: "section",
	transitionEffect: "fade",
	titleTemplate: '<span class="step">#index#</span> #title#',
	labels: {
		finish: "Submit"
	},
	onStepChanged: function (event, currentIndex, priorIndex) {
		console.log('wiz1_changed')
		$('.steps .current').prevAll().addClass('disabled');
	},
	onFinished: function (event, currentIndex) {
		console.log('wiz1')
		$('#success-modal').modal('show');
	}
});

$(".tab-wizard2").steps({
	headerTag: "h5",
	bodyTag: "section",
	transitionEffect: "fade",
	titleTemplate: '<span class="step">#index#</span> <span class="info">#title#</span>',
	labels: {
		finish: "Submit",
		next: "Next",
		previous: "Previous",
	},
	onStepChanged: function(event, currentIndex, priorIndex) {
		console.log('wiz2_changed')
        if (currentIndex == 2) {
            $("#email_confirm").text($("#id_email").val())
            $("#full_name_confirm").text($("#id_first_name").val()+" "+$("#id_last_name").val())
            var location = ''
            if ($("#id_city").val() != '') {
                location = $("#id_city").val()
            }
            if ($("#id_state").val() != '') {
                if (location != '') {
                    location = location + ',' + $("#id_state").val()
                } else {
                    location = $("#id_state").val()
                }
            }
            if ($("#id_country").val() != '') {
                if (location != '') {
                    location = location + ',' + $("#id_country").val()
                } else {
                    location = $("#id_country").val()
                }
            }
            $("#location_confirm").text(location)
        }
		$('.steps .current').prevAll().addClass('disabled');
	},
	onFinished: function(event, currentIndex) {
        $( "#registration" ).submit();
	}
});