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
        this.handleAllFilters(); 
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

handleAllFilters() {
    const searchTerm = this.searchInput.value.trim();
    const opportunities = document.querySelectorAll('.opp-card');
    let visibleCount = 0;

    opportunities.forEach(opp => {
        let shouldShow = true;

        if (searchTerm) {
            const title = opp.querySelector('.opp-header h3')?.textContent.toLowerCase() || '';
            const org = opp.querySelector('.opp-org')?.textContent.toLowerCase() || '';
            const desc = opp.querySelector('.opp-desc')?.textContent.toLowerCase() || '';
            const tags = Array.from(opp.querySelectorAll('.opp-tags span')).map(span => span.textContent.toLowerCase());
            
            const matchesSearch = title.includes(searchTerm) || 
                                org.includes(searchTerm) || 
                                desc.includes(searchTerm) || 
                                tags.some(tag => tag.includes(searchTerm));
            
            if (!matchesSearch) {
                shouldShow = false;
            }
        }

        const selectedTypes = Array.from(document.querySelectorAll('input[name="opportunityType"]:checked'))
            .map(cb => cb.value);
        const oppType = opp.getAttribute('data-type');
        
        if (selectedTypes.length > 0 && !selectedTypes.includes(oppType)) {
            shouldShow = false;
        }

        opp.style.display = shouldShow ? 'block' : 'none';
        if (shouldShow) visibleCount++;
    });

    this.updateResultsCount(visibleCount);
    
    if (visibleCount === 0) {
        this.showNoResults();
    } else {
        this.hideNoResults();
    }
    
    // NEW: Refresh sorting after filtering to maintain sort order
    if (window.opportunitySorterInstance) {
        window.opportunitySorterInstance.refreshSort();
    }
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

// Opportunity Type Filter Functionality
class TypeFilter {
    constructor() {
        this.typeCheckboxes = document.querySelectorAll('input[name="opportunityType"]');
        this.typeCounts = {
            assistantship: document.getElementById('count-assistantship'),
            volunteer: document.getElementById('count-volunteer'),
            sports: document.getElementById('count-sports'),
            leadership: document.getElementById('count-leadership'),
            other: document.getElementById('count-other')
        };
        this.filterCount = document.getElementById('typeFilterCount');
        this.opportunities = document.querySelectorAll('.opp-card');
        
        this.init();
    }
    
    init() {
        this.attachEventListeners();
        this.updateTypeCounts();
        this.updateFilterCountText();
    }
    
    attachEventListeners() {
        // Listen for checkbox changes
        this.typeCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.handleTypeFilterChange();
            });
        });
    }
    
    handleTypeFilterChange() {
        const selectedTypes = this.getSelectedTypes();
        
        if (selectedTypes.length === 0) {
            // If no types selected, show all
            this.showAllOpportunities();
        } else {
            // Filter opportunities based on selected types
            this.filterOpportunitiesByType(selectedTypes);
        }
        
        this.updateFilterCountText();
        this.handleSearchAndFilterCombination();
    }
    
    getSelectedTypes() {
        const selectedTypes = [];
        this.typeCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                selectedTypes.push(checkbox.value);
            }
        });
        return selectedTypes;
    }
    
    filterOpportunitiesByType(selectedTypes) {
        let visibleCount = 0;
        
        this.opportunities.forEach(opp => {
            const oppType = opp.getAttribute('data-type');
            
            if (selectedTypes.includes(oppType)) {
                opp.style.display = 'block';
                visibleCount++;
            } else {
                opp.style.display = 'none';
            }
        });
        
        this.updateResultsDisplay(visibleCount);
    }
    
    showAllOpportunities() {
        this.opportunities.forEach(opp => {
            opp.style.display = 'block';
        });
        
        const resultsCount = document.getElementById('resultsCount');
        const searchResultsInfo = document.getElementById('searchResultsInfo');
        resultsCount.textContent = this.opportunities.length;
        searchResultsInfo.style.display = 'none';
        
        const noResults = document.getElementById('noResults');
        const opportunityGrid = document.getElementById('opportunityGrid');
        noResults.style.display = 'none';
        opportunityGrid.style.display = 'grid';
    }
    
    updateResultsDisplay(visibleCount) {
    const resultsCount = document.getElementById('resultsCount');
    const noResults = document.getElementById('noResults');
    const opportunityGrid = document.getElementById('opportunityGrid');
    const searchResultsInfo = document.getElementById('searchResultsInfo');

    resultsCount.textContent = visibleCount;

    if (visibleCount === 0) {
        noResults.style.display = 'block';
        opportunityGrid.style.display = 'none';
    } else {
        noResults.style.display = 'none';
        opportunityGrid.style.display = 'grid';
    }

    if (this.categoryDropdown.value !== '') {
        searchResultsInfo.style.display = 'block';
    }
}
    
    updateTypeCounts() {
        const counts = {
            assistantship: 0,
            volunteer: 0,
            sports: 0,
            leadership: 0,
            other: 0
        };
        
        this.opportunities.forEach(opp => {
            const type = opp.getAttribute('data-type');
            if (counts.hasOwnProperty(type)) {
                counts[type]++;
            }
        });
    
        Object.keys(counts).forEach(type => {
            if (this.typeCounts[type]) {
                this.typeCounts[type].textContent = counts[type];
            }
        });
    }
    
    updateFilterCountText() {
        const selectedTypes = this.getSelectedTypes();
        const totalTypes = this.typeCheckboxes.length;
        
        if (selectedTypes.length === totalTypes) {
            this.filterCount.textContent = 'All types';
        } else if (selectedTypes.length === 0) {
            this.filterCount.textContent = 'No types selected';
        } else {
            this.filterCount.textContent = `${selectedTypes.length} type${selectedTypes.length > 1 ? 's' : ''} selected`;
        }
    }
    
    handleSearchAndFilterCombination() {
        const searchInput = document.querySelector('.search-box input');
        const searchTerm = searchInput.value.trim();
        
        if (searchTerm) {
            const searchEvent = new Event('input', { bubbles: true });
            searchInput.dispatchEvent(searchEvent);
        }
    }

    resetTypeFilter() {
        this.typeCheckboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
        this.updateFilterCountText();
    }
}

