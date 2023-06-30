jQuery(document).ready(function(){
	jQuery("#add-event").submit(function(){
		alert("Submitted");
		var values = {};
		$.each($('#add-event').serializeArray(), function(i, field) {
			values[field.name] = field.value;
		});
		console.log(
			values
		);
	});
});

(function () {
	'use strict';
	// ------------------------------------------------------- //
	// Calendar
	// ------------------------------------------------------ //
	jQuery(function() {
		// page is ready
		jQuery('#calendar').fullCalendar({
			themeSystem: 'bootstrap4',
			// emphasizes business hours
			businessHours: false,
			defaultView: 'month',
			// event dragging & resizing
			editable: true,
			// header
			header: {
				left: 'title',
				// center: 'month,agendaWeek,agendaDay',
				right: 'today prev,next'
			},
			events: [
			{
				title: 'Barber',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-05-05',
				end: '2020-05-05',
				className: 'fc-bg-default',
				icon : "circle"
			},
			{
				title: 'Flight Paris',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-08-08T14:00:00',
				end: '2020-08-08T20:00:00',
				className: 'fc-bg-deepskyblue',
				icon : "cog",
				allDay: false
			},
			{
				title: 'Team Meeting',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-07-10T13:00:00',
				end: '2020-07-10T16:00:00',
				className: 'fc-bg-pinkred',
				icon : "group",
				allDay: false
			},
			{
				title: 'Meeting',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-08-12',
				className: 'fc-bg-lightgreen',
				icon : "suitcase"
			},
			{
				title: 'Conference',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-08-13',
				end: '2020-08-15',
				className: 'fc-bg-blue',
				icon : "calendar"
			},
			{
				title: 'Baby Shower',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-08-13',
				end: '2020-08-14',
				className: 'fc-bg-default',
				icon : "child"
			},
			{
				title: 'Birthday',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-09-13',
				end: '2020-09-14',
				className: 'fc-bg-default',
				icon : "birthday-cake"
			},
			{
				title: 'Restaurant',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-10-15T09:30:00',
				end: '2020-10-15T11:45:00',
				className: 'fc-bg-default',
				icon : "glass",
				allDay: false
			},
			{
				title: 'Dinner',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-11-15T20:00:00',
				end: '2020-11-15T22:30:00',
				className: 'fc-bg-default',
				icon : "cutlery",
				allDay: false
			},
			{
				title: 'Shooting',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-08-25',
				end: '2020-08-25',
				className: 'fc-bg-blue',
				icon : "camera"
			},
			{
				title: 'Go Space :)',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-12-27',
				end: '2020-12-27',
				className: 'fc-bg-default',
				icon : "rocket"
			},
			{
				title: 'Dentist',
				description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras eu pellentesque nibh. In nisl nulla, convallis ac nulla eget, pellentesque pellentesque magna.',
				start: '2020-12-29T11:30:00',
				end: '2020-12-29T012:30:00',
				className: 'fc-bg-blue',
				icon : "medkit",
				allDay: false
			}
			],
			dayClick: function() {
                var date = $(this).attr("data-date")
                if (new Date() >= new Date(date)) {
                    jQuery('#modal-view-event-add').modal();
                    data = {}
                    data['uid'] = user_id
                    data['survey_date'] = date
                    $.ajax({
                        type: 'POST',
                        url: dashboard_calendar_inhalations_url,
                        dataType:'json',
                        data: data,
                        success: function (data) {
                            if (data['status'] == 200) {
                                var html = ''
                                console.log(data['data'])
                                $.each(data['data'], function(key, val) {
                                    html = html+'<tr>'
                                    html = html+'<th scope="row">'+val['time']+'</th>'
                                    if (val['angle'] == 1) {
                                        html = html+'<th scope="row"><i class="icon-copy fa fa-check" aria-hidden="true" style="color:green"></i></th>'
                                    } else {
                                        html = html+'<th scope="row"><i class="icon-copy fa fa-times" aria-hidden="true" style="color:red"></i></th>'
                                    }
                                    if (val['shaken'] == 1) {
                                        html = html+'<th scope="row"><i class="icon-copy fa fa-check" aria-hidden="true" style="color:green"></i></th>'
                                    } else {
                                        html = html+'<th scope="row"><i class="icon-copy fa fa-times" aria-hidden="true" style="color:red"></i></th>'
                                    }
                                    html = html+'</tr>'
                                });
                                $("#calendar_inhalation_table tbody").html(html);
                            }
                        },
                        error: function(XMLHttpRequest, textStatus, errorThrown) {
                            $('#city').val('Error occurred in getting forecast')
                        }
                    });
                    $.ajax({
                        type: 'POST',
                        url: dashboard_calendar_survey_details_url,
                        dataType:'json',
                        data: data,
                        success: function (data) {
                            if (data['status'] == 200) {
                                var html = ''
                                if (data['survey_taken'] == 1 || data['survey_taken'] == '1') {
                                    $.each(data['data'], function(key, val) {
                                        var response = ''
                                        if (val.options[val.response-1] == undefined) {
                                            response = 'Not answered'
                                        } else {
                                            response = val.options[val.response-1]
                                        }
                                        html = html + '<div class="card"><div class="card-header">Question #'+(key+1)+'</div><div class="card-body">'+val.question+'</div><div class="card-body">'+response+'</div></div>'
                                    });
                                } else {
                                    html = html + '<div class="card"><div class="card-header">Survey not taken for selected date. <a href='+take_survey_url+'?survey_date='+date+'>Click here to take</a></div></div>'
                                }
                                $("#accordion").html(html);
                            }
                        },
                        error: function(XMLHttpRequest, textStatus, errorThrown) {
                            $('#city').val('Error occurred in getting forecast')
                        }
                    });
                }
			},
			eventClick: function(event, jsEvent, view) {
				jQuery('.event-icon').html("<i class='fa fa-"+event.icon+"'></i>");
				jQuery('.event-title').html(event.title);
				jQuery('.event-body').html(event.description);
				jQuery('.eventUrl').attr('href',event.url);
				jQuery('#modal-view-event').modal();
			},
		})
});

})(jQuery);