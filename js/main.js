document.addEventListener('DOMContentLoaded', function() {
    // Inicializace mapy
    const mapElement = document.getElementById('map');
    if (mapElement) {
        const map = L.map('map').setView([50.4393953, 13.0545889], 14);

        // Přidání OpenStreetMap podkladu
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Přidání značky
        const marker = L.marker([50.4393953, 13.0545889])
            .addTo(map)
            .bindPopup('<strong>Aviatika - Horské apartmány</strong><br>nám. J. Švermy 71, Kovářská')
            .openPopup();
    }
    // Mobilní menu
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenuBtn.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
        
        // Zavření menu po kliknutí na odkaz
        const navLinksItems = document.querySelectorAll('.nav-links a');
        navLinksItems.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenuBtn.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
    }

    // Skrolování navigace
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll <= 0) {
            navbar.classList.remove('scroll-up');
            return;
        }

        if (currentScroll > lastScroll && !navbar.classList.contains('scroll-down')) {
            navbar.classList.remove('scroll-up');
            navbar.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && navbar.classList.contains('scroll-down')) {
            navbar.classList.remove('scroll-down');
            navbar.classList.add('scroll-up');
        }

        lastScroll = currentScroll;
    });

    // Galerie lightbox
    const galleryItems = document.querySelectorAll('.gallery-item');
    const body = document.body;

    galleryItems.forEach(item => {
        item.addEventListener('click', () => {
            const img = item.querySelector('img');
            const lightbox = document.createElement('div');
            lightbox.className = 'lightbox';
            
            const lightboxContent = document.createElement('div');
            lightboxContent.className = 'lightbox-content';
            
            const lightboxImg = document.createElement('img');
            lightboxImg.src = img.src;
            
            const closeBtn = document.createElement('button');
            closeBtn.className = 'lightbox-close';
            closeBtn.innerHTML = '&times;';
            
            lightboxContent.appendChild(lightboxImg);
            lightboxContent.appendChild(closeBtn);
            lightbox.appendChild(lightboxContent);
            body.appendChild(lightbox);
            
            setTimeout(() => lightbox.classList.add('active'), 10);
            
            const closeLightbox = () => {
                lightbox.classList.remove('active');
                setTimeout(() => lightbox.remove(), 300);
            };
            
            closeBtn.addEventListener('click', closeLightbox);
            lightbox.addEventListener('click', (e) => {
                if (e.target === lightbox) closeLightbox();
            });
        });
    });

    // Plynulé skrolování
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                // Scroll with offset for fixed navbar so target isn't hidden
                const yOffset = -((navbar?.offsetHeight) || 0) - 10; // extra margin
                const y = targetElement.getBoundingClientRect().top + window.pageYOffset + yOffset;
                window.scrollTo({ top: y, behavior: 'smooth' });
                
                // Zavřít mobilní menu po kliknutí na odkaz
                if (mobileMenuBtn?.classList.contains('active')) {
                    mobileMenuBtn.classList.remove('active');
                    navLinks.classList.remove('active');
                }
            }
        });
    });

    // FAQ-style apartmány (podpora pro .apartment-item i .apartment-type)
    const apartmentItems = document.querySelectorAll('.apartment-item, .apartment-type');

    apartmentItems.forEach(item => {
        const header = item.querySelector('.apartment-header');
        
        header?.addEventListener('click', () => {
            const currentlyActive = document.querySelector('.apartment-item.active, .apartment-type.active');
            
            if (currentlyActive && currentlyActive !== item) {
                currentlyActive.classList.remove('active');
            }
            
            item.classList.toggle('active');
        });
    });

    // Animace při skrolování
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.glass-card, .feature-card, .apartment-card, .gallery-item').forEach(element => {
        observer.observe(element);
    });

    // RealVisor – kontaktni-formu-07197
    (function() {
        const form = document.querySelector('#contact-form');
        if (!form) return;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const name = form.querySelector('[name="name"]').value.trim();
            const email = form.querySelector('[name="email"]').value.trim();
            const phone = form.querySelector('[name="phone"]').value.trim();
            const interest = form.querySelector('[name="interest"]').value;
            const message = form.querySelector('[name="message"]').value.trim();

            const parts = name.split(/\s+/);
            const firstName = parts[0] || '';
            const lastName = parts.slice(1).join(' ') || '';

            const payload = {
                firstName,
                lastName,
                email,
                phone,
                message,
                data: {
                    source: 'web',
                    interest: interest
                }
            };

            const btn = form.querySelector('[type="submit"]');
            const origText = btn.textContent;
            btn.textContent = 'Odesílám...';
            btn.disabled = true;

            try {
                const res = await fetch('/api/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    form.reset();
                    document.querySelector('#interest').value = 'Koupě celého projektu';
                    btn.textContent = 'Odesláno ✓';
                    setTimeout(() => { btn.textContent = origText; btn.disabled = false; }, 3000);
                } else {
                    console.error('API error:', await res.json());
                    btn.textContent = 'Chyba – zkuste znovu';
                    setTimeout(() => { btn.textContent = origText; btn.disabled = false; }, 3000);
                }
            } catch (err) {
                console.error('Network error:', err);
                btn.textContent = 'Chyba připojení';
                setTimeout(() => { btn.textContent = origText; btn.disabled = false; }, 3000);
            }
        });
    })();

    // Accordion functionality
    const layoutItems = document.querySelectorAll('.layout-item');

    layoutItems.forEach(item => {
        const header = item.querySelector('.layout-header');
        const content = item.querySelector('.layout-content');
        const icon = item.querySelector('.toggle-icon');

        header?.addEventListener('click', () => {
            // Close all other items
            layoutItems.forEach(otherItem => {
                if (otherItem !== item) {
                    const otherContent = otherItem.querySelector('.layout-content');
                    const otherIcon = otherItem.querySelector('.toggle-icon');
                    if (otherContent && otherIcon) {
                        otherContent.style.display = 'none';
                        otherIcon.textContent = '+';
                    }
                }
            });

            // Toggle current item
            if (content && icon) {
                const isOpen = content.style.display === 'block';
                content.style.display = isOpen ? 'none' : 'block';
                icon.textContent = isOpen ? '+' : '-';
            }
        });
    });
});
