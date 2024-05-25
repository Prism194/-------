document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const suggestionsList = document.getElementById('suggestions-list');

    searchInput.addEventListener('input', function() {
        const query = searchInput.value;

        if (query.length >= 2) {
            fetch(`/autocomplete?search=${query}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsList.innerHTML = '';
                    data.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item;
                        li.classList.add('list-group-item');
                        li.addEventListener('click', function() {
                            searchInput.value = item;
                            suggestionsList.innerHTML = '';  // Clear suggestions
                        });
                        suggestionsList.appendChild(li);
                    });
                });
        } else {
            suggestionsList.innerHTML = '';
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target)) {
            suggestionsList.innerHTML = '';
        }
    });
});
