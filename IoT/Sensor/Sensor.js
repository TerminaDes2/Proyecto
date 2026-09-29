var $Temp = $('#Temperatura'); // asignamos el objeto Temperatura a una variable nueva
var $Hum= $('#Humedad'); // asignamos el objeto Humedad a una variable nueva
var temp=0;
var hum=0;
var temperaturaLeida = false;
var humedadLeida = false;
var baseDatosLecturas;
var graficaTemperaturas;
var solicitudBaseDatos = indexedDB.open('SensorDB', 1);

solicitudBaseDatos.onupgradeneeded = function(event) {
baseDatosLecturas = event.target.result;
if (!baseDatosLecturas.objectStoreNames.contains('lecturas')) {
baseDatosLecturas.createObjectStore('lecturas', { keyPath: 'fecha' });
}
};

solicitudBaseDatos.onsuccess = function(event) {
baseDatosLecturas = event.target.result;
};

solicitudBaseDatos.onerror = function(event) {
console.log('No se pudo abrir la base de datos de lecturas.', event.target.error);
};

function guardarLectura() {
if (!temperaturaLeida || !humedadLeida || !baseDatosLecturas) {
return;
}

var lectura = {
fecha: new Date().toISOString(),
temperatura: Number(temp),
humedad: Number(hum)
};
var transaccion = baseDatosLecturas.transaction(['lecturas'], 'readwrite');
transaccion.objectStore('lecturas').add(lectura);
transaccion.onerror = function(event) {
console.log('No se pudo guardar la lectura.', event.target.error);
};
temperaturaLeida = false;
humedadLeida = false;
}

function obtenerFechaInicial(periodo) {
var fechaInicial = new Date();

if (periodo === 'mes') {
fechaInicial.setMonth(fechaInicial.getMonth() - 1);
return fechaInicial;
}

if (periodo === 'año') {
fechaInicial.setFullYear(fechaInicial.getFullYear() - 1);
return fechaInicial;
}

fechaInicial.setHours(fechaInicial.getHours() - Number(periodo));
return fechaInicial;
}

function actualizarGrafica(lecturas) {
var lecturasParaGrafica = lecturas.slice().sort(function(lecturaA, lecturaB) {
return new Date(lecturaA.fecha) - new Date(lecturaB.fecha);
});
var etiquetas = lecturasParaGrafica.map(function(lectura) {
return new Date(lectura.fecha).toLocaleString('es-MX');
});
var temperaturas = lecturasParaGrafica.map(function(lectura) {
return lectura.temperatura;
});

if (graficaTemperaturas) {
graficaTemperaturas.destroy();
}

graficaTemperaturas = new Chart(document.getElementById('graficaTemperaturas'), {
type: 'line',
data: {
labels: etiquetas,
datasets: [{
label: 'Temperatura (°C)',
data: temperaturas,
borderColor: '#713f9b',
backgroundColor: 'rgba(113, 63, 155, 0.16)',
borderWidth: 3,
fill: true,
tension: 0.25,
pointRadius: 3
}]
},
options: {
responsive: true,
maintainAspectRatio: false,
scales: {
y: {
title: {
display: true,
text: 'Temperatura (°C)'
}
}
},
plugins: {
legend: {
display: false
}
}
}
});
}

function mostrarHistorial() {
if (!baseDatosLecturas) {
console.log('La base de datos todavía no está disponible.');
return;
}

var historial = document.getElementById('historial');
var listaHistorial = document.getElementById('listaHistorial');
var periodo = document.getElementById('periodoHistorial').value;
var fechaInicial = obtenerFechaInicial(periodo);
var transaccion = baseDatosLecturas.transaction(['lecturas'], 'readonly');
var solicitudLecturas = transaccion.objectStore('lecturas').getAll();

solicitudLecturas.onsuccess = function() {
listaHistorial.innerHTML = '';
var lecturasFiltradas = solicitudLecturas.result.filter(function(lectura) {
return new Date(lectura.fecha) >= fechaInicial;
}).sort(function(lecturaA, lecturaB) {
return new Date(lecturaB.fecha) - new Date(lecturaA.fecha);
});

actualizarGrafica(lecturasFiltradas);

if (lecturasFiltradas.length === 0) {
var filaVacia = document.createElement('tr');
var mensaje = document.createElement('td');
mensaje.colSpan = 2;
mensaje.textContent = 'No hay temperaturas registradas en este periodo.';
filaVacia.appendChild(mensaje);
listaHistorial.appendChild(filaVacia);
} else {
lecturasFiltradas.forEach(function(lectura) {
var fila = document.createElement('tr');
var fecha = document.createElement('td');
var temperatura = document.createElement('td');
fecha.textContent = new Date(lectura.fecha).toLocaleString('es-MX');
temperatura.textContent = lectura.temperatura.toFixed(2) + ' °C';
fila.appendChild(fecha);
fila.appendChild(temperatura);
listaHistorial.appendChild(fila);
});
}
historial.hidden = false;
};
}

document.getElementById('mostrarHistorial').addEventListener('click', mostrarHistorial);
document.getElementById('periodoHistorial').addEventListener('change', mostrarHistorial);

var particle = new Particle();
var token;
particle.login({username: 'dgarcia70@ucol.mx', password: '#Elmausegamer29'}).then(
function(data) {
token = data.body.access_token;
},
function (err) {
console.log('Could not log in.', err);
}
);
setInterval(function() {

particle.getVariable({ deviceId: '29002b000b47313037363132', name: 'TEMP', auth:
token }).then(function(data) {

console.log('Device variable retrieved successfully:', data);
temp=data.body.result;
temperaturaLeida = true;
guardarLectura();

}, function(err) {
console.log('An error occurred while getting attrs:', err);
});
particle.getVariable({ deviceId: '29002b000b47313037363132', name: 'HUM', auth:
token }).then(function(data) {

console.log('Device variable retrieved successfully:', data);
hum=data.body.result;
humedadLeida = true;
guardarLectura();

}, function(err) {
console.log('An error occurred while getting attrs:', err);
});
Hum = hum.toFixed(2);
Temp = temp.toFixed(2);
$Hum.text(Hum+" %");
$Temp.text(Temp+" °C");
},60000);