const API_URL = "http://localhost:5001/tsp-sa";

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

document.getElementById("btn-default").onclick = async () => {
  mostrarResultado("Calculando...");
  const temp = parseFloat(document.getElementById("temp-input").value);
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ coord: default_coord, temperatura: temp }),
  });
  const data = await res.json();
  mostrarResultado(formatearRespuesta(data));
};

document.getElementById("btn-personal").onclick = () => {
  document.getElementById("personal-form").classList.toggle("oculto");
};

document.getElementById("btn-send-personal").onclick = async () => {
  let coord;
  try {
    coord = JSON.parse(document.getElementById("coord-input").value);
    if (!coord || typeof coord !== "object") throw new Error();
  } catch {
    mostrarResultado("Formato inválido. Usa JSON: {'Ciudad':[lat,lon],...}");
    return;
  }
  mostrarResultado("Calculando...");
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ coord }),
  });
  const data = await res.json();
  mostrarResultado(formatearRespuesta(data));
};

function mostrarResultado(html) {
  document.getElementById("resultado").innerHTML = html;
}

function formatearRespuesta(data) {
  if (
    !data ||
    !data.ruta ||
    !data.distancia ||
    !data.mejor_ruta ||
    !data.mejor_distancia ||
    !data.temperatura
  )
    return "No se pudo calcular la ruta.";
  return `
    <h2>Mejor Ruta</h2>
    <p>${data.mejor_ruta.map((c, i) => `${i + 1}. ${c}`).join(" <br> ")}</p>
    <p><strong>Distancia total:</strong> ${data.mejor_distancia.toFixed(4)}</p>
    <p><strong>Temperatura:</strong> ${data.temperatura}</p>
    <h2>Ruta Inicial</h2>
    <p>${data.ruta.map((c, i) => `${i + 1}. ${c}`).join(" <br> ")}</p>
    <p><strong>Distancia total:</strong> ${data.distancia.toFixed(4)}</p>
  `;
}
