/* =====================================================
   FOCUS — app.js
   Shared logic: header, cart, modals, product cards
   ===================================================== */

// Inject SVG filter to remove white backgrounds from product images
// feColorMatrix formula: alpha = 3 - R - G - B (white→transparent, colors→opaque)
document.addEventListener('DOMContentLoaded', function () {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('style', 'display:none;position:absolute;width:0;height:0');
  svg.innerHTML = '<defs><filter id="remove-white" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  -1 -1 -1 3 0"/></filter></defs>';
  document.body.prepend(svg);
});

// ─────────────────────────────────────────
// CONFIG — editá estos valores
// ─────────────────────────────────────────
const WHATSAPP_NUMBER = '5492645557617'; // Argentina: 54 + 9 + 264 5557617
const STORE_NAME      = 'FOCUS Perfumes & Cosméticos';

// ─────────────────────────────────────────
// Cart State
// ─────────────────────────────────────────
let cart = JSON.parse(localStorage.getItem('focus_cart') || '[]');

function saveCart() {
  localStorage.setItem('focus_cart', JSON.stringify(cart));
}

function addToCart(carpeta) {
  const product = CATALOGO.find(p => p.carpeta === carpeta);
  if (!product) return;

  const existing = cart.find(i => i.carpeta === carpeta);
  if (existing) {
    existing.qty++;
  } else {
    cart.push({ ...product, qty: 1 });
  }
  saveCart();
  updateCartUI();
  showToast(`✓ ${formatName(product.nombre)} agregado`);
  openCart();
}

function addVaperToCart(idx) {
  if (typeof CATALOGO_VAPERS === 'undefined') return;
  const v = CATALOGO_VAPERS[idx];
  if (!v) return;

  const id = `vaper__${v.marca}__${v.modelo}__${idx}`;
  const existing = cart.find(i => i.carpeta === id);
  if (existing) {
    existing.qty++;
  } else {
    cart.push({
      carpeta: id,
      nombre: `${v.modelo} — ${v.nombre}`,
      marca: v.marca,
      precio: v.precio,
      moneda: v.moneda,
      tipo: 'vaper',
      imagen: v.imagen,
      tiene_imagen: false,
      qty: 1
    });
  }
  saveCart();
  updateCartUI();
  showToast(`✓ ${v.nombre} agregado`);
  openCart();
}

function removeFromCart(carpeta) {
  cart = cart.filter(i => i.carpeta !== carpeta);
  saveCart();
  updateCartUI();
}

function changeQty(carpeta, delta) {
  const item = cart.find(i => i.carpeta === carpeta);
  if (!item) return;
  item.qty = Math.max(1, item.qty + delta);
  saveCart();
  updateCartUI();
}

// ─────────────────────────────────────────
// Price Formatting
// ─────────────────────────────────────────
function formatPrice(product) {
  if (product.moneda === 'ARS') {
    // Argentine peso: $30.000
    return '$' + product.precio.toLocaleString('es-AR');
  }
  // USD
  return '$' + product.precio.toFixed(2);
}

function formatPriceValue(precio, moneda) {
  if (moneda === 'ARS') {
    return '$' + precio.toLocaleString('es-AR');
  }
  return '$' + precio.toFixed(2);
}

