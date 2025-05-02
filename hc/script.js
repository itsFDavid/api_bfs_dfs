const URL_API = "http://127.0.0.1:5001";

const default_coord = {
  Jiloyork: [19.916012, -99.58058],
  Toluca: [19.289165, -99.655697],
  Atlacomulco: [19.79952, -99.873844],
  Guadalajara: [20.677754472859146, -103.34625354877137],
  Monterrey: [25.69161110159454, -100.321838480256],
  QuintanaRoo: [21.163111924844458, -86.80231502121464],
  Michohacan: [19.701400113725654, -101.20829680213464],
  Aguascalientes: [21.87641043660486, -102.26438663286967],
  CDMX: [19.432713075976878, -99.13318344772986],
  QRO: [20.59719437542255, -100.38667040246602],
};

function fillTable() {
  const tbody = document.querySelector("#tabla-coordenadas tbody");
  for (const ciudad in default_coord) {
    const fila = document.createElement("tr");
    const [lat, lon] = default_coord[ciudad];

    fila.innerHTML = `
      <td>${ciudad}</td>
      <td>${lat.toFixed(6)}</td>
      <td>${lon.toFixed(6)}</td>
    `;
    tbody.appendChild(fila);
  }
}

document.addEventListener("DOMContentLoaded", fillTable);

const btn = document.getElementById("btn");
btn.addEventListener("click", async () => {
  try {
    const response = await fetch(`${URL_API}/ihc`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(default_coord),
    });
    const data = await response.json();
    console.log(data);
    mostrarResultado(data);
  } catch (error) {
    console.error("Error al enviar la solicitud:", error);
    document.getElementById(
      "resultado"
    ).innerHTML = `<p style="color:red;">Error al calcular rutas.</p>`;
  }
});

function mostrarResultado(data) {
  const { ruta, distancia } = data;
  const div = document.getElementById("resultado");
  div.innerHTML = "";
  if (!ruta || !distancia) {
    div.innerHTML = "<p>No se encontraron rutas.</p>";
    return;
  }
  const rutaStr = ruta
    .map((ciudad, index) => {
      return `<hr>${index+1} - ${ciudad}</hr>`;
    }).join("");
  div.innerHTML = `
  <h2>Resultados</h2>
  <p><strong>Ruta ${rutaStr}:</strong></p><hr/>
  <p>Distancia total: ${distancia} km</p><hr/>
  `;

  // div.innerHTML += `
  // <p><strong>Ruta ${rutaStr}:</strong></p>
  // <p>Distancia total: ${distancia} km</p><hr/>
  // `;
}