// ===== SORTING FUNCTIONALITY =====
class OpportunitySorter {
    constructor() {
        this.currentSort = 'recent';
        this.sortDirection = 'desc';
        this.sortDropdown = document.getElementById('sortDropdown');
        this.opportunityGrid = document.getElementById('opportunityGrid');
        
        this.init();
    }
    
    init() {
        this.attachEventListeners();
        this.applySort('recent', 'desc'); // Default sort
    }
    
    attachEventListeners() {
        this.sortDropdown.addEventListener('change', (e) => {
            this.handleSortChange(e.target.value);
        });
    }
    
    handleSortChange(sortType) {
        this.currentSort = sortType;
        
        // Set default direction based on sort type
        switch(sortType) {
            case 'recent':
                this.sortDirection = 'desc'; // Newest first
                break;
            case 'deadline':
                this.sortDirection = 'asc'; // Soonest first
                break;
            case 'organization':
            case 'title':
                this.sortDirection = 'asc'; // A-Z
                break;
        }
        
        this.applySort(sortType, this.sortDirection);
        this.updateSortIndicator();
    }
    
    applySort(sortType, direction) {
        const opportunities = Array.from(this.opportunityGrid.querySelectorAll('.opp-card'));
        const sortedOpportunities = this.sortOpportunities(opportunities, sortType, direction);
        
        // Clear and re-append sorted opportunities
        this.opportunityGrid.innerHTML = '';
        sortedOpportunities.forEach(opp => {
            this.opportunityGrid.appendChild(opp);
        });
    }
    
