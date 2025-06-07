const container = document.getElementById("games-container");
const loadMoreBtn = document.getElementById("load-more");
const pageSize = 8;
let currentPage = 0;

function renderGames() {
  const start = currentPage * pageSize;
  const end = start + pageSize;
  const gamesToShow = games.slice(start, end);

  gamesToShow.forEach((game) => {
    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
      <img src="/static/img/tech_diff.png" alt="Portada de ${game.Name}" />
      <div class="card-info">
        <h2>${game.Name}</h2>
        <p><strong>Año:</strong> ${game.Year}</p>
        <p><strong>Género:</strong> ${game.Genre}</p>
        <p><strong>Plataforma:</strong> ${game.Platform}</p>
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

// Cargar los primeros juegos al iniciar
renderGames();