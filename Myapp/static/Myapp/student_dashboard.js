class OpportunitySearch {
    constructor() {
        this.searchInput = document.querySelector('.search-box input');
        this.opportunityGrid = document.getElementById('opportunityGrid');
        this.noResults = document.getElementById('noResults');
        this.resultsCount = document.getElementById('resultsCount');
        this.searchResultsInfo = document.getElementById('searchResultsInfo');
        
        this.opportunities = [];
        this.searchTimeout = null;
        this.debounceDelay = 300; // milliseconds
        
        this.init();
    }
    
    init() {
        // Load existing opportunities from the page
        this.loadOpportunitiesFromDOM();
        this.attachEventListeners();
        this.updateResultsCount(this.opportunities.length);
    }
    
    loadOpportunitiesFromDOM() {
        const opportunityCards = this.opportunityGrid.querySelectorAll('.opp-card');
        
        this.opportunities = Array.from(opportunityCards).map((card, index) => {
            return {
                id: index + 1,
                element: card,
                title: card.querySelector('.opp-header h3')?.textContent || '',
                organization: card.querySelector('.opp-org')?.textContent || '',
                description: card.querySelector('.opp-desc')?.textContent || '',
                tags: Array.from(card.querySelectorAll('.opp-tags span')).map(span => span.textContent),
                type: card.querySelector('.opp-type')?.textContent || '',
                // Store original HTML for highlighting
                originalHTML: card.innerHTML
            };
        });
    }
    
    attachEventListeners() {
        // Real-time search with debouncing
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });
        
        // Clear search on escape key
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.clearSearch();
            }
        });
        
        // Also add search to the top search bar if needed
        const topSearch = document.querySelector('.top-search');
        if (topSearch) {
            topSearch.addEventListener('input', (e) => {
                this.searchInput.value = e.target.value;
                this.handleSearch(e.target.value);
            });
        }
    }
    
    handleSearch(searchTerm) {
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Set new timeout for debouncing
        this.searchTimeout = setTimeout(() => {
            this.performSearch(searchTerm);
        }, this.debounceDelay);
    }
    
    performSearch(searchTerm) {
        const trimmedTerm = searchTerm.trim().toLowerCase();
        
        if (!trimmedTerm) {
            this.showAllOpportunities();
            return;
        }
        
        const filteredOpportunities = this.opportunities.filter(opp => 
            this.opportunityMatchesSearch(opp, trimmedTerm)
        );
        
        this.displaySearchResults(filteredOpportunities, trimmedTerm);
    }
    
    opportunityMatchesSearch(opportunity, searchTerm) {
        const searchableFields = [
            opportunity.title,
            opportunity.organization,
            opportunity.description,
            opportunity.type,
            ...opportunity.tags
        ];
        
        return searchableFields.some(field => 
            field.toLowerCase().includes(searchTerm)
        );
    }
    
    displaySearchResults(opportunities, searchTerm) {
        // Hide all opportunities first
        this.opportunities.forEach(opp => {
            opp.element.style.display = 'none';
        });
        
        // Show matching opportunities with highlighting
        opportunities.forEach(opp => {
            opp.element.style.display = 'block';
            this.highlightSearchTerms(opp, searchTerm);
        });
        
        // Update results count and show/hide no results message
        this.updateResultsCount(opportunities.length);
        
        if (opportunities.length === 0) {
            this.showNoResults();
        } else {
            this.hideNoResults();
        }
    }
    
    highlightSearchTerms(opportunity, searchTerm) {
        if (!searchTerm) {
            // Restore original HTML if no search term
            opportunity.element.innerHTML = opportunity.originalHTML;
            return;
        }
        
        const elementsToHighlight = [
            { element: opportunity.element.querySelector('.opp-header h3'), text: opportunity.title },
            { element: opportunity.element.querySelector('.opp-org'), text: opportunity.organization },
            { element: opportunity.element.querySelector('.opp-desc'), text: opportunity.description }
        ];
        
        elementsToHighlight.forEach(({ element, text }) => {
            if (element && text) {
                const highlightedText = this.highlightText(text, searchTerm);
                element.innerHTML = highlightedText;
            }
        });
        
        // Highlight tags
        const tagElements = opportunity.element.querySelectorAll('.opp-tags span');
        tagElements.forEach((tagElement, index) => {
            const tagText = opportunity.tags[index];
            if (tagText && tagText.toLowerCase().includes(searchTerm)) {
                const highlightedTag = this.highlightText(tagText, searchTerm);
                tagElement.innerHTML = highlightedTag;
            }
        });
    }
    
    highlightText(text, searchTerm) {
        const regex = new RegExp(`(${this.escapeRegex(searchTerm)})`, 'gi');
        return text.replace(regex, '<span class="highlight">$1</span>');
    }
    
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    showAllOpportunities() {
        this.opportunities.forEach(opp => {
            opp.element.style.display = 'block';
            opp.element.innerHTML = opp.originalHTML; // Remove highlighting
        });
        
        this.updateResultsCount(this.opportunities.length);
        this.hideNoResults();
    }
    
    updateResultsCount(count) {
        this.resultsCount.textContent = count;
        
        if (this.searchInput.value.trim()) {
            this.searchResultsInfo.style.display = 'block';
        } else {
            this.searchResultsInfo.style.display = 'none';
        }
    }
    
    showNoResults() {
        this.noResults.style.display = 'block';
        this.opportunityGrid.style.display = 'none';
    }
    
    hideNoResults() {
        this.noResults.style.display = 'none';
        this.opportunityGrid.style.display = 'grid';
    }
    
    clearSearch() {
        this.searchInput.value = '';
        this.showAllOpportunities();
    }
}

