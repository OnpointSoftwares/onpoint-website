// Import chat widget
import { ChatWidget } from './chat-widget.js';

// Main application initialization
document.addEventListener('DOMContentLoaded', function() {
  // Initialize chat widget
  ChatWidget.init();
  
  // Initialize price calculator
  const priceCalculator = {
    init: function() {
      const pageCount = document.getElementById('pageCount');
      const pageCountValue = document.getElementById('pageCountValue');
      const projectType = document.getElementById('projectType');
      const designComplexity = document.getElementById('designComplexity');
      const featureSeo = document.getElementById('featureSeo');
      const featureResponsive = document.getElementById('featureResponsive');
      const featureCms = document.getElementById('featureCms');
      const featureEcommerce = document.getElementById('featureEcommerce');
      const totalCostElement = document.getElementById('totalCost');
      const getQuoteBtn = document.getElementById('getQuoteBtn');

      // Base prices for different project types
      const basePrices = {
        website: 5000,
        webapp: 25000,
        mobile: 40000,
        ecommerce: 60000,
        custom: 75000
      };

      // Multipliers for design complexity
      const complexityMultipliers = {
        basic: 1,
        standard: 1.5,
        premium: 2.5
      };

      // Feature costs
      const featureCosts = {
        seo: 5000,
        responsive: 3000,
        cms: 10000,
        ecommerce: 15000
      };

      // Update page count display
      if (pageCount && pageCountValue) {
        pageCount.addEventListener('input', updateEstimate);
        pageCountValue.textContent = pageCount.value;
      }

      // Add event listeners
      if (projectType) projectType.addEventListener('change', updateEstimate);
      if (designComplexity) designComplexity.addEventListener('change', updateEstimate);
      if (featureSeo) featureSeo.addEventListener('change', updateEstimate);
      if (featureResponsive) featureResponsive.addEventListener('change', updateEstimate);
      if (featureCms) featureCms.addEventListener('change', updateEstimate);
      if (featureEcommerce) featureEcommerce.addEventListener('change', updateEstimate);
      if (getQuoteBtn) getQuoteBtn.addEventListener('click', handleGetQuote);

      // Initial calculation
      updateEstimate();

      function updateEstimate() {
        if (!pageCount || !totalCostElement) return;
        
        // Get values
        const pages = parseInt(pageCount.value) || 1;
        const project = projectType ? projectType.value : 'website';
        const complexity = designComplexity ? designComplexity.value : 'standard';
        
        // Calculate base price
        let basePrice = basePrices[project] || 10000;
        
        // Apply page multiplier (for websites)
        if (project === 'website') {
          basePrice += (pages - 1) * 1500;
        }
        
        // Apply complexity multiplier
        const complexityMultiplier = complexityMultipliers[complexity] || 1;
        let total = basePrice * complexityMultiplier;
        
        // Add feature costs
        if (featureSeo && featureSeo.checked) total += featureCosts.seo;
        if (featureResponsive && featureResponsive.checked) total += featureCosts.responsive;
        if (featureCms && featureCms.checked) total += featureCosts.cms;
        if (featureEcommerce && featureEcommerce.checked) total += featureCosts.ecommerce;
        
        // Apply startup discount (15%)
        const discount = total * 0.15;
        const finalPrice = total - discount;
        
        // Update page count display
        if (pageCountValue) {
          pageCountValue.textContent = pages;
        }
        
        // Update total cost display
        if (totalCostElement) {
          totalCostElement.innerHTML = `
            KES ${finalPrice.toLocaleString('en-US')}
            <small class="text-success d-block mt-1">
              <i class="bi bi-stars me-1"></i> 15% startup discount applied
            </small>
          `;
        }
      }

      function handleGetQuote(e) {
        e.preventDefault();
        // Collect form data
        const formData = {
          projectType: projectType ? projectType.value : 'website',
          pages: pageCount ? pageCount.value : 5,
          designComplexity: designComplexity ? designComplexity.value : 'standard',
          features: []
        };
        
        if (featureSeo && featureSeo.checked) formData.features.push('SEO Optimization');
        if (featureResponsive && featureResponsive.checked) formData.features.push('Responsive Design');
        if (featureCms && featureCms.checked) formData.features.push('Content Management');
        if (featureEcommerce && featureEcommerce.checked) formData.features.push('E-commerce');
        
        // In a real app, you would send this data to your server
        console.log('Quote requested:', formData);
        
        // For now, just show an alert
        alert('Thank you for your interest! Our team will contact you shortly with a detailed quote.');
        
        // You would typically redirect to a contact form or open a modal
        // window.location.href = '/contact/?quote=true';
      }
    }
  };
  
  priceCalculator.init();
  
  // Initialize AOS (Animate On Scroll) if available
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 800,
      easing: 'ease-in-out',
      once: true
    });
  }
  
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Update current year in footer
  const yearElement = document.getElementById('current-year');
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }
});
