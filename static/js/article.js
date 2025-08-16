document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 600,
            easing: 'ease-in-out',
            once: true
        });
    }

    // Handle comment form submission
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Posting...';
            }
        });
    }

    // Handle reply functionality
    if (typeof setReplyTo === 'undefined') {
        window.setReplyTo = function(commentId, username) {
            const parentIdInput = document.getElementById('parent_id');
            const commentText = document.getElementById('comment-text');
            const cancelReplyBtn = document.getElementById('cancel-reply');
            
            if (parentIdInput && commentText && cancelReplyBtn) {
                parentIdInput.value = commentId;
                commentText.focus();
                cancelReplyBtn.classList.remove('d-none');
                
                // Smooth scroll to comment form
                document.getElementById('comment-form').scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Add mention to comment text
                commentText.value = `@${username} `;
            }
            
            // Hide any other open reply forms
            document.querySelectorAll('.reply-form').forEach(form => {
                if (form.id !== `reply-form-${commentId}`) {
                    form.classList.add('d-none');
                }
            });
            
            // Toggle the current reply form
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (replyForm) {
                replyForm.classList.toggle('d-none');
                if (!replyForm.classList.contains('d-none')) {
                    replyForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            }
        };
    }

    // Handle cancel reply
    if (typeof cancelReply === 'undefined') {
        window.cancelReply = function(commentId) {
            const parentIdInput = document.getElementById('parent_id');
            const cancelReplyBtn = document.getElementById('cancel-reply');
            
            if (parentIdInput) parentIdInput.value = '';
            if (cancelReplyBtn) cancelReplyBtn.classList.add('d-none');
            
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (replyForm) replyForm.classList.add('d-none');
            
            const commentText = document.getElementById('comment-text');
            if (commentText) commentText.value = '';
        };
    }

    // Handle cancel reply button
    const cancelReplyBtn = document.getElementById('cancel-reply');
    if (cancelReplyBtn) {
        cancelReplyBtn.addEventListener('click', function() {
            const parentIdInput = document.getElementById('parent_id');
            if (parentIdInput) parentIdInput.value = '';
            this.classList.add('d-none');
            
            const commentText = document.getElementById('comment-text');
            if (commentText) commentText.value = '';
            
            // Hide all reply forms
            document.querySelectorAll('.reply-form').forEach(form => {
                form.classList.add('d-none');
            });
        });
    }

    // Copy to clipboard functionality
    if (typeof copyToClipboard === 'undefined') {
        window.copyToClipboard = function(text, button) {
            navigator.clipboard.writeText(text).then(function() {
                // Change button icon to checkmark
                const icon = button.querySelector('i');
                const originalIcon = icon.className;
                
                icon.className = 'bi bi-check';
                button.setAttribute('data-bs-original-title', 'Copied!');
                const tooltip = bootstrap.Tooltip.getInstance(button);
                if (tooltip) {
                    tooltip._config.title = 'Copied!';
                    tooltip.show();
                }
                
                // Revert after 2 seconds
                setTimeout(function() {
                    icon.className = originalIcon;
                    button.setAttribute('data-bs-original-title', 'Copy link');
                    if (tooltip) {
                        tooltip._config.title = 'Copy link';
                    }
                }, 2000);
            }).catch(function(err) {
                console.error('Could not copy text: ', err);
            });
        };
    }

    // Handle table of contents generation
    const generateTableOfContents = () => {
        const tocContainer = document.getElementById('table-of-contents');
        const articleContent = document.querySelector('.article-content');
        
        if (!tocContainer || !articleContent) return;
        
        const headings = articleContent.querySelectorAll('h2, h3, h4');
        if (headings.length === 0) {
            tocContainer.style.display = 'none';
            return;
        }
        
        let tocHtml = '<h5 class="mb-3">Table of Contents</h5><nav class="nav flex-column">';
        let headingCount = 0;
        
        headings.forEach((heading, index) => {
            const level = parseInt(heading.tagName.substring(1)); // h2 -> 2, h3 -> 3, etc.
            const title = heading.textContent;
            const id = `heading-${++headingCount}`;
            
            // Add ID to heading for anchor links
            heading.setAttribute('id', id);
            
            // Add margin to headings for better spacing
            heading.style.scrollMarginTop = '80px';
            
            // Generate TOC item with proper indentation
            const indent = level === 2 ? '' : 'ms-3';
            tocHtml += `
                <a class="nav-link ps-2 py-1 ${indent} border-start border-3 border-transparent" 
                   href="#${id}" 
                   style="font-size: 0.9rem;">
                    ${title}
                </a>`;
        });
        
        tocHtml += '</nav>';
        tocContainer.innerHTML = tocHtml;
        
        // Add active class to TOC items on scroll
        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.5
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const id = entry.target.getAttribute('id');
                if (entry.isIntersecting && id) {
                    document.querySelectorAll('#table-of-contents .nav-link').forEach(link => {
                        link.classList.remove('active', 'border-primary');
                        if (link.getAttribute('href') === `#${id}`) {
                            link.classList.add('active', 'border-primary');
                        }
                    });
                }
            });
        }, observerOptions);
        
        headings.forEach(heading => {
            observer.observe(heading);
        });
    };
    
    // Generate table of contents if the element exists
    if (document.getElementById('table-of-contents')) {
        generateTableOfContents();
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const headerOffset = 90;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                
                // Update URL without page jump
                if (history.pushState) {
                    history.pushState(null, null, targetId);
                } else {
                    window.location.hash = targetId;
                }
            }
        });
    });
    
    // Handle back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Handle print button
    const printButton = document.getElementById('print-article');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }
    
    // Handle code block copy buttons
    document.querySelectorAll('.code-block').forEach(block => {
        const copyButton = block.querySelector('.copy-button');
        if (copyButton) {
            copyButton.addEventListener('click', function() {
                const code = block.querySelector('code');
                if (code) {
                    navigator.clipboard.writeText(code.textContent).then(() => {
                        const originalText = copyButton.innerHTML;
                        copyButton.innerHTML = '<i class="bi bi-check"></i> Copied!';
                        setTimeout(() => {
                            copyButton.innerHTML = originalText;
                        }, 2000);
                    });
                }
            });
        }
    });
});
