// Chat Widget with Bootstrap Modal
export const ChatWidget = (function() {
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
    messageDiv.className = 'd-flex justify-content-end mb-3';
    messageDiv.innerHTML = `
      <div class="bg-primary text-white p-3 rounded-3" style="max-width: 80%;">
        ${formatMessage(message)}
        <div class="text-end small mt-1">
          ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
        </div>
      </div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();
  }
  
  function addBotMessage(message) {
    if (!elements.chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'd-flex justify-content-start mb-3';
    messageDiv.innerHTML = `
      <div class="bg-light text-dark p-3 rounded-3" style="max-width: 80%;">
        ${formatMessage(message)}
        <div class="text-end small text-muted mt-1">
          ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
        </div>
      </div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();
  }
  
  async function handleSendMessage() {
    const userInput = elements.userInput;
    if (!userInput || !userInput.value.trim()) return;
    
    const message = userInput.value.trim();
    userInput.value = '';
    
    // Add user message to chat
    addUserMessage(message);
    showTypingIndicator();
    
    try {
      // Get CSRF token from window object or cookie
      let csrftoken = window.csrfToken || getCookie('csrftoken');
      
      if (!csrftoken) {
        // Last resort: try to get from meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
          csrftoken = metaTag.getAttribute('content');
        }
      }
      
      if (!csrftoken) {
        throw new Error('CSRF token not found. Please refresh the page and try again.');
      }
      
      // Ensure the token is a string and not empty
      csrftoken = String(csrftoken).trim();
      if (!csrftoken) {
        throw new Error('Invalid CSRF token. Please refresh the page and try again.');
      }
      
      // Ensure URL is properly initialized
      const chatApiUrl = (window.djangoUrls && window.djangoUrls.chatApi) || '/chat/';
      
      const response = await fetch(chatApiUrl, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ message: message })
      });
      
      if (!response.ok) {
        // Handle CSRF token mismatch specifically
        if (response.status === 403) {
          throw new Error('Session expired. Please refresh the page and try again.');
        }
        
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = { error: 'Invalid server response' };
        }
        const errorMessage = errorData.error || `Server responded with status ${response.status}`;
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      
      // Add bot response to chat
      if (data.response) {
        addBotMessage(data.response);
      } else {
        addBotMessage('I apologize, but I am having trouble processing your request.');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // More specific error messages
      if (error.message.includes('quota') || error.message.includes('API')) {
        addBotMessage(`⚠️ Our chat service is currently experiencing high demand. Please try again in a few minutes. If the issue persists, you can reach us directly at onpointinfo635@gmail.com`);
      } else if (error.message.includes('Network')) {
        addBotMessage('🔌 Unable to connect to the chat service. Please check your internet connection and try again.');
      } else {
        addBotMessage('⚠️ Sorry, there was an error processing your message. Please try again later or contact us at onpointinfo635@gmail.com');
      }
    } finally {
      hideTypingIndicator();
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
        
        // Initialize event listeners
        elements.chatToggle.addEventListener('click', () => {
          elements.chatModal.show();
          // Focus input after modal is shown
          setTimeout(() => elements.userInput?.focus(), 500);
        });
        
        elements.sendButton.addEventListener('click', handleSendMessage);
        
        elements.userInput.addEventListener('keypress', (e) => {
          if (e.key === 'Enter') {
            handleSendMessage();
          }
        });
        
        // Mark as initialized
        isInitialized = true;
        console.log('Chat widget initialized successfully');
        
        // Add welcome message
        setTimeout(() => {
          addBotMessage('Hello! How can I assist you today?');
        }, 1000);
        
      } catch (error) {
        console.error('Error initializing chat widget:', error);
      }
    },
    
    isInitialized: function() {
      return isInitialized;
    }
  };
})();

// Initialize chat widget when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize chat widget
  ChatWidget.init();
});
