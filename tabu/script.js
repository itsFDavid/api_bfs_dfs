const URL_API = "https://api-dijkstra.onrender.com/api";

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
  tbody.innerHTML = ""; // Limpiar el contenido previo
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
    const tabu_tam = document.getElementById("tabu_tam").value;
    const iteraciones = document.getElementById("num_iter").value;
    const dataSend = {
      coord: default_coord,
      iteraciones: tabu_tam ? parseInt(iteraciones) : 100,
      tabu_tam: tabu_tam ? parseInt(tabu_tam) : 10,
    };
    const response = await fetch(`${URL_API}/tabu-tsp`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(dataSend),
    });

    const data = await response.json();
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
      return `<hr>${index + 1} - ${ciudad}</hr>`;
    })
    .join("");
  div.innerHTML = `
  <h2>Resultados</h2>
  <p>Distancia total: ${distancia} km</p><hr/>
  <p><strong>Ruta ${rutaStr}:</strong></p><hr/>
  `;

  // div.innerHTML += `
  // <p><strong>Ruta ${rutaStr}:</strong></p>
  // <p>Distancia total: ${distancia} km</p><hr/>
  // `;
}

const btnAddUbicacion = document.getElementById("add_ubi_btn");
btnAddUbicacion.addEventListener("click", () => {
  console.log("Agregando ubicación");
  const div_form = document.getElementById("container_add_ubicacion");
  div_form.style.display = "block";
  const form = document.createElement("form");
  form.innerHTML = `
    <div class="form-group">
      <div>
        <label for="nombre">Nombre de la ubicación:</label>
        <input type="text" id="nombre" required>
      </div>
      <div>
        <label for="latitud">Latitud:</label>
        <input type="number" id="latitud" step="any" required>
      </div>
      <div>
        <label for="longitud">Longitud:</label>
        <input type="number" id="longitud" step="any" required>
      </div>
    </div>
    <div class="buttons-add">
      <button type="submit" id="btnAddUbicacion">Agregar</button>
      <button type="button" id="btnClose">Cerrar</button>
    </div>
  `;
  div_form.appendChild(form);
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const nombre = document.getElementById("nombre").value;
    const latitud = parseFloat(document.getElementById("latitud").value);
    const longitud = parseFloat(document.getElementById("longitud").value);
    default_coord[nombre] = [latitud, longitud];
    fillTable();
    div_form.removeChild(form);
    div_form.removeChild(btnClose);
  });
  div_form.appendChild(form);
  const btnClose = document.getElementById("btnClose");
  btnClose.innerText = "Cerrar";
  btnClose.addEventListener("click", () => {
    div_form.style.display = "none";
    div_form.removeChild(form);
    div_form.innerHTML = ""; // Limpiar el contenido del div
  });
});
