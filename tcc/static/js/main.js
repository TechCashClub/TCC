console.log("Loading jQuery document ready...");

$(document).ready(function() {
    console.log("jQuery document ready");  // Verificar que jQuery se ejecuta
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: '/calendar_events',
        eventDidMount: function(info) {
            console.log(info.event);  // Verificar que los eventos se cargan
        },
        loading: function(isLoading) {
            if (isLoading) { // Cuando empieza a cargar eventos
                console.log('Loading events...');
            } else { // Cuando termina de cargar eventos
                console.log('Events loaded');
            }
        },
        eventSources: [{
            url: '/calendar_events',
            method: 'GET',
            failure: function() {
                alert('There was an error while fetching events!');
            }
        }]
    });
    calendar.render();
    console.log("Calendar rendered");  // Verificar que el calendario se renderiza
});