// ─────────────────────────────────────────
// WhatsApp
// ─────────────────────────────────────────
function cartToWhatsApp() {
  if (cart.length === 0) {
    showToast('Tu carrito está vacío');
    return;
  }

  const now = new Date();
  const fecha = now.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });

  let msg = `Estimado equipo de *${STORE_NAME}*,\n\n`;
  msg += `Me comunico para realizar una consulta de compra. A continuación detallo los productos de mi interés:\n\n`;

  cart.forEach((item, idx) => {
    const name  = formatName(item.nombre);
    const qty   = item.qty;
    const unit  = formatPriceValue(item.precio, item.moneda);
    const total = formatPriceValue(item.precio * qty, item.moneda);
    msg += `${idx + 1}. *${name}*`;
    if (item.cantidad) msg += ` — ${item.cantidad}`;
    msg += `\n   Cantidad: ${qty} u.  |  P. unitario: ${unit}  |  Subtotal: ${total}\n`;
  });

  // Total (mixed currencies — show per currency)
  const arsItems = cart.filter(i => i.moneda === 'ARS');
  const usdItems = cart.filter(i => i.moneda === 'USD');
  msg += '\n';
  if (arsItems.length > 0) {
    const arsTotal = arsItems.reduce((s, i) => s + i.precio * i.qty, 0);
    msg += `*Subtotal ARS:* ${formatPriceValue(arsTotal, 'ARS')}\n`;
  }
  if (usdItems.length > 0) {
    const usdTotal = usdItems.reduce((s, i) => s + i.precio * i.qty, 0);
    msg += `*Subtotal Otros (USD):* ${formatPriceValue(usdTotal, 'USD')}\n`;
  }

  msg += `\nQuedo a la espera de confirmación de stock y opciones de envío.\n`;
  msg += `Desde ya, muchas gracias.\n\n`;
  msg += `_Consulta generada el ${fecha}_`;

  const url = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`;
  window.open(url, '_blank');
}

// ─────────────────────────────────────────
// Cart UI
// ─────────────────────────────────────────
function updateCartUI() {
  const badge = document.getElementById('cartBadge');
  const totalUnits = cart.reduce((s, i) => s + i.qty, 0);

  if (badge) {
    badge.textContent = totalUnits;
    badge.classList.toggle('visible', totalUnits > 0);
  }

  const cartItemsEl  = document.getElementById('cartItems');
  const cartEmptyEl  = document.getElementById('cartEmpty');
  const cartFooterEl = document.getElementById('cartFooter');
  const cartTotalEl  = document.getElementById('cartTotal');

  if (!cartItemsEl) return;

  // Remove existing cart-item elements (keep cart-empty)
  cartItemsEl.querySelectorAll('.cart-item').forEach(el => el.remove());

  if (cart.length === 0) {
    if (cartEmptyEl) cartEmptyEl.style.display = '';
    if (cartFooterEl) cartFooterEl.style.display = 'none';
    return;
  }

  if (cartEmptyEl) cartEmptyEl.style.display = 'none';
  if (cartFooterEl) cartFooterEl.style.display = 'flex';

  const arsTotal = cart.filter(i => i.moneda === 'ARS').reduce((s, i) => s + i.precio * i.qty, 0);
  const usdTotal = cart.filter(i => i.moneda !== 'ARS').reduce((s, i) => s + i.precio * i.qty, 0);
  if (cartTotalEl) {
    let totalText = '';
    if (arsTotal > 0) totalText += formatPriceValue(arsTotal, 'ARS');
    if (arsTotal > 0 && usdTotal > 0) totalText += ' + ';
    if (usdTotal > 0) totalText += formatPriceValue(usdTotal, 'USD');
    cartTotalEl.textContent = totalText;
  }

  cart.forEach(item => {
    const div = document.createElement('div');
    div.className = 'cart-item';
    div.dataset.carpeta = item.carpeta;
    div.innerHTML = `
      <div class="cart-item-img">
        ${(item.tipo === 'vaper' || item.tipo === 'accesorio') && item.imagen
          ? `<img src="${item.imagen}" alt="${formatName(item.nombre)}" loading="lazy" style="object-fit:contain;background:#111;">`
          : item.tiene_imagen
            ? `<img src="../catalogo/${item.carpeta}/imagen.jpeg" alt="${formatName(item.nombre)}" loading="lazy"
                 onerror="this.parentElement.innerHTML=buildPlaceholder('${item.marca}','${item.categoria}')">`
            : buildPlaceholder(item.marca, item.categoria || 'Vapers')
        }
      </div>
      <div class="cart-item-info">
        <div class="cart-item-marca">${item.marca !== 'OTROS' ? item.marca : ''}</div>
        <div class="cart-item-name">${formatName(item.nombre)}</div>
        <div class="cart-item-controls">
          <div class="qty-controls">
            <button class="qty-btn" data-action="dec" data-carpeta="${item.carpeta}">−</button>
            <span class="qty-value">${item.qty}</span>
            <button class="qty-btn" data-action="inc" data-carpeta="${item.carpeta}">+</button>
          </div>
          <span class="cart-item-price">${formatPriceValue(item.precio * item.qty, item.moneda)}</span>
          <button class="cart-item-remove" data-carpeta="${item.carpeta}" title="Eliminar">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
            </svg>
          </button>
        </div>
      </div>
    `;
    cartItemsEl.appendChild(div);
  });

  // Delegate cart item events (avoids inline onclick issues)
  cartItemsEl.onclick = (e) => {
    const decBtn = e.target.closest('[data-action="dec"]');
    const incBtn = e.target.closest('[data-action="inc"]');
    const rmBtn  = e.target.closest('.cart-item-remove');
    if (decBtn) changeQty(decBtn.dataset.carpeta, -1);
    if (incBtn) changeQty(incBtn.dataset.carpeta, 1);
    if (rmBtn)  removeFromCart(rmBtn.dataset.carpeta);
  };
}

// ─────────────────────────────────────────
// Product Card Builder
// ─────────────────────────────────────────
function buildProductCard(product) {
  const imgSrc = product.tiene_imagen
    ? `../catalogo/${product.carpeta}/imagen.jpeg`
    : null;

  const name  = formatName(product.nombre);
  const marca = product.marca !== 'OTROS' ? product.marca : '';

  return `
    <div class="product-card" data-carpeta="${product.carpeta}">
      <div class="product-image">
        ${imgSrc
          ? `<img src="${imgSrc}" alt="${name}" loading="lazy"
               onerror="this.parentElement.innerHTML=buildPlaceholder('${marca}', '${product.categoria}')">`
          : buildPlaceholder(marca, product.categoria)
        }
        <div class="product-actions-overlay">
          <button class="product-quick-add" data-carpeta="${product.carpeta}" data-action="add">
            + Agregar al carrito
          </button>
        </div>
      </div>
      <div class="product-info">
        ${marca ? `<div class="product-marca">${marca}</div>` : ''}
        <div class="product-name">${name}</div>
        ${product.aroma ? `<div class="product-aroma">${product.aroma}</div>` : ''}
        ${product.cantidad ? `<div class="product-cantidad">${product.cantidad}</div>` : ''}
        <div class="product-footer">
          <div class="product-price">${formatPrice(product)}</div>
          <button class="product-add-btn" data-carpeta="${product.carpeta}" data-action="add" title="Agregar al carrito">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  `;
}

// Luxury placeholder for products without a real photo
function buildPlaceholder(marca, categoria) {
  // Pick gradient & icon by category
  const themes = {
    'Perfumes':      { bg: 'linear-gradient(145deg,#1a1200,#2d2000,#1a1200)', accent: '#c9a227', icon: placeholderIconPerfume() },
    'Body Cream':    { bg: 'linear-gradient(145deg,#0e1a1a,#162a2a,#0e1a1a)', accent: '#7ecaca', icon: placeholderIconCream() },
    'Ambientadores': { bg: 'linear-gradient(145deg,#0d1a10,#152b1a,#0d1a10)', accent: '#7ec47e', icon: placeholderIconAir() },
  };
  const t = themes[categoria] || themes['Perfumes'];
  const label = marca || 'FOCUS';

  return `
    <div class="product-placeholder" style="background:${t.bg};">
      <div class="placeholder-ring" style="border-color:${t.accent}33;">
        <div class="placeholder-icon" style="color:${t.accent};">${t.icon}</div>
      </div>
      <div class="placeholder-brand" style="color:${t.accent};">${label}</div>
    </div>`;
}

function placeholderIconPerfume() {
  return `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
    <path d="M9 3h6v2H9zM7 5h10v2a6 6 0 0 1 0 12H7a6 6 0 0 1 0-12V5z"/>
    <circle cx="12" cy="11" r="1.5" fill="currentColor" stroke="none"/>
  </svg>`;
}

function placeholderIconCream() {
  return `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
    <path d="M8 3h8a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/>
    <path d="M10 3V1M14 3V1"/>
    <path d="M9 10c1.5-1 4.5-1 6 0"/>
  </svg>`;
}

function placeholderIconAir() {
  return `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
    <path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/>
  </svg>`;
}

// Global event delegation for product grids (handles cards without inline onclick)
document.addEventListener('click', (e) => {
  const addBtn = e.target.closest('[data-action="add"]');
  if (addBtn) {
    e.stopPropagation();
    addToCart(addBtn.dataset.carpeta);
    return;
  }

  const card = e.target.closest('.product-card');
  if (card && card.dataset.carpeta && !e.target.closest('[data-action]')) {
    openModal(card.dataset.carpeta);
  }
});

// ─────────────────────────────────────────
// Product Modal
// ─────────────────────────────────────────
function openModal(carpeta) {
  const product = CATALOGO.find(p => p.carpeta === carpeta);
  if (!product) return;

  const name   = formatName(product.nombre);
  const marca  = product.marca !== 'OTROS' ? product.marca : '';
  const imgSrc = product.tiene_imagen ? `../catalogo/${product.carpeta}/imagen.jpeg` : null;

  document.getElementById('modalContent').innerHTML = `
    <div class="modal-image">
      ${imgSrc
        ? `<img src="${imgSrc}" alt="${name}"
             onerror="this.parentElement.innerHTML=buildPlaceholder('${marca}','${product.categoria}')">`
        : buildPlaceholder(marca, product.categoria)
      }
    </div>
    <div class="modal-body">
      ${marca ? `<div class="modal-marca">${marca}</div>` : ''}
      <h2 class="modal-name">${name}</h2>
      ${product.cantidad ? `<div class="modal-qty">${product.cantidad}</div>` : ''}
      <div class="modal-price">${formatPrice(product)}</div>
      ${product.aroma ? `<div class="modal-aroma">${product.aroma}</div>` : ''}
      <div class="modal-desc">${product.descripcion || 'Fragancia de lujo árabe.'}</div>
      <div style="display:flex;gap:12px;margin-top:8px;">
        <button class="btn btn-primary" style="flex:1;justify-content:center;"
          data-carpeta="${product.carpeta}" data-action="add-close">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <path d="M16 10a4 4 0 0 1-8 0"/>
          </svg>
          Agregar al carrito
        </button>
      </div>
    </div>
  `;

  // Handle modal add button
  document.querySelector('[data-action="add-close"]')?.addEventListener('click', () => {
    addToCart(product.carpeta);
    closeModal();
  });

  document.getElementById('modalOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modalOverlay')?.classList.remove('open');
  document.body.style.overflow = '';
}

// ─────────────────────────────────────────
// Cart Drawer
// ─────────────────────────────────────────
function openCart() {
  document.getElementById('cartDrawer')?.classList.add('open');
  document.getElementById('cartOverlay')?.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeCart() {
  document.getElementById('cartDrawer')?.classList.remove('open');
  document.getElementById('cartOverlay')?.classList.remove('open');
  document.body.style.overflow = '';
}

// ─────────────────────────────────────────
// Toast
// ─────────────────────────────────────────
function showToast(message, duration = 2500) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all .3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ─────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────
// Preserves uppercase abbreviations: EDP, EDT, ML, EDP, etc.
const KEEP_UPPER = new Set(['EDP','EDT','EDP','EDP','ML','G','OZ','AIR','FRESHENER','ALHAMBRA']);

function formatName(nombre) {
  return nombre.split(' ').map(w => {
    if (KEEP_UPPER.has(w)) return w;
    return w.length > 2
      ? w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()
      : w.toLowerCase();
  }).join(' ');
}

// ─────────────────────────────────────────
// Header scroll effect
// ─────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('header')?.classList.toggle('scrolled', window.scrollY > 50);
}, { passive: true });

// ─────────────────────────────────────────
// DOMContentLoaded: Wire up shared elements
// ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // Mobile hamburger
  document.getElementById('hamburgerBtn')?.addEventListener('click', () => {
    document.getElementById('mobileMenu')?.classList.toggle('open');
  });

  // Cart open/close
  document.getElementById('cartBtn')?.addEventListener('click', openCart);
  document.getElementById('closeCartBtn')?.addEventListener('click', closeCart);
  document.getElementById('cartOverlay')?.addEventListener('click', closeCart);

  // Modal close
  document.getElementById('modalClose')?.addEventListener('click', closeModal);
  document.getElementById('modalOverlay')?.addEventListener('click', (e) => {
    if (e.target.id === 'modalOverlay') closeModal();
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { closeModal(); closeCart(); }
  });

  // Init cart
  updateCartUI();
});
