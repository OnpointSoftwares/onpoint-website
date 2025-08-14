document.addEventListener('DOMContentLoaded', () => {
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

  // Price Calculator
  const priceCalculator = {
    basePrices: {
      website: 1000,
      webapp: 3000,
      mobile: 5000,
      ecommerce: 4000,
      custom: 6000
    },
    
    complexityMultiplier: {
      basic: 1,
      standard: 1.5,
      premium: 2.5
    },
    
    pagePrice: 50,
    
    featurePrices: {
      seo: 500,
      responsive: 300,
      cms: 1000,
      ecommerce: 2000
    },
    
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
      
      // Update UI
      document.getElementById('totalCost').textContent = total.toLocaleString();
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
