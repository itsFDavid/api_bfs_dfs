const URL_API = "https://api-bfs-dfs-1.onrender.com";

const coord_default = {
  "EDO.MEX": [19.29370432359307, -99.65371080401178],
  QRO: [20.593507359686654, -100.39007276165671],
  CDMX: [19.43291511136525, -99.13336444220519],
  SPL: [22.15093335177082, -100.97414039898334],
  MTY: [25.67505869471195, -100.28758283172263],
  PUE: [19.063633672407946, -98.3069909799001],
  GDL: [20.677204573193357, -103.34699475549439],
  MICH: [19.702594693971918, -101.1923828770145],
  SON: [29.075226304565465, -110.95962477492],
};

const pedidos_default = {
  "EDO.MEX": 10,
  QRO: 13,
  CDMX: 7,
  SPL: 11,
  MTY: 15,
  PUE: 8,
  GDL: 6,
  MICH: 7,
  SON: 8,
};

document.getElementById("vrp-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    max_carga: parseInt(document.getElementById("max_carga").value),
    tiempo_max: parseFloat(document.getElementById("tiempo_max").value),
    velocidad: parseFloat(document.getElementById("velocidad").value),
    tiempo_carga: parseFloat(document.getElementById("tiempo_carga").value),
  };

  try {
    const res = await fetch(`${URL_API}/api/vrp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const rutas = await res.json();
    console.log(rutas);
    mostrarResultado(rutas);
  } catch (error) {
    document.getElementById(
      "resultado"
    ).innerHTML = `<p style="color:red;">Error al calcular rutas.</p>`;
    console.error(error);
  }
});

function mostrarResultado(data) {
  const { rutas, error } = data;
  const div = document.getElementById("resultado");
  div.innerHTML = "";
  if (error) {
    div.innerHTML = `<p style="color:red;">${error}</p>`;
    return;
  }
  if (!rutas.length) {
    div.innerHTML = "<p>No se encontraron rutas.</p>";
    return;
  }
  const totalCarga = rutas.reduce((acc, r) => acc + r.carga, 0);
  const totalTiempo = rutas.reduce((acc, r) => acc + r.tiempo_total, 0).toFixed(2);
  // si  9 minutos = (9 * 1) / 60 = 0.15 horas

  const horas = Math.floor(totalTiempo);
  const minutos = Math.round((totalTiempo - horas) * 60);
  const tiempoEstimado = `${horas} horas, ${minutos} minutos`;

  div.innerHTML = `<h3>Resultados</h3>
    <p><strong>Total de carga:</strong> ${totalCarga}</p>
    <p><strong>Total de tiempo estimado:</strong> ${tiempoEstimado}</p>
    <hr/>`;

  // div.innerHTML = "<h3>Rutas Óptimas</h3><hr/>";
  rutas.forEach((r, i) => {
    div.innerHTML += `
      <p><strong>Ruta ${i + 1}:</strong> ${r.ruta.join(" ➜ ")}</p>
      <p>Carga total: ${r.carga}</p>
      <p>Tiempo estimado: ${r.tiempo_estimado}</p><hr/>
    `;
  });
}

function llenarTabla() {
  const tbody = document.querySelector("#tabla-coordenadas tbody");
  for (const ciudad in coord_default) {
    const fila = document.createElement("tr");
    const [lat, lon] = coord_default[ciudad];
    const pedidos = pedidos_default[ciudad];

    fila.innerHTML = `
      <td>${ciudad}</td>
      <td>${lat.toFixed(6)}</td>
      <td>${lon.toFixed(6)}</td>
      <td>${pedidos}</td>
    `;
    tbody.appendChild(fila);
  }
}

document.addEventListener("DOMContentLoaded", llenarTabla);
