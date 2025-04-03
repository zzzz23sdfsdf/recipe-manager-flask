document.addEventListener("DOMContentLoaded", function () {
    let searchForm = document.getElementById("search-form");
    let searchInput = document.getElementById("search-input");

    if (searchForm) {
        searchForm.addEventListener("submit", function (event) {
            let query = searchInput.value.trim(); 

            if (!query) {
                event.preventDefault(); 
                searchInput.value = ""; 
                searchInput.classList.add("is-invalid"); 
                document.getElementById("search-warning").textContent = "Search query cannot be empty or whitespace!";
                searchInput.focus(); 
            } else {
                searchInput.classList.remove("is-invalid");
                document.getElementById("search-warning").textContent = ""; 
            }
        });
    }


    highlightSearchResults();
});

function highlightSearchResults() {
    const searchQuery = new URLSearchParams(window.location.search).get("query");
    const searchType = new URLSearchParams(window.location.search).get("type");
    
    if (!searchQuery) return;
    
    const queryLower = searchQuery.toLowerCase();

    
    function highlightTextContent(selector) {
        document.querySelectorAll(selector).forEach(function(el) {
            
            if (el.closest('footer') || el.querySelector('.highlight')) return;
            
            const originalText = el.textContent;
            const lowerText = originalText.toLowerCase();
            
            if (lowerText.includes(queryLower)) {
                
                const regex = new RegExp(`(${searchQuery.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi');
                
                
                el.innerHTML = originalText.replace(regex, '<span class="highlight">$1</span>');
            }
        });
    }

    
    if (searchType === 'prep_time') {
        
        highlightTextContent('.prep-time');
        highlightTextContent('h1');
    } 
    else if (searchType === 'servings') {
        
        highlightTextContent('.servings');
        highlightTextContent('h1');
    }
    else {
        
        highlightTextContent('.recipe-title');
        highlightTextContent('.recipe-summary');
        highlightTextContent('p');
        highlightTextContent('small');
        highlightTextContent('span');
    }
}