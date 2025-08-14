// Chat Widget with Bootstrap Modal
const chatWidget = {
  init() {
    this.elements = {
      chatModal: new bootstrap.Modal(document.getElementById('chatModal')),
      chatToggle: document.getElementById('chatToggle'),
      chatMessages: document.getElementById('chatMessages'),
      userInput: document.getElementById('userInput'),
      sendButton: document.getElementById('sendButton'),
      typingIndicator: document.getElementById('typingIndicator')
    };
    
    // Initialize modal events
    this.initModalEvents();
    
    // Initialize chat toggle button
    if (this.elements.chatToggle) {
      this.elements.chatToggle.addEventListener('click', () => {
        this.elements.chatModal.show();
        // Focus input after modal is shown
        setTimeout(() => this.elements.userInput?.focus(), 500);
      });
    }
    
    // Send message on button click or Enter key
    if (this.elements.sendButton) {
      this.elements.sendButton.addEventListener('click', () => this.handleSendMessage());
    }
    
    if (this.elements.userInput) {
      this.elements.userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') this.handleSendMessage();
      });
      
      // Auto-resize textarea
      this.elements.userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
      });
    }
  },
  
  initModalEvents() {
    // Focus input when modal is shown
    const modal = document.getElementById('chatModal');
    if (modal) {
      modal.addEventListener('shown.bs.modal', () => {
        this.elements.userInput?.focus();
      });
    }
  },
  
  async handleSendMessage() {
    if (!this.elements.userInput) return;
    
    const userMessage = this.elements.userInput.value.trim();
    if (!userMessage) return;
    
    // Add user message to chat
    this.addUserMessage(userMessage);
    this.elements.userInput.value = '';
    this.elements.userInput.style.height = 'auto'; // Reset textarea height
    
    // Show typing indicator
    this.showTypingIndicator();
    
    try {
      // Send message to server
      const response = await fetch('/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: `message=${encodeURIComponent(userMessage)}`
      });
      
      const data = await response.json();
      
      if (data.response) {
        // Simulate typing delay
        setTimeout(() => {
          this.hideTypingIndicator();
          this.addBotMessage(data.response);
        }, 800);
      } else {
        throw new Error('No response from server');
      }
    } catch (error) {
      console.error('Error:', error);
      this.hideTypingIndicator();
      this.addBotMessage("I'm sorry, I'm having trouble connecting to the server. Please try again later or contact us directly at onpointinfo635@gmail.com");
    }
  },
  
  addUserMessage(message) {
    if (!this.elements.chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message mb-3';
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
      <div class="message-avatar">
        <i class="bi bi-person"></i>
      </div>
      <div class="message-content">
        <p class="mb-1">${this.escapeHtml(message)}</p>
        <small class="message-time text-muted">${time}</small>
      </div>
    `;
    
    this.elements.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
  },
  
  addBotMessage(message) {
    if (!this.elements.chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message mb-3';
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
      <div class="message-avatar">
        <i class="bi bi-robot"></i>
      </div>
      <div class="message-content">
        <p class="mb-1">${this.formatMessage(message)}</p>
        <small class="message-time text-muted">${time}</small>
      </div>
    `;
    
    this.elements.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
  },
  
  formatMessage(message) {
    // Convert markdown to HTML
    return this.escapeHtml(message)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="text-primary">$1</a>');
  },
  
  escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },
  
  showTypingIndicator() {
    if (this.elements.typingIndicator) {
      this.elements.typingIndicator.style.display = 'block';
      this.scrollToBottom();
    }
  },
  
  hideTypingIndicator() {
    if (this.elements.typingIndicator) {
      this.elements.typingIndicator.style.display = 'none';
    }
  },
  
  scrollToBottom() {
    if (this.elements.chatMessages) {
      this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
  },
  
  getCookie(name) {
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
};

document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM fully loaded');
  
  // Debug: Log chat widget elements
  console.log('Chat widget element:', document.querySelector('.chat-widget'));
  console.log('Chat toggle button:', document.getElementById('chatToggle'));
  
  // Initialize chat widget
  try {
    chatWidget.init();
    console.log('Chat widget initialized');
  } catch (error) {
    console.error('Error initializing chat widget:', error);
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