    sortOpportunities(opportunities, sortType, direction) {
        return opportunities.sort((a, b) => {
            let aValue, bValue;
            
            switch(sortType) {
                case 'recent':
                    aValue = new Date(a.getAttribute('data-posted'));
                    bValue = new Date(b.getAttribute('data-posted'));
                    break;
                case 'deadline':
                    aValue = new Date(a.getAttribute('data-deadline'));
                    bValue = new Date(b.getAttribute('data-deadline'));
                    break;
                case 'organization':
                    aValue = a.querySelector('.opp-org').textContent.toLowerCase();
                    bValue = b.querySelector('.opp-org').textContent.toLowerCase();
                    break;
                case 'title':
                    aValue = a.querySelector('.opp-header h3').textContent.toLowerCase();
                    bValue = b.querySelector('.opp-header h3').textContent.toLowerCase();
                    break;
                default:
                    return 0;
            }
            
            let comparison = 0;
            if (sortType === 'recent' || sortType === 'deadline') {
                comparison = aValue - bValue;
            } else {
                if (aValue < bValue) comparison = -1;
                if (aValue > bValue) comparison = 1;
            }
            
            return direction === 'desc' ? -comparison : comparison;
        });
    }
    
    updateSortIndicator() {
        // Remove existing indicators
        const existingIndicators = this.sortDropdown.querySelectorAll('.sort-indicator');
        existingIndicators.forEach(indicator => indicator.remove());
        
        // Add new indicator to selected option
        const selectedOption = this.sortDropdown.options[this.sortDropdown.selectedIndex];
        selectedOption.textContent = selectedOption.textContent.replace(/ ↑| ↓/g, '');
        selectedOption.textContent += this.sortDirection === 'asc' ? ' ↑' : ' ↓';
    }
    
    refreshSort() {
        this.applySort(this.currentSort, this.sortDirection);
    }
    
}

// ===== CATEGORY FILTER FUNCTIONALITY =====
class CategoryFilter {
    constructor() {
        this.categoryDropdown = document.getElementById('categoryFilter'); // Updated
        this.init();
    }
    
    init() {
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        this.categoryDropdown.addEventListener('change', (e) => {
            this.handleCategoryFilter(e.target.value);
        });
    }
    
    handleCategoryFilter(category) {
    const opportunities = document.querySelectorAll('.opp-card');
    let visibleCount = 0;

    opportunities.forEach(opp => {
        let shouldShow = true;

        if (category && category !== '') {
            switch(category) {
                case 'internship':
                    shouldShow = this.isInternship(opp);
                    break;
                case 'research':
                    shouldShow = this.isResearch(opp);
                    break;
                case 'part-time':
                    shouldShow = this.isPartTime(opp);
                    break;
            }
        }

        opp.style.display = shouldShow ? 'block' : 'none';
        if (shouldShow) visibleCount++;
    });

    this.updateResultsDisplay(visibleCount);
    this.handleSearchAndFilterCombination();
}
    
    isInternship(opp) {
        const title = opp.querySelector('.opp-header h3')?.textContent.toLowerCase() || '';
        const desc = opp.querySelector('.opp-desc')?.textContent.toLowerCase() || '';
        
        return title.includes('intern') || 
               title.includes('internship') || 
               desc.includes('intern') ||
               desc.includes('internship');
    }
    
    isResearch(opp) {
        const title = opp.querySelector('.opp-header h3')?.textContent.toLowerCase() || '';
        const desc = opp.querySelector('.opp-desc')?.textContent.toLowerCase() || '';
        const org = opp.querySelector('.opp-org')?.textContent.toLowerCase() || '';
        
        return title.includes('research') || 
               title.includes('assistant') ||
               desc.includes('research') ||
               desc.includes('data analysis') ||
               org.includes('research') ||
               org.includes('lab');
    }
    
    isPartTime(opp) {
        const title = opp.querySelector('.opp-header h3')?.textContent.toLowerCase() || '';
        const desc = opp.querySelector('.opp-desc')?.textContent.toLowerCase() || '';
        
        return title.includes('part-time') || 
               title.includes('part time') ||
               desc.includes('part-time') ||
               desc.includes('part time') ||
               desc.includes('flexible hours') ||
               desc.includes('20 hours') ||
               desc.includes('15-20 hours');
    }
    
