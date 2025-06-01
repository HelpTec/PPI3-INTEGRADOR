const API_URL = "https://api.sampleapis.com/playstation/games";
const container = document.getElementById("games-container");
const loadMoreBtn = document.getElementById("load-more");
const pageSize = 8;
let games = [];
let currentPage = 0;

async function fetchGames() {
  try {
    const response = await fetch(API_URL);
    if (!response.ok) {
      throw new Error("Error al cargar los juegos");
    }
    games = await response.json();
    renderGames();
  } catch (error) {
    container.innerHTML = `<p style="color:red;">${error.message}</p>`;
    loadMoreBtn.style.display = "none";
  }
}

function renderGames() {
  const start = currentPage * pageSize;
  const end = start + pageSize;
  const gamesToShow = games.slice(start, end);

  gamesToShow.forEach((game) => {
    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
        <img src="./recursos/tech_diff.png" alt="Portada de ${game.title}" />
          <div class="card-info">
            <h2>${game.title}</h2>
            <p><strong>Año:</strong> ${game.year}</p>
            <p><strong>Género:</strong> ${game.genre}</p>
          </div>
        `;

    container.appendChild(card);
  });

  currentPage++;

  if (currentPage * pageSize >= games.length) {
    loadMoreBtn.style.display = "none";
  }
}

loadMoreBtn.addEventListener("click", renderGames);

// Cargar los juegos al iniciar
fetchGames();
