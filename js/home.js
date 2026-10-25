const state = {
  categories: [],
  universities: [],
  products: [],
  myProducts: [],
  favoriteProducts: [],
  user: null,
  favorites: new Set(),
  csrfToken: '',
};

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}[character]));

const formatPrice = (amount) => new Intl.NumberFormat('en-PK', {
  style: 'currency',
  currency: 'PKR',
  maximumFractionDigits: 0,
}).format(Number(amount));

const api = async (url, options = {}) => {
  const headers = new Headers(options.headers || {});
  if (options.method && options.method !== 'GET') {
    if (!state.csrfToken) {
      const csrfResponse = await fetch('/api/csrf/');
      state.csrfToken = (await csrfResponse.json()).csrfToken;
    }
    headers.set('Content-Type', 'application/json');
    headers.set('X-CSRFToken', state.csrfToken);
  }
  const response = await fetch(url, { ...options, headers, credentials: 'same-origin' });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || 'Something went wrong. Please try again.');
  return data;
};

const showMessage = (message, isError = false) => {
  let element = document.getElementById('pageMessage');
  if (!element) {
    element = document.createElement('div');
    element.id = 'pageMessage';
    element.className = 'page-message';
    element.setAttribute('role', 'status');
    document.querySelector('main').prepend(element);
  }
  element.textContent = message;
  element.classList.toggle('error', isError);
};

const renderAccountActions = () => {
  const actions = document.getElementById('accountActions');
  if (!actions) return;
  actions.innerHTML = state.user
    ? `<span class="account-greeting">Hi, ${escapeHtml(state.user.name)}</span><button class="secondary-button" type="button" id="logoutButton">Log out</button><button class="primary-button" type="button" id="openSellModal">Sell Product</button>`
    : '<button class="secondary-button" type="button" id="loginButton">Log in</button><button class="primary-button" type="button" id="signupButton">Sign up</button>';
  document.getElementById('loginButton')?.addEventListener('click', () => openAuthModal('login'));
  document.getElementById('signupButton')?.addEventListener('click', () => openAuthModal('signup'));
  document.getElementById('logoutButton')?.addEventListener('click', logoutUser);
  document.getElementById('openSellModal')?.addEventListener('click', openSellModal);
};