    updateResultsDisplay(visibleCount) {
        const resultsCount = document.getElementById('resultsCount');
        const noResults = document.getElementById('noResults');
        const opportunityGrid = document.getElementById('opportunityGrid');
        const searchResultsInfo = document.getElementById('searchResultsInfo');

        resultsCount.textContent = visibleCount;

        if (visibleCount === 0) {
            noResults.style.display = 'block';
            opportunityGrid.style.display = 'none';
        } else {
            noResults.style.display = 'none';
            opportunityGrid.style.display = 'grid';
        }

        // Show results info when filtered
        if (this.categoryDropdown.value !== 'All Categories') {
            searchResultsInfo.style.display = 'block';
        }
    }
    
    handleSearchAndFilterCombination() {
        const searchInput = document.querySelector('.search-box input');
        const searchTerm = searchInput.value.trim();
        
        if (searchTerm) {
            const searchEvent = new Event('input', { bubbles: true });
            searchInput.dispatchEvent(searchEvent);
        }
        
        // Refresh sorting if needed
        if (window.opportunitySorterInstance) {
            window.opportunitySorterInstance.refreshSort();
        }
    }
    
    clearCategoryFilter() {
        this.categoryDropdown.value = '';
        const opportunities = document.querySelectorAll('.opp-card');
        opportunities.forEach(opp => {
            opp.style.display = 'block';
        });
        
        const searchResultsInfo = document.getElementById('searchResultsInfo');
        searchResultsInfo.style.display = 'none';
    }
}

// ===== PROFESSIONAL ORGANIZATION MULTI-SELECT FUNCTIONALITY =====
class OrganizationFilter {
    constructor() {
        this.organizationSelect = document.querySelector('.organization-multi-select');
        this.selectHeader = this.organizationSelect.querySelector('.select-header');
        this.selectDropdown = this.organizationSelect.querySelector('.select-dropdown');
        this.orgSearch = this.organizationSelect.querySelector('.org-search');
        this.orgOptions = this.organizationSelect.querySelectorAll('.org-option input');
        this.selectedOrgsContainer = this.organizationSelect.querySelector('.selected-orgs');
        this.selectedOrganizations = new Set();
        
        this.init();
    }
    
    init() {
        this.attachEventListeners();
        this.updateVisualState();
    }
    