// Deadline Filter Functionality
class DeadlineFilter {
    constructor() {
        this.deadlineFilter = document.getElementById('deadlineFilter');
        this.customDateRange = document.getElementById('customDateRange');
        this.startDate = document.getElementById('startDate');
        this.endDate = document.getElementById('endDate');
        this.applyCustomRange = document.querySelector('.apply-custom-range');
        
        this.init();
    }
    
    init() {
        this.attachEventListeners();
        this.setMinDate();
    }
    
    attachEventListeners() {
    this.deadlineFilter.addEventListener('change', (e) => {
        this.handleDeadlineFilterChange(e.target.value);
    });
    
    this.applyCustomRange.addEventListener('click', () => {
        this.applyCustomDateFilter();
    });
    
    // Add real-time date validation
    this.startDate.addEventListener('change', () => {
        this.validateDateRange();
        // Update end date min to be at least start date
        if (this.startDate.value) {
            this.endDate.min = this.startDate.value;
        }
    });
    
    this.endDate.addEventListener('change', () => {
        this.validateDateRange();
    });
}
    
    handleDeadlineFilterChange(value) {
        this.customDateRange.style.display = 'none';
        if (value === 'custom') {
            this.customDateRange.style.display = 'flex';
        } else if (value) {
            this.applyQuickFilter(value);
        } else {
            this.clearDeadlineFilter();
        }
    }
    
    applyQuickFilter(filterType) {
    const today = new Date();
    let startDate, endDate;

    switch (filterType) {
        case 'today':
            startDate = new Date(today);
            endDate = new Date(today);
            break;
        case 'week':
            startDate = new Date(today);
            endDate = new Date(today);
            endDate.setDate(today.getDate() + 7);
            break;
        case 'month':
            startDate = new Date(today);
            endDate = new Date(today);
            endDate.setMonth(today.getMonth() + 1);
            break;
        default:
            return;
    }

    // Filter opportunities
    this.filterOpportunitiesByDateRange(startDate, endDate);
    this.showFilterActiveState(filterType);
    
    // Handle search + filter combination
    this.handleSearchAndFilterCombination();

  }

filterOpportunitiesByDateRange(startDate, endDate) {
    const opportunities = document.querySelectorAll('.opp-card');
    let visibleCount = 0;

    opportunities.forEach(opp => {
        const deadlineStr = opp.getAttribute('data-deadline');
        if (!deadlineStr) {
            opp.style.display = 'none';
            return;
        }

        const deadline = new Date(deadlineStr);
        
        // Check if deadline is within range
        if (deadline >= startDate && deadline <= endDate) {
            opp.style.display = 'block';
            visibleCount++;
        } else {
            opp.style.display = 'none';
        }
    });

    // Update results count and show/hide no results
    this.updateFilterResults(visibleCount);
}

updateFilterResults(visibleCount) {
    const resultsCount = document.getElementById('resultsCount');
    const noResults = document.getElementById('noResults');
    const opportunityGrid = document.getElementById('opportunityGrid');

    resultsCount.textContent = visibleCount;

    if (visibleCount === 0) {
        noResults.style.display = 'block';
        opportunityGrid.style.display = 'none';
    } else {
        noResults.style.display = 'none';
        opportunityGrid.style.display = 'grid';
    }

    // Show results info
    const searchResultsInfo = document.getElementById('searchResultsInfo');
    searchResultsInfo.style.display = 'block';
}
    
