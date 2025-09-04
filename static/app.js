// Main JavaScript file for Coupon Tracker Application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Initialize components
    initializeComponents();
    
    // Load initial data if needed
    loadInitialData();
}

function setupEventListeners() {
    // Navigation menu toggle for mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    
    if (menuToggle && nav) {
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
        });
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });

    // Search functionality
    const searchInput = document.querySelector('#search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }

    // Filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', handleFilter);
    });

    // Modal functionality
    setupModals();
}

function initializeComponents() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize copy-to-clipboard functionality
    initializeCopyButtons();
    
    // Initialize date pickers
    initializeDatePickers();
    
    // Initialize sortable tables
    initializeSortableTables();
}

function loadInitialData() {
    // Load coupon statistics
    loadCouponStats();
    
    // Load recent activity
    loadRecentActivity();
}

// Form handling
function handleFormSubmit(event) {
    const form = event.target;
    
    // Basic validation
    if (!validateForm(form)) {
        event.preventDefault();
        return false;
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        showLoadingState(submitBtn);
    }
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    // Date validation
    const dateFields = form.querySelectorAll('input[type="date"]');
    dateFields.forEach(field => {
        if (field.value && new Date(field.value) < new Date()) {
            showFieldError(field, 'Date cannot be in the past');
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
}

function clearFieldError(field) {
    field.classList.remove('error');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Search functionality
function handleSearch(event) {
    const query = event.target.value.toLowerCase();
    const items = document.querySelectorAll('.coupon-item, .table tbody tr');
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const shouldShow = text.includes(query);
        item.style.display = shouldShow ? '' : 'none';
    });
    
    updateSearchResults(query);
}

function updateSearchResults(query) {
    const resultCount = document.querySelectorAll('.coupon-item:not([style*="display: none"]), .table tbody tr:not([style*="display: none"])').length;
    const resultDiv = document.querySelector('#search-results');
    
    if (resultDiv) {
        if (query) {
            resultDiv.textContent = `${resultCount} results found for "${query}"`;
            resultDiv.style.display = 'block';
        } else {
            resultDiv.style.display = 'none';
        }
    }
}

// Filter functionality
function handleFilter(event) {
    const filterBtn = event.target;
    const filterType = filterBtn.dataset.filter;
    const filterValue = filterBtn.dataset.value;
    
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    filterBtn.classList.add('active');
    
    // Apply filter
    applyFilter(filterType, filterValue);
}

function applyFilter(type, value) {
    const items = document.querySelectorAll('.coupon-item, .table tbody tr');
    
    items.forEach(item => {
        let shouldShow = true;
        
        if (value !== 'all') {
            switch (type) {
                case 'status':
                    const statusElement = item.querySelector('.status-badge, .status');
                    shouldShow = statusElement && statusElement.textContent.toLowerCase().includes(value);
                    break;
                case 'type':
                    const typeElement = item.querySelector('.coupon-type, [data-type]');
                    shouldShow = typeElement && typeElement.textContent.toLowerCase().includes(value);
                    break;
                default:
                    shouldShow = true;
            }
        }
        
        item.style.display = shouldShow ? '' : 'none';
    });
}

// Modal functionality
function setupModals() {
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const modals = document.querySelectorAll('.modal');
    const closeBtns = document.querySelectorAll('.modal-close, .close');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.dataset.modal;
            const modal = document.getElementById(modalId);
            if (modal) {
                openModal(modal);
            }
        });
    });
    
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                closeModal(modal);
            }
        });
    });
    
    // Close modal on backdrop click
    modals.forEach(modal => {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });
}

function openModal(modal) {
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Focus trap
    const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusableElements.length) {
        focusableElements[0].focus();
    }
}

function closeModal(modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
}

// Copy to clipboard functionality
function initializeCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn, [data-copy]');
    
    copyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const textToCopy = this.dataset.copy || this.textContent;
            copyToClipboard(textToCopy);
        });
    });
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        showNotification('Failed to copy to clipboard', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Notification system
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    // Add to container or create one
    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto remove
    const removeNotification = () => {
        notification.classList.add('notification-exit');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    };
    
    // Close button
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', removeNotification);
    
    // Auto-remove after duration
    setTimeout(removeNotification, duration);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('notification-enter');
    }, 10);
}