const renderFilters = () => {
  const categories = document.getElementById('categoryFilter');
  const universities = document.getElementById('universityFilter');
  categories.innerHTML = '<option value="">All Categories</option>' + state.categories.map((item) =>
    `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('');
  universities.innerHTML = '<option value="">All Universities</option>' + state.universities.map((item) =>
    `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('');
  document.getElementById('universitiesCount').textContent = String(state.universities.length);
};

const renderFavorites = () => {
  const list = document.getElementById('favoritesList');
  const products = state.favoriteProducts;
  list.innerHTML = products.length
    ? products.map((product) => `<li><a href="/products/${product.id}/">${escapeHtml(product.title)}</a><strong>${formatPrice(product.price)}</strong></li>`).join('')
    : '<li class="muted">No saved items yet.</li>';
};

const renderMyListings = () => {
  const list = document.getElementById('myListings');
  if (!state.user) {
    list.innerHTML = '<li class="muted"><button type="button" class="inline-action" id="listingLogin">Log in to see your listings</button></li>';
    document.getElementById('listingLogin').addEventListener('click', () => openAuthModal('login'));
    return;
  }
  list.innerHTML = state.myProducts.length
    ? state.myProducts.map((product) => `
      <li class="listing-status-item">
        <div><a href="${product.status === 'Approved' ? `/products/${product.id}/` : '#'}">${escapeHtml(product.title)}</a><strong class="status-${product.status.toLowerCase()}">${escapeHtml(product.status)}</strong>
        ${product.rejectionReason ? `<span class="rejection-reason">Reason: ${escapeHtml(product.rejectionReason)}</span>` : ''}</div>
        ${product.canWithdraw ? `<button class="withdraw-button" type="button" data-product-id="${product.id}">Withdraw</button>` : ''}
      </li>`).join('')
    : '<li class="muted">No listings yet. Submit your first product for review.</li>';
  list.querySelectorAll('.withdraw-button').forEach((button) => button.addEventListener('click', async () => {
    if (!window.confirm('Withdraw this listing? It will no longer be available publicly.')) return;
    try {
      await api(`/api/my-products/${button.dataset.productId}/withdraw/`, { method: 'POST', body: '{}' });
      await loadData();
      showMessage('Your listing has been withdrawn.');
    } catch (error) {
      showMessage(error.message, true);
    }
  }));
};

const renderProducts = () => {
  const search = document.getElementById('searchInput').value.trim().toLowerCase();
  const categoryId = document.getElementById('categoryFilter').value;
  const universityId = document.getElementById('universityFilter').value;
  const filtered = state.products.filter((product) => {
    const matchesText = `${product.title} ${product.description}`.toLowerCase().includes(search);
    return matchesText && (!categoryId || String(product.categoryId) === categoryId) &&
      (!universityId || String(product.universityId) === universityId);
  });
  document.getElementById('activeListingCount').textContent = String(state.products.length);
  document.getElementById('resultCount').textContent = `${filtered.length} of ${state.products.length} items`;
  document.getElementById('demoFeedNotice').hidden = !filtered.some((product) => product.demo);
  const grid = document.getElementById('productGrid');
  grid.innerHTML = filtered.length ? filtered.map((product) => `
    <article class="product-card">
      ${product.demo ? '<div class="preview-tag">Sample</div>' : ''}
      ${product.demo ? '<div class="product-card-content">' : `<a class="product-card-link" href="/products/${product.id}/" aria-label="View ${escapeHtml(product.title)}">`}
        <div class="image-wrap">${product.image ? `<img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.title)}" loading="lazy" />` : '<div class="image-fallback">Campus find</div>'}</div>
        <div class="card-body">
          <div class="meta-row"><span class="pill">${escapeHtml(product.condition)}</span><span class="university-pill">${escapeHtml(product.university)}</span></div>
          <h3>${escapeHtml(product.title)}</h3><p class="price">${formatPrice(product.price)}</p>
          <div class="category-line">${escapeHtml(product.category)}</div><p class="seller">Seller: ${escapeHtml(product.sellerName)}</p>
        </div>
      ${product.demo ? '</div>' : '</a>'}
      ${product.demo ? '' : `<button class="favorite-button ${state.favorites.has(product.id) ? 'active' : ''}" data-id="${product.id}" type="button" aria-label="Toggle favorite">♥</button>`}
    </article>`).join('') : '<div class="empty-state"><h3>No approved products found</h3><p>Try clearing a filter or search for another item.</p><a href="/products/">Browse all products</a></div>';
  grid.querySelectorAll('.favorite-button').forEach((button) => button.addEventListener('click', async () => {
    if (!state.user) {
      openAuthModal('login');
      document.getElementById('authMessage').textContent = 'Log in to save this product to your favourites.';
      return;
    }
    const productId = Number(button.dataset.id);
    try {
      await api('/api/favorites/toggle/', { method: 'POST', body: JSON.stringify({ productId }) });
      const favoriteData = await api('/api/favorites/');
      state.favoriteProducts = favoriteData.products;
      state.favorites = new Set(state.favoriteProducts.map((product) => product.id));
      renderProducts();
      renderFavorites();
    } catch (error) {
      showMessage(error.message, true);
    }
  }));
  renderFavorites();
};

const loadData = async () => {
  const [catalog, productData, session] = await Promise.all([
    api('/api/catalog/'),
    api('/api/products/'),
    api('/api/session/'),
  ]);
  state.categories = catalog.categories;
  state.universities = catalog.universities;
  state.products = productData.products;
  state.user = session.user;
  state.favoriteProducts = [];
  state.favorites = new Set();
  renderFilters();
  renderAccountActions();
  renderProducts();
  if (state.user) {
    const [listingData, favoriteData] = await Promise.all([
      api('/api/my-products/'),
      api('/api/favorites/'),
    ]);
    state.myProducts = listingData.products;
    state.favoriteProducts = favoriteData.products;
    state.favorites = new Set(state.favoriteProducts.map((product) => product.id));
  }
  renderMyListings();
};

const openAuthModal = (mode = 'login') => {
  const container = document.getElementById('modalContainer');
  container.innerHTML = `
    <div class="modal-backdrop" role="presentation">
      <section class="modal-card auth-modal" role="dialog" aria-modal="true" aria-labelledby="authTitle">
        <div class="modal-header"><div><p class="eyebrow">Your campus community</p><h2 id="authTitle"></h2></div><button class="close-button" type="button" id="closeModal" aria-label="Close">×</button></div>
        <div class="auth-tabs" role="tablist"><button type="button" id="loginTab" role="tab" aria-selected="false">Log in</button><button type="button" id="signupTab" role="tab" aria-selected="false">Sign up</button></div>
        <p class="form-message" id="authMessage" role="status"></p>
        <form class="auth-form" id="loginForm">
          <label>Email address<input name="email" type="email" autocomplete="email" required /></label>
          <label>Password<input name="password" type="password" autocomplete="current-password" required /></label>
          <button class="primary-button" type="submit">Log in</button>
        </form>
        <form class="auth-form" id="signupForm" hidden>
          <label>Display name<input name="name" type="text" maxlength="150" autocomplete="name" required /></label>
          <label>Email address<input name="email" type="email" autocomplete="email" required /></label>
          <label>Password<input name="password" type="password" minlength="6" autocomplete="new-password" required /></label>
          <p class="form-hint">Personal email is welcome. In this local demo, your account is ready as soon as you sign up.</p>
          <button class="primary-button" type="submit">Sign up</button>
        </form>
      </section>
    </div>`;
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const loginTab = document.getElementById('loginTab');
  const signupTab = document.getElementById('signupTab');
  const setMode = (nextMode) => {
    const isLogin = nextMode === 'login';
    loginForm.hidden = !isLogin;
    signupForm.hidden = isLogin;
    loginTab.classList.toggle('selected', isLogin);
    signupTab.classList.toggle('selected', !isLogin);
    loginTab.setAttribute('aria-selected', String(isLogin));
    signupTab.setAttribute('aria-selected', String(!isLogin));
    document.getElementById('authTitle').textContent = isLogin ? 'Log in to UniMart' : 'Create your UniMart account';
  };
  loginTab.addEventListener('click', () => setMode('login'));
  signupTab.addEventListener('click', () => setMode('signup'));
  document.getElementById('closeModal').addEventListener('click', closeModal);
  container.querySelector('.modal-backdrop').addEventListener('click', (event) => {
    if (event.target.classList.contains('modal-backdrop')) closeModal();
  });
  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = new FormData(loginForm);
    try {
      await api('/api/login/', { method: 'POST', body: JSON.stringify(Object.fromEntries(form)) });
      closeModal();
      await loadData();
      const nextPath = new URLSearchParams(location.search).get('next');
      if (nextPath?.startsWith('/') && !nextPath.startsWith('//')) {
        location.assign(nextPath);
        return;
      }
      showMessage('You are signed in. You can now submit a product.');
    } catch (error) {
      document.getElementById('authMessage').classList.add('error');
      document.getElementById('authMessage').textContent = error.message;
    }
  });
  signupForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = new FormData(signupForm);
    try {
      const result = await api('/api/signup/', { method: 'POST', body: JSON.stringify(Object.fromEntries(form)) });
      if (result.authenticated) {
        state.user = result.user;
        closeModal();
        await loadData();
        const nextPath = new URLSearchParams(location.search).get('next');
        if (nextPath?.startsWith('/') && !nextPath.startsWith('//')) {
          location.assign(nextPath);
          return;
        }
        showMessage(result.message);
        return;
      }
      document.getElementById('authMessage').textContent = result.message;
      signupForm.reset();
    } catch (error) {
      document.getElementById('authMessage').classList.add('error');
      document.getElementById('authMessage').textContent = error.message;
    }
  });
  setMode(mode);
};

const closeModal = () => {
  document.getElementById('modalContainer').innerHTML = '';
};

const logoutUser = async () => {
  try {
    await api('/api/logout/', { method: 'POST', body: '{}' });
    state.user = null;
    state.myProducts = [];
    state.favoriteProducts = [];
    state.favorites = new Set();
    renderAccountActions();
    renderMyListings();
    renderProducts();
    showMessage('You have been signed out.');
  } catch (error) {
    showMessage(error.message, true);
  }
};

const openSellModal = async () => {
  if (!state.user) {
    openAuthModal('signup');
    return;
  }
  const container = document.getElementById('modalContainer');
  container.innerHTML = `
    <div class="modal-backdrop" role="presentation">
      <section class="modal-card" role="dialog" aria-modal="true" aria-labelledby="sellTitle">
        <div class="modal-header"><div><p class="eyebrow">One easy step to sell</p><h2 id="sellTitle">List a physical product</h2></div><button class="close-button" type="button" id="closeModal" aria-label="Close">×</button></div>
        <p class="form-message" id="sellMessage" role="status"></p>
        <form class="sell-form" id="sellForm">
          <label>Product title<input name="title" type="text" maxlength="200" required /></label>
          <label>Description<textarea name="description" rows="4" maxlength="5000" required></textarea></label>
          <div class="double-field">
            <label>Price (PKR)<input name="price" type="number" min="0.01" step="0.01" required /></label>
            <label>Condition<select name="condition"><option value="new">New</option><option value="pre_loved">Pre-loved</option></select></label>
          </div>
          <div class="double-field">
            <label>Category<select name="categoryId" required>${state.categories.map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('')}</select></label>
            <label>University affiliation<select name="universityId"><option value="">Not affiliated / Other</option>${state.universities.map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('')}</select></label>
          </div>
          <label>Product image URL<input name="imageUrl" type="url" placeholder="https://..." required /></label>
          <label class="contact-consent"><input name="allowEmailContact" type="checkbox" value="true" /> I agree to share my account email with signed-in buyers for this listing.</label>
          <p class="form-hint">Your listing stays private until an administrator approves it.</p>
          <div class="modal-actions"><button type="button" class="secondary-button" id="cancelModal">Cancel</button><button type="submit" class="primary-button">Submit for review</button></div>
        </form>
      </section>
    </div>`;
  document.getElementById('closeModal').addEventListener('click', closeModal);
  document.getElementById('cancelModal').addEventListener('click', closeModal);
  document.getElementById('sellForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const form = Object.fromEntries(formData);
    form.allowEmailContact = formData.get('allowEmailContact') === 'true';
    try {
      const result = await api('/api/products/create/', { method: 'POST', body: JSON.stringify(form) });
      state.myProducts.unshift(result.product);
      closeModal();
      renderMyListings();
      showMessage('Your product was submitted and will appear publicly after admin approval.');
    } catch (error) {
      document.getElementById('sellMessage').classList.add('error');
      document.getElementById('sellMessage').textContent = error.message;
    }
  });
};

const bindEvents = () => {
  document.getElementById('openSellModalSecondary').addEventListener('click', openSellModal);
  document.getElementById('searchInput').addEventListener('input', renderProducts);
  document.getElementById('categoryFilter').addEventListener('change', renderProducts);
  document.getElementById('universityFilter').addEventListener('change', renderProducts);
  document.getElementById('clearFilters').addEventListener('click', () => {
    document.getElementById('searchInput').value = '';
    document.getElementById('categoryFilter').value = '';
    document.getElementById('universityFilter').value = '';
    renderProducts();
  });
};

bindEvents();
try {
  await loadData();
  if (new URLSearchParams(location.search).has('verified')) showMessage('Email verified. You can now use your account and submit a listing.');
  const authMode = new URLSearchParams(location.search).get('auth');
  if (authMode === 'login' || authMode === 'signup') openAuthModal(authMode);
  if (new URLSearchParams(location.search).get('sell')) openSellModal();
} catch (error) {
  showMessage(error.message, true);
}
