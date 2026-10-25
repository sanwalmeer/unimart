const elements = {
  search: document.getElementById('searchInput'),
  category: document.getElementById('categoryFilter'),
  condition: document.getElementById('conditionFilter'),
  university: document.getElementById('universityFilter'),
  sort: document.getElementById('sortFilter'),
  grid: document.getElementById('productGrid'),
  count: document.getElementById('catalogCount'),
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

const loadCatalog = async () => {
  const response = await fetch('/api/catalog/');
  if (!response.ok) throw new Error('Could not load marketplace filters.');
  const catalog = await response.json();
  elements.category.insertAdjacentHTML('beforeend', catalog.categories.map((category) =>
    `<option value="${category.id}">${escapeHtml(category.name)}</option>`).join(''));
  elements.university.insertAdjacentHTML('beforeend', catalog.universities.map((university) =>
    `<option value="${university.id}">${escapeHtml(university.name)}</option>`).join(''));
};

const productCard = (product) => {
  const image = product.image
    ? `<img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.title)}" loading="lazy" onerror="this.parentElement.innerHTML='<span class=&quot;image-fallback&quot;>Campus find</span>'" />`
    : '<span class="image-fallback">Campus find</span>';
  const cardContent = `
      <div class="catalog-card-image">${image}</div>
      <div class="catalog-card-body">
        ${product.demo ? '<span class="preview-tag">Sample listing</span>' : ''}
        <div class="catalog-card-meta"><span>${escapeHtml(product.condition)}</span><span>${escapeHtml(product.university)}</span></div>
        <h3>${escapeHtml(product.title)}</h3>
        <p class="catalog-card-price">${formatPrice(product.price)}</p>
        <p class="catalog-card-category">${escapeHtml(product.category)}</p>
      </div>`;
  return product.demo
    ? `<article class="catalog-card demo-product">${cardContent}</article>`
    : `<a class="catalog-card" href="/products/${product.id}/">${cardContent}</a>`;
};

const loadProducts = async () => {
  const params = new URLSearchParams();
  if (elements.search.value.trim()) params.set('search', elements.search.value.trim());
  if (elements.category.value) params.set('category', elements.category.value);
  if (elements.university.value) params.set('university', elements.university.value);
  if (elements.condition.value) params.set('condition', elements.condition.value);

  elements.grid.innerHTML = '<p class="loading-state">Loading products...</p>';
  try {
    const response = await fetch(`/api/products/?${params.toString()}`);
    if (!response.ok) throw new Error('Could not load products.');
    const { products } = await response.json();
    const sort = elements.sort.value;
    if (sort === 'price-low') products.sort((left, right) => Number(left.price) - Number(right.price));
    if (sort === 'price-high') products.sort((left, right) => Number(right.price) - Number(left.price));
    elements.count.textContent = String(products.length);
    document.getElementById('demoFeedNotice').hidden = !products.some((product) => product.demo);
    elements.grid.innerHTML = products.length
      ? products.map(productCard).join('')
      : '<div class="empty-state"><h3>No products match these filters</h3><p>Try another category or clear your filters.</p></div>';
  } catch (error) {
    elements.grid.innerHTML = `<div class="empty-state"><h3>Products could not load</h3><p>${escapeHtml(error.message)}</p></div>`;
  }
};

let searchTimer;
elements.search.addEventListener('input', () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(loadProducts, 250);
});
[elements.category, elements.condition, elements.university, elements.sort].forEach((control) => {
  control.addEventListener('change', loadProducts);
});
document.getElementById('clearFilters').addEventListener('click', () => {
  elements.search.value = '';
  elements.category.value = '';
  elements.condition.value = '';
  elements.university.value = '';
  elements.sort.value = 'recent';
  loadProducts();
});

try {
  await loadCatalog();
  await loadProducts();
} catch (error) {
  elements.grid.innerHTML = `<div class="empty-state"><h3>Marketplace data could not load</h3><p>${escapeHtml(error.message)}</p></div>`;
}