// Tooltip functionality
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
        element.addEventListener('focus', showTooltip);
        element.addEventListener('blur', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.dataset.tooltip;
    
    if (!tooltipText) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = tooltipText;
    tooltip.id = 'active-tooltip';
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltipRect.width / 2) + 'px';
    tooltip.style.top = rect.top - tooltipRect.height - 10 + 'px';
    
    // Show tooltip
    setTimeout(() => {
        tooltip.classList.add('show');
    }, 10);
}

function hideTooltip() {
    const tooltip = document.getElementById('active-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Date picker initialization
function initializeDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Set minimum date to today for expiry dates
        if (input.name.includes('expiry') || input.classList.contains('future-date')) {
            const today = new Date().toISOString().split('T')[0];
            input.min = today;
        }
    });
}

// Sortable tables
function initializeSortableTables() {
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    
    sortableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            sortTable(this);
        });
    });
}

function sortTable(header) {
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const column = Array.from(header.parentNode.children).indexOf(header);
    const currentDirection = header.dataset.sortDirection || 'asc';
    const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
    
    // Clear other sort indicators
    table.querySelectorAll('th[data-sort]').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add sort indicator
    header.classList.add(`sort-${newDirection}`);
    header.dataset.sortDirection = newDirection;
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.children[column].textContent.trim();
        const bValue = b.children[column].textContent.trim();
        
        let comparison = 0;
        
        // Try to parse as numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            comparison = aNum - bNum;
        } else {
            // String comparison
            comparison = aValue.localeCompare(bValue);
        }
        
        return newDirection === 'asc' ? comparison : -comparison;
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// Loading state management
function showLoadingState(element) {
    element.disabled = true;
    element.dataset.originalText = element.textContent;
    element.innerHTML = '<span class="spinner"></span> Loading...';
}

function hideLoadingState(element) {
    element.disabled = false;
    element.textContent = element.dataset.originalText || 'Submit';
}

// Statistics loading
function loadCouponStats() {
    const statsContainer = document.querySelector('.stats-grid');
    if (!statsContainer) return;
    
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateStats(data);
        })
        .catch(error => {
            console.error('Failed to load stats:', error);
        });
}

function updateStats(stats) {
    const statElements = {
        'total-coupons': stats.totalCoupons,
        'active-coupons': stats.activeCoupons,
        'total-claims': stats.totalClaims,
        'total-savings': stats.totalSavings
    };
    
    Object.entries(statElements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            animateCounter(element, value);
        }
    });
}

