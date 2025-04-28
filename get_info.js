document.getElementById('newsForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const searchQuery = document.getElementById('searchQuery').value;
  const loader = document.getElementById('loader');
  const mainDiv = document.getElementById('mainDiv');
  mainDiv.innerHTML = '';
  loader.style.display = 'block';

  fetch('http://127.0.0.1:5000/news', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ query: searchQuery })
  })
  .then(response => response.json())
  .then(result => {
    loader.style.display = 'none';
    for (let news of result.articles) {
      mainDiv.innerHTML += `
        <div class="card">
          <img src="${news.urlToImage}" onerror="this.style.display='none'">
          <div class="card-body">
            <h5 class="card-title">
              <a href="${news.url}" target="_blank">${news.title}</a>
            </h5>
          </div>
        </div>`;
    }
  });
});