    attachEventListeners() {
        // Toggle dropdown
        this.selectHeader.addEventListener('click', (e) => {
            this.toggleDropdown();
        });
        
        // Search organizations
        this.orgSearch.addEventListener('input', (e) => {
            this.filterOrganizations(e.target.value);
        });
        
        // Organization selection
        this.orgOptions.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.handleOrganizationSelection(e.target);
            });
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.organizationSelect.contains(e.target)) {
                this.closeDropdown();
            }
        });
    }
    
    toggleDropdown() {
        if (this.selectDropdown.classList.contains('show')) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }
    
    openDropdown() {
        this.selectDropdown.classList.add('show');
        this.selectHeader.classList.add('active');
        this.orgSearch.focus();
    }
    
    closeDropdown() {
        this.selectDropdown.classList.remove('show');
        this.selectHeader.classList.remove('active');
        this.orgSearch.value = '';
        this.filterOrganizations(''); // Reset filter
    }
    
    filterOrganizations(searchTerm) {
        const term = searchTerm.toLowerCase();
        this.orgOptions.forEach(checkbox => {
            const orgName = checkbox.value.toLowerCase();
            const orgOption = checkbox.closest('.org-option');
            if (orgName.includes(term)) {
                orgOption.style.display = 'flex';
            } else {
                orgOption.style.display = 'none';
            }
        });
    }
    
    handleOrganizationSelection(checkbox) {
        const orgName = checkbox.value;
        
        if (checkbox.checked) {
            this.selectedOrganizations.add(orgName);
        } else {
            this.selectedOrganizations.delete(orgName);
        }
        
        this.updateSelectedOrgsDisplay();
        this.updateVisualState();
        this.applyOrganizationFilter();
    }
    
    updateSelectedOrgsDisplay() {
        this.selectedOrgsContainer.innerHTML = '';
        
        this.selectedOrganizations.forEach(orgName => {
            const chip = document.createElement('div');
            chip.className = 'org-chip';
            chip.innerHTML = `
                ${orgName}
                <button class="remove-chip" data-org="${orgName}">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            `;
            this.selectedOrgsContainer.appendChild(chip);
        });
        
        // Add remove chip functionality
        this.selectedOrgsContainer.querySelectorAll('.remove-chip').forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const orgName = button.getAttribute('data-org');
                this.removeOrganization(orgName);
            });
        });
    }
    
    removeOrganization(orgName) {
        this.selectedOrganizations.delete(orgName);
        
        // Uncheck the corresponding checkbox
        this.orgOptions.forEach(checkbox => {
            if (checkbox.value === orgName) {
                checkbox.checked = false;
            }
        });
        
        this.updateSelectedOrgsDisplay();
        this.updateVisualState();
        this.applyOrganizationFilter();
    }
    
    updateVisualState() {
        if (this.selectedOrganizations.size > 0) {
            this.selectHeader.style.borderColor = '#00c6ff';
            this.selectHeader.style.backgroundColor = '#f0f9ff';
        } else {
            this.selectHeader.style.borderColor = '';
            this.selectHeader.style.backgroundColor = '';
        }
    }
    
    applyOrganizationFilter() {
        const opportunities = document.querySelectorAll('.opp-card');
        let visibleCount = 0;

        opportunities.forEach(opp => {
            let shouldShow = true;

            if (this.selectedOrganizations.size > 0) {
                const oppOrg = opp.querySelector('.opp-org')?.textContent || '';
                if (!this.selectedOrganizations.has(oppOrg)) {
                    shouldShow = false;
                }
            }

            opp.style.display = shouldShow ? 'block' : 'none';
            if (shouldShow) visibleCount++;
        });

        this.updateResultsDisplay(visibleCount);
        this.handleSearchAndFilterCombination();
    }
    
    updateResultsDisplay(visibleCount) {
        const resultsCount = document.getElementById('resultsCount');
        const noResults = document.getElementById('noResults');
        const opportunityGrid = document.getElementById('opportunityGrid');
        const searchResultsInfo = document.getElementById('searchResultsInfo');

        resultsCount.textContent = visibleCount;

        if (visibleCount === 0) {
            noResults.style.display = 'block';
            opportunityGrid.style.display = 'none';
        } else {
            noResults.style.display = 'none';
            opportunityGrid.style.display = 'grid';
        }

        // Show results info when filtered
        if (this.selectedOrganizations.size > 0) {
            searchResultsInfo.style.display = 'block';
        }
    }
    
    handleSearchAndFilterCombination() {
        const searchInput = document.querySelector('.search-box input');
        const searchTerm = searchInput.value.trim();
        
        if (searchTerm) {
            const searchEvent = new Event('input', { bubbles: true });
            searchInput.dispatchEvent(searchEvent);
        }
        
        if (window.opportunitySorterInstance) {
            window.opportunitySorterInstance.refreshSort();
        }
    }
    
    clearOrganizationFilter() {
        this.selectedOrganizations.clear();
        this.orgOptions.forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateSelectedOrgsDisplay();
        this.updateVisualState();
        this.applyOrganizationFilter();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.opportunitySearchInstance = new OpportunitySearch();
    window.deadlineFilterInstance = new DeadlineFilter(); 
    window.typeFilterInstance = new TypeFilter();
    window.opportunitySorterInstance = new OpportunitySorter();
    window.categoryFilterInstance = new CategoryFilter();
    window.organizationFilterInstance = new OrganizationFilter(); 

    const avatar = document.getElementById('profileAvatar');
    const menu = document.getElementById('profileMenu');
    avatar.addEventListener('click', () => { 
        menu.parentElement.classList.toggle('show'); 
    });
    
    window.addEventListener('click', (e) => {
        if (!avatar.contains(e.target) && !menu.contains(e.target)) { 
            menu.parentElement.classList.remove('show'); 
        }
    });
});