function animateCounter(element, targetValue) {
    const startValue = parseInt(element.textContent.replace(/[^0-9]/g, '')) || 0;
    const duration = 1000;
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
        
        // Format the value
        if (element.id === 'total-savings') {
            element.textContent = ' + currentValue.toLocaleString();
        } else {
            element.textContent = currentValue.toLocaleString();
        }
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Recent activity loading
function loadRecentActivity() {
    const activityContainer = document.querySelector('.recent-activity');
    if (!activityContainer) return;
    
    fetch('/api/recent-activity')
        .then(response => response.json())
        .then(data => {
            updateRecentActivity(data);
        })
        .catch(error => {
            console.error('Failed to load recent activity:', error);
        });
}

function updateRecentActivity(activities) {
    const activityList = document.querySelector('.activity-list');
    if (!activityList) return;
    
    activityList.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon ${activity.type}">
                ${getActivityIcon(activity.type)}
            </div>
            <div class="activity-content">
                <p class="activity-message">${activity.message}</p>
                <span class="activity-time">${formatTime(activity.timestamp)}</span>
            </div>
        </div>
    `).join('');
}

function getActivityIcon(type) {
    const icons = {
        'claim': '🎫',
        'create': '➕',
        'expire': '⏰',
        'delete': '🗑️',
        'edit': '✏️'
    };
    return icons[type] || '📝';
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    return `${Math.floor(diffInSeconds / 86400)} days ago`;
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// API helpers
function makeApiCall(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    if (mergedOptions.body && typeof mergedOptions.body === 'object') {
        mergedOptions.body = JSON.stringify(mergedOptions.body);
    }
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Export functions for global access
window.CouponTracker = {
    showNotification,
    copyToClipboard,
    openModal,
    closeModal,
    showLoadingState,
    hideLoadingState,
    makeApiCall,
    validateForm
};

// Admin-specific functions
function deleteCoupon(couponId) {
    if (confirm('Are you sure you want to delete this coupon? This action cannot be undone.')) {
        makeApiCall(`/api/coupons/${couponId}`, { method: 'DELETE' })
            .then(data => {
                showNotification('Coupon deleted successfully', 'success');
                // Remove the row from the table
                const row = document.querySelector(`[data-coupon-id="${couponId}"]`);
                if (row) {
                    row.remove();
                }
            })
            .catch(error => {
                showNotification('Failed to delete coupon', 'error');
            });
    }
}

function toggleCouponStatus(couponId, currentStatus) {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
    
    makeApiCall(`/api/coupons/${couponId}/status`, {
        method: 'PATCH',
        body: { status: newStatus }
    })
        .then(data => {
            showNotification(`Coupon ${newStatus}`, 'success');
            // Update the status badge
            const statusBadge = document.querySelector(`[data-coupon-id="${couponId}"] .status-badge`);
            if (statusBadge) {
                statusBadge.textContent = newStatus;
                statusBadge.className = `status-badge ${newStatus}`;
            }
        })
        .catch(error => {
            showNotification('Failed to update coupon status', 'error');
        });
}

// Bulk operations
function selectAllCoupons() {
    const checkboxes = document.querySelectorAll('.coupon-checkbox');
    const selectAllCheckbox = document.getElementById('selectAll');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    
    updateBulkActions();
}

function updateBulkActions() {
    const checkedBoxes = document.querySelectorAll('.coupon-checkbox:checked');
    const bulkActions = document.querySelector('.bulk-actions');
    
    if (bulkActions) {
        bulkActions.style.display = checkedBoxes.length > 0 ? 'block' : 'none';
    }
}

function bulkDeleteCoupons() {
    const checkedBoxes = document.querySelectorAll('.coupon-checkbox:checked');
    const couponIds = Array.from(checkedBoxes).map(cb => cb.value);
    
    if (couponIds.length === 0) {
        showNotification('Please select coupons to delete', 'warning');
        return;
    }
    
    if (confirm(`Are you sure you want to delete ${couponIds.length} coupons? This action cannot be undone.`)) {
        makeApiCall('/api/coupons/bulk-delete', {
            method: 'POST',
            body: { couponIds }
        })
            .then(data => {
                showNotification(`${couponIds.length} coupons deleted successfully`, 'success');
                // Refresh the page or remove the rows
                location.reload();
            })
            .catch(error => {
                showNotification('Failed to delete coupons', 'error');
            });
    }
}

function bulkUpdateStatus(status) {
    const checkedBoxes = document.querySelectorAll('.coupon-checkbox:checked');
    const couponIds = Array.from(checkedBoxes).map(cb => cb.value);
    
    if (couponIds.length === 0) {
        showNotification('Please select coupons to update', 'warning');
        return;
    }
    
    makeApiCall('/api/coupons/bulk-status', {
        method: 'POST',
        body: { couponIds, status }
    })
        .then(data => {
            showNotification(`${couponIds.length} coupons updated successfully`, 'success');
            location.reload();
        })
        .catch(error => {
            showNotification('Failed to update coupons', 'error');
        });
}

// Export functions
function exportCoupons(format = 'csv') {
    const url = `/api/export/coupons?format=${format}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `coupons_export_${new Date().toISOString().split('T')[0]}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Export started', 'success');
}

// Real-time updates (if WebSocket is available)
function initializeWebSocket() {
    if (typeof WebSocket === 'undefined') return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'coupon_claimed':
            updateCouponUsage(data.couponId, data.newUsageCount);
            showNotification(`Coupon "${data.couponCode}" was just claimed!`, 'info');
            break;
        case 'coupon_expired':
            markCouponExpired(data.couponId);
            break;
        case 'stats_updated':
            updateStats(data.stats);
            break;
    }
}

function updateCouponUsage(couponId, newUsageCount) {
    const usageCell = document.querySelector(`[data-coupon-id="${couponId}"] .usage-count`);
    if (usageCell) {
        usageCell.textContent = newUsageCount;
        usageCell.classList.add('updated');
        setTimeout(() => usageCell.classList.remove('updated'), 2000);
    }
}

function markCouponExpired(couponId) {
    const statusBadge = document.querySelector(`[data-coupon-id="${couponId}"] .status-badge`);
    if (statusBadge) {
        statusBadge.textContent = 'expired';
        statusBadge.className = 'status-badge expired';
    }
}

// Initialize WebSocket if on admin page
if (window.location.pathname.includes('admin')) {
    initializeWebSocket();
}