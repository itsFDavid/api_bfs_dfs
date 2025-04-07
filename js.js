// Prevent form submissions
document.addEventListener("submit", function (e) {
  e.preventDefault();
  return false;
});

// Graph data structure
let graph = {};
let nodes = [];
let nodePositions = {};

// DOM elements
const nodeCountInput = document.getElementById("nodeCount");
const createNodesBtn = document.getElementById("createNodes");
const sourceNodeSelect = document.getElementById("sourceNode");
const targetNodeSelect = document.getElementById("targetNode");
const weightInput = document.getElementById("weight");
const addEdgeBtn = document.getElementById("addEdge");
const findPathBtn = document.getElementById("findPath");
const graphVisualization = document.getElementById("graphVisualization");
const resultsDiv = document.getElementById("results");
const pathResultDiv = document.getElementById("pathResult");
const distanceResultDiv = document.getElementById("distanceResult");
const resultImage = document.getElementById("resultImage");
const edgeError = document.getElementById("edgeError");

// Create nodes based on user input
createNodesBtn.addEventListener("click", (e) => {
  e.preventDefault(); // Prevent page reload
  const count = parseInt(nodeCountInput.value);
  if (count < 2) {
    alert("Por favor ingrese al menos 2 nodos");
    return;
  }

  // Reset everything
  graph = {};
  nodes = [];
  nodePositions = {};
  graphVisualization.innerHTML = "";
  sourceNodeSelect.innerHTML = "";
  targetNodeSelect.innerHTML = "";
  resultsDiv.style.display = "none";
  edgeError.textContent = "";

  // Create nodes
  for (let i = 1; i <= count; i++) {
    const nodeName = `Nodo ${i}`;
    nodes.push(nodeName);
    graph[nodeName] = {};

    // Add to dropdowns
    const sourceOption = document.createElement("option");
    sourceOption.value = nodeName;
    sourceOption.textContent = nodeName;
    sourceNodeSelect.appendChild(sourceOption);

    const targetOption = document.createElement("option");
    targetOption.value = nodeName;
    targetOption.textContent = nodeName;
    targetNodeSelect.appendChild(targetOption);

    // Position node randomly in the visualization
    const angle = (2 * Math.PI * (i - 1)) / count;
    const radius =
      Math.min(
        graphVisualization.offsetWidth,
        graphVisualization.offsetHeight
      ) * 0.4;
    const x = graphVisualization.offsetWidth / 2 + radius * Math.cos(angle);
    const y = graphVisualization.offsetHeight / 2 + radius * Math.sin(angle);

    nodePositions[nodeName] = { x, y };

    // Create visual node
    createVisualNode(nodeName, x, y);
  }
});

// Add edge between nodes
addEdgeBtn.addEventListener("click", (e) => {
  e.preventDefault(); // Prevent page reload
  const source = sourceNodeSelect.value;
  const target = targetNodeSelect.value;
  const weight = parseInt(weightInput.value);

  edgeError.textContent = "";

  // Validate
  if (!source || !target) {
    edgeError.textContent =
      "Por favor seleccione tanto el nodo de origen como el de destino";
    return;
  }

  if (source === target) {
    edgeError.textContent = "Un nodo no puede conectarse a sí mismo";
    return;
  }

  if (weight <= 0) {
    edgeError.textContent = "El peso debe ser mayor que 0";
    return;
  }

  // Add to graph data structure (directional - only from source to target)
  graph[source][target] = weight;

  // Create visual edge with direction
  createVisualEdge(source, target, weight);
});

// Find shortest path
findPathBtn.addEventListener("click", async (e) => {
  e.preventDefault(); // Prevent page reload

  if (Object.keys(graph).length === 0) {
    alert("Por favor, cree un grafo primero");
    return;
  }

  const source = sourceNodeSelect.value;
  const target = targetNodeSelect.value;

  if (!source || !target) {
    alert("Por favor seleccione tanto el nodo de origen como el de destino");
    return;
  }

  try {
    const response = await fetch("https://api-dijkstra.onrender.com/dijkstra", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        grafo: graph,
        nodo_inicial: source,
        nodo_final: target,
      }),
    });

    if (!response.ok) {
      throw new Error("La respuesta de la red no fue satisfactoria");
    }

    const data = await response.json();
    console.log("Response data:", data);

    // Display results
    resultsDiv.style.display = "block";
    pathResultDiv.textContent = `Camino: ${data.camino.join(" → ")}`;
    distanceResultDiv.textContent = `Distancia Total: ${data.distancia}`;

    if (data.imagen_url) {
      resultImage.src = data.imagen_url;
      resultImage.style.display = "block";
    } else {
      resultImage.style.display = "none";
    }
  } catch (error) {
    console.error("Error:", error);
    alert(
      "Error al encontrar el camino. Asegúrate de que tu servidor esté corriendo en http://localhost:5005"
    );
  }
});

// Create visual node element
function createVisualNode(name, x, y) {
  const nodeElement = document.createElement("div");
  nodeElement.className = "node";
  nodeElement.textContent = name.split(" ")[1]; // Just show the number
  nodeElement.style.left = `${x - 20}px`;
  nodeElement.style.top = `${y - 20}px`;
  nodeElement.setAttribute("data-node", name);

  // Make nodes draggable
  nodeElement.addEventListener("mousedown", startDrag);

  graphVisualization.appendChild(nodeElement);
}

// Create visual edge between nodes
function createVisualEdge(source, target, weight) {
  // Remove existing edge if any
  const existingEdges = document.querySelectorAll(
    `.edge[data-source="${source}"][data-target="${target}"]`
  );
  existingEdges.forEach((edge) => edge.remove());

  const existingLabels = document.querySelectorAll(
    `.edge-label[data-source="${source}"][data-target="${target}"]`
  );
  existingLabels.forEach((label) => label.remove());

  // Create new edge
  const sourcePos = nodePositions[source];
  const targetPos = nodePositions[target];

  const dx = targetPos.x - sourcePos.x;
  const dy = targetPos.y - sourcePos.y;
  const length = Math.sqrt(dx * dx + dy * dy);
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;

  // Adjust length to not overlap with nodes
  const adjustedLength = length - 20; // Subtract node radius

  const edge = document.createElement("div");
  edge.className = "edge";
  edge.style.width = `${adjustedLength}px`;
  edge.style.left = `${sourcePos.x}px`;
  edge.style.top = `${sourcePos.y}px`;
  edge.style.transform = `rotate(${angle}deg)`;
  edge.setAttribute("data-source", source);
  edge.setAttribute("data-target", target);

  // Create weight label
  const label = document.createElement("div");
  label.className = "edge-label";
  label.textContent = weight;
  label.style.left = `${sourcePos.x + dx / 2 - 10}px`;
  label.style.top = `${sourcePos.y + dy / 2 - 10}px`;
  label.setAttribute("data-source", source);
  label.setAttribute("data-target", target);

  graphVisualization.appendChild(edge);
  graphVisualization.appendChild(label);
}

// Dragging functionality for nodes
let draggedNode = null;
let offsetX, offsetY;

function startDrag(e) {
  draggedNode = e.target;
  const rect = draggedNode.getBoundingClientRect();
  offsetX = e.clientX - rect.left;
  offsetY = e.clientY - rect.top;

  document.addEventListener("mousemove", drag);
  document.addEventListener("mouseup", stopDrag);

  // Prevent default behavior
  e.preventDefault();
}

function drag(e) {
  if (!draggedNode) return;

  const containerRect = graphVisualization.getBoundingClientRect();
  let x = e.clientX - containerRect.left - offsetX + 20;
  let y = e.clientY - containerRect.top - offsetY + 20;

  // Keep within bounds
  x = Math.max(20, Math.min(containerRect.width - 20, x));
  y = Math.max(20, Math.min(containerRect.height - 20, y));

  draggedNode.style.left = `${x - 20}px`;
  draggedNode.style.top = `${y - 20}px`;

  // Update node position in our data
  const nodeName = draggedNode.getAttribute("data-node");
  nodePositions[nodeName] = { x, y };

  // Update all connected edges
  updateConnectedEdges(nodeName);
}

function stopDrag() {
  draggedNode = null;
  document.removeEventListener("mousemove", drag);
  document.removeEventListener("mouseup", stopDrag);
}

function updateConnectedEdges(nodeName) {
  // Update all edges where this node is the source
  for (const target in graph[nodeName]) {
    createVisualEdge(nodeName, target, graph[nodeName][target]);
  }

  // Update all edges where this node is the target
  for (const source in graph) {
    if (graph[source][nodeName]) {
      createVisualEdge(source, nodeName, graph[source][nodeName]);
    }
  }
}
