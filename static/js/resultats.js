document.addEventListener('DOMContentLoaded', function() {
          
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

   
    function updateResults() {
        const visibleRows = document.querySelectorAll('#resultsTable tbody tr:not([style*="display: none"])');
        const resultsCount = document.querySelector('.results-count span strong');
        
        if (resultsCount) {
            resultsCount.textContent = visibleRows.length;
        }
    }
    
});