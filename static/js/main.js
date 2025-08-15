// Chat Widget with Bootstrap Modal
(function() {
  // Private variables
  let isInitialized = false;
  let elements = {};
  
  // Private methods
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
  
  function formatMessage(message) {
    // Simple URL to link conversion
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return escapeHtml(message)
      .replace(urlRegex, url => {
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
      })
      .replace(/\n/g, '<br>');
  }
  
  function scrollToBottom() {
    if (elements.chatMessages) {
      elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }
  }
  
  function showTypingIndicator() {
    if (elements.typingIndicator) {
      elements.typingIndicator.style.display = 'block';
      scrollToBottom();
    }
  }
  
  function hideTypingIndicator() {
    if (elements.typingIndicator) {
      elements.typingIndicator.style.display = 'none';
    }
  }
  
  function addUserMessage(message) {
    if (!elements.chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message mb-3';
    messageDiv.innerHTML = `
      <div class="message-content">
        <p>${escapeHtml(message)}</p>
        <small class="message-time">Just now</small>
      </div>
      <div class="message-avatar">
        <i class="bi bi-person"></i>
      </div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();
  }
  
  function addBotMessage(message) {
    if (!elements.chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message mb-3';
    messageDiv.innerHTML = `
      <div class="message-avatar">
        <i class="bi bi-robot"></i>
      </div>
      <div class="message-content">
        <p>${formatMessage(message)}</p>
        <small class="message-time">Just now</small>
      </div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();
  }
  
  async function handleSendMessage() {
    if (!elements.userInput) {
      console.error('User input element not found');
      return;
    }
    
    const userMessage = elements.userInput.value.trim();
    if (!userMessage) return;
    
    try {
      // Add user message to chat
      addUserMessage(userMessage);
      elements.userInput.value = '';
      elements.userInput.style.height = 'auto'; // Reset textarea height
      
      // Show typing indicator
      showTypingIndicator();
      
          // Get CSRF token from cookie or meta tag
      function getCSRFToken() {
        // First try to get from meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
          return metaTag.getAttribute('content');
        }
        
        // Then try to get from cookie
        const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
        if (cookieMatch) {
          return cookieMatch[1];
        }
        
        return null;
      }
      
      const csrftoken = getCSRFToken();
      
      if (!csrftoken) {
        console.error('CSRF token not found');
        hideTypingIndicator();
        addBotMessage("We're having trouble connecting to the server. Please refresh the page and try again.");
        return;
      }
      
      console.log('Sending message to server...');
      
      try {
        // Send message to server as JSON
        const response = await fetch('/chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify({ message: userMessage }),
          credentials: 'same-origin' // Include cookies in the request
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Server error:', errorText);
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.response) {
          // Simulate typing delay
          setTimeout(() => {
            hideTypingIndicator();
            addBotMessage(data.response);
          }, 800);
        } else {
          throw new Error('No response from server');
        }
      } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addBotMessage("Sorry, I'm having trouble connecting to the chat service. Please try again later or contact us directly at onpointinfo635@gmail.com");
      }
    } catch (error) {
      console.error('Chat error:', error);
      hideTypingIndicator();
      addBotMessage("I'm having trouble connecting to the server. Please try again later or contact us at onpointinfo635@gmail.com");
    }
  }
  
  // Public API
  return {
    init: function() {
      if (isInitialized) return;
      
      console.log('Initializing chat widget...');
      
      try {
        // Initialize elements
        elements = {
          chatModal: new bootstrap.Modal(document.getElementById('chatModal')),
          chatToggle: document.getElementById('chatToggle'),
          chatMessages: document.getElementById('chatMessages'),
          userInput: document.getElementById('userInput'),
          sendButton: document.getElementById('sendButton'),
          typingIndicator: document.getElementById('typingIndicator')
        };
        
        // Verify all required elements exist
        if (!elements.chatModal || !elements.chatToggle || !elements.chatMessages || 
            !elements.userInput || !elements.sendButton || !elements.typingIndicator) {
          console.error('Missing required chat widget elements');
          return;
        }
        
        // Initialize modal events
        elements.chatToggle.addEventListener('click', () => {
          elements.chatModal.show();
          // Focus input after modal is shown
          setTimeout(() => elements.userInput?.focus(), 500);
        });
        
    }

    if (elements.userInput) {
      elements.userInput.value = message;
      handleSendMessage();
    }
  },
  isInitialized: function() {
    return isInitialized;
  }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  // DOMContentLoaded has already fired
  setTimeout(initialize, 0);
}

// Initialize when window loads
window.addEventListener('load', function() {
  console.log('Window fully loaded - initializing chat widget');
  // Check for required elements
  function checkElements() {
    const requiredElements = [
      'chatModal', 'chatToggle', 'chatMessages', 
      'userInput', 'sendButton', 'typingIndicator'
    ];
    
    const elements = {};
    const missing = [];
    
    requiredElements.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        elements[id] = el;
      } else {
        missing.push(id);
      }
    });
    
    return { elements, missing };
  }
  
  // Initialize chat widget with retry logic
  function initChatWidget(retryCount = 0) {
    const maxRetries = 5;
    const retryDelay = 300; // ms
    
    try {
      console.log(`Initializing chat widget, attempt ${retryCount + 1}...`);
      
      // Check for required elements
      const { elements, missing } = checkElements();
      
      if (missing.length > 0) {
        console.warn('Missing required elements:', missing);
        if (retryCount < maxRetries) {
          console.log(`Retrying in ${retryDelay}ms... (${retryCount + 1}/${maxRetries})`);
          return setTimeout(() => initChatWidget(retryCount + 1), retryDelay);
        }
        console.error('Max retries reached. Chat widget initialization failed.');
        return;
      }
      
      // Initialize chat widget if available
      if (typeof chatWidget !== 'undefined') {
        console.log('All elements found, initializing chat widget...');
        chatWidget.init();
        console.log('Chat widget initialized successfully');
      } else {
        console.error('chatWidget is not defined');
        if (retryCount < maxRetries) {
          console.log(`Retrying in ${retryDelay}ms... (${retryCount + 1}/${maxRetries})`);
          setTimeout(() => initChatWidget(retryCount + 1), retryDelay);
        }
      }
    } catch (error) {
      console.error('Error initializing chat widget:', error);
      if (retryCount < maxRetries) {
        console.log(`Retrying after error in ${retryDelay}ms... (${retryCount + 1}/${maxRetries})`);
        setTimeout(() => initChatWidget(retryCount + 1), retryDelay);
      }
    }
  }
  
  // Start initialization
  initChatWidget();
  
  // Also try to initialize when DOM is fully loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      console.log('DOM fully loaded - initializing chat widget');
      initChatWidget();
    });
  } else {
    // DOMContentLoaded has already fired
    console.log('DOM already loaded - initializing chat widget');
    initChatWidget();
  }
  
  // Header sticky effect
  const header = document.getElementById('siteHeader');
  const onScroll = () => {
    if (window.scrollY > 60) header.classList.add('scrolled');
    else header.classList.remove('scrolled');
  };
  onScroll();
  window.addEventListener('scroll', onScroll);

  // Year
  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Price Calculator - Startup Friendly Kenya Prices
  const priceCalculator = {
    basePrices: {
      website: 15000,     // KES - Basic website for startups
      webapp: 40000,      // KES - Web application for startups
      mobile: 20000,     // KES - Mobile app development
      ecommerce: 50000,  // KES - Basic e-commerce site
      custom: 50000      // KES - Custom software solutions
    },
    
    complexityMultiplier: {
      basic: 0.8,      // 20% discount for basic projects
      standard: 1,     // Standard pricing
      premium: 1.5     // 50% premium for complex projects
    },
    
    pagePrice: 2000,   // KES per page after first 3 pages (startup friendly)
    
    featurePrices: {
      seo: 5000,      // KES - Basic SEO package
      responsive: 5000, // KES - Included in most packages
      cms: 25000,      // KES - Content Management System
      ecommerce: 50000 // KES - E-commerce functionality
    },
    
    // Special startup discount (percentage)
    startupDiscount: 0.15,  // 15% discount for startups
    
    calculate: function() {
      // Get selected values
      const projectType = document.getElementById('projectType').value;
      const pageCount = parseInt(document.getElementById('pageCount').value);
      const complexity = document.getElementById('designComplexity').value;
      
      // Calculate base price
      let total = this.basePrices[projectType] || 0;
      
      // Add pages cost (capped at 50 pages)
      const pages = Math.min(pageCount, 50);
      total += (pages - 5) * this.pagePrice; // First 5 pages included in base price
      
      // Apply complexity multiplier
      total *= this.complexityMultiplier[complexity] || 1;
      
      // Add features
      if (document.getElementById('featureSeo').checked) total += this.featurePrices.seo;
      if (document.getElementById('featureResponsive').checked) total += this.featurePrices.responsive;
      if (document.getElementById('featureCms').checked) total += this.featurePrices.cms;
      if (document.getElementById('featureEcommerce').checked) total += this.featurePrices.ecommerce;
      
      // Apply startup discount
      const discountedTotal = total * (1 - this.startupDiscount);
      
      // Update UI with KES formatting
      const formattedTotal = new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES',
        maximumFractionDigits: 0
      }).format(discountedTotal);
      
      document.getElementById('totalCost').innerHTML = `
        ${formattedTotal} 
        <small class="text-success d-block mt-1">
          <i class="bi bi-stars me-1"></i> 15% startup discount applied
        </small>
      `;
    },
    
    init: function() {
      // Update page count display
      const pageCount = document.getElementById('pageCount');
      const pageCountValue = document.getElementById('pageCountValue');
      
      if (pageCount && pageCountValue) {
        pageCount.addEventListener('input', () => {
          pageCountValue.textContent = pageCount.value;
          this.calculate();
        });
      }
      
      // Add event listeners
      const inputs = document.querySelectorAll('#projectType, #designComplexity, .form-check-input');
      inputs.forEach(input => {
        input.addEventListener('change', () => this.calculate());
      });
      
      // Initial calculation
      this.calculate();
      
      // Get Quote button
      const getQuoteBtn = document.getElementById('getQuoteBtn');
      if (getQuoteBtn) {
        getQuoteBtn.addEventListener('click', () => {
          // Scroll to contact form
          document.getElementById('contact').scrollIntoView({ behavior: 'smooth' });
        });
      }
    }
  };

  priceCalculator.init();

  // AOS
  if (window.AOS) AOS.init({ once: true, duration: 700, offset: 80 });

  // Swiper for testimonials
  if (window.Swiper) {
    new Swiper('.swiper', {
      slidesPerView: 1,
      spaceBetween: 24,
      pagination: { el: '.swiper-pagination', clickable: true },
      breakpoints: { 768: { slidesPerView: 2 }, 1200: { slidesPerView: 3 } },
      autoplay: { delay: 4500 },
      loop: true,
    });
  }

  // Animated counters
  document.querySelectorAll('[data-counter]').forEach(el => {
    const target = Number(el.getAttribute('data-target')) || 0;
    const duration = 1400;
    const start = performance.now();

    const step = (now) => {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.floor(eased * target).toLocaleString();
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });

  // Smooth scroll for nav links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id.length > 1) {
        e.preventDefault();
        document.querySelector(id)?.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
});
