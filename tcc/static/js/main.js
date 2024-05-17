/* console.log("Loading jQuery document ready...");

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

*/
/*
console.log("Loading jQuery document ready...");

$(document).ready(function() {
    console.log("jQuery document ready");  // Verificar que jQuery se ejecuta
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'es',  // Configuración de idioma a español
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
        }],
        buttonText: {  // Personalización de textos de los botones
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día'
        },
        headerToolbar: {  // Configuración de la barra de herramientas del calendario
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }
    });
    calendar.render();
    console.log("Calendar rendered");  // Verificar que el calendario se renderiza
});

*/

console.log("Loading jQuery document ready...");

$(document).ready(function() {
    console.log("jQuery document ready");  // Verificar que jQuery se ejecuta
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'es',  // Configuración de idioma a español
        firstDay: 1, // Configuración para que la semana comience el lunes. 
        initialView: 'dayGridMonth',
        eventDidMount: function(info) {
            console.log(info.event);  // Verificar que los eventos se cargan correctamente
        },
        loading: function(isLoading) {
            if (isLoading) { // Cuando empieza a cargar eventos
                console.log('Loading events...');
            } else { // Cuando termina de cargar eventos
                console.log('Events loaded');
            }
        },
        eventSources: [{
            url: '/calendar_events',  // Única fuente de eventos definida aquí
            method: 'GET',
            failure: function() {
                alert('There was an error while fetching events!');
            }
        }],
        buttonText: {  // Personalización de textos de los botones
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día'
        },
        headerToolbar: {  // Configuración de la barra de herramientas del calendario
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }
    });
    calendar.render();
    console.log("Calendar rendered");  // Verificar que el calendario se renderiza correctamente
});