    applyCustomDateFilter() {
    const start = this.startDate.value;
    const end = this.endDate.value;
    
    if (!start || !end) {
        alert('Please select both start and end dates');
        return;
    }
    
    const startDate = new Date(start);
    const endDate = new Date(end);
    
    if (startDate > endDate) {
        alert('End date cannot be before start date');
        return;
    }
    
    console.log(`Applying custom date range: ${start} to ${end}`);
    
    this.filterOpportunitiesByDateRange(startDate, endDate);
    this.showFilterActiveState('custom');
    
    this.handleSearchAndFilterCombination();
}
    
    showFilterActiveState(filterType) {
        this.deadlineFilter.style.borderColor = '#00c6ff';
        this.deadlineFilter.style.backgroundColor = '#f0f9ff';
    }
    
    clearDeadlineFilter() {
    this.deadlineFilter.style.borderColor = '';
    this.deadlineFilter.style.backgroundColor = '';
    this.customDateRange.style.display = 'none';
    this.startDate.value = '';
    this.endDate.value = '';
    
    const searchInput = document.querySelector('.search-box input');
    const searchTerm = searchInput.value.trim();
    
    if (searchTerm) {
        const searchEvent = new Event('input', { bubbles: true });
        searchInput.dispatchEvent(searchEvent);
    } else {
        const opportunities = document.querySelectorAll('.opp-card');
        opportunities.forEach(opp => {
            opp.style.display = 'block';
        });
        
        const resultsCount = document.getElementById('resultsCount');
        const searchResultsInfo = document.getElementById('searchResultsInfo');
        resultsCount.textContent = opportunities.length;
        searchResultsInfo.style.display = 'none';
        
        const noResults = document.getElementById('noResults');
        const opportunityGrid = document.getElementById('opportunityGrid');
        noResults.style.display = 'none';
        opportunityGrid.style.display = 'grid';
    }
    
    console.log('Deadline filter cleared');
}
    
    setMinDate() {
        const today = new Date().toISOString().split('T')[0];
        this.startDate.min = today;
        this.endDate.min = today;
    }

handleSearchAndFilterCombination() {
    const searchInput = document.querySelector('.search-box input');
    const searchTerm = searchInput.value.trim();
    
    if (searchTerm) {
        const searchEvent = new Event('input', { bubbles: true });
        searchInput.dispatchEvent(searchEvent);
    }
  }

  validateDateRange() {
    const start = this.startDate.value;
    const end = this.endDate.value;
    
    if (start && end) {
        const startDate = new Date(start);
        const endDate = new Date(end);
        
        if (startDate > endDate) {
            this.endDate.setCustomValidity('End date must be after start date');
        } else {
            this.endDate.setCustomValidity('');
        }
    }
}
}

document.addEventListener('DOMContentLoaded', () => {
    window.opportunitySearchInstance = new OpportunitySearch(); // Store instance globally
    new DeadlineFilter(); 
});

const avatar = document.getElementById('profileAvatar');
const menu = document.getElementById('profileMenu');
avatar.addEventListener('click', () => { menu.parentElement.classList.toggle('show'); });
window.addEventListener('click', (e) => {
    if (!avatar.contains(e.target) && !menu.contains(e.target)) { 
        menu.parentElement.classList.remove('show'); 
    }
});
