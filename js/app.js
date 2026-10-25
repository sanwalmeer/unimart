const universities = [
  'NUST',
  'COMSATS University Islamabad',
  'FAST-NUCES Islamabad',
  'Quaid-i-Azam University (QAU)',
  'Air University',
  'Bahria University Islamabad',
  'International Islamic University Islamabad (IIUI)',
  'NUML Islamabad',
  'Institute of Space Technology (IST)',
  'Riphah International University Islamabad',
  'NUTECH (National University of Technology)',
];

const categories = [
  'Electronics & Laptops',
  'Headphones & Accessories',
  'Books & Study Materials',
  'Backpacks & Bags',
  'Clothes & Fashion',
  'Sneakers & Footwear',
  'Kitchen Essentials',
  'Food & Homemade Meals',
  'Hostel & Room Essentials',
  'Handmade Products',
];

const products = [
  {
    id: 1,
    title: 'Dell Latitude 7410',
    description: 'Well-maintained business laptop with 16GB RAM and 512GB SSD. Perfect for study and work.',
    price: 82000,
    category: 'Electronics & Laptops',
    condition: 'Pre-loved',
    university: 'NUST',
    sellerName: 'Ali R.',
    image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80',
    status: 'Approved',
    createdAt: '2026-10-20',
  },
  {
    id: 2,
    title: 'Chemistry Lab Book Set',
    description: 'Complete set of used but clean chemistry books and notes. Good for first-year students.',
    price: 3500,
    category: 'Books & Study Materials',
    condition: 'Pre-loved',
    university: 'FAST-NUCES Islamabad',
    sellerName: 'Hania K.',
    image: 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=900&q=80',
    status: 'Approved',
    createdAt: '2026-10-19',
  },
  {
    id: 3,
    title: 'MacBook Air 13"',
    description: 'Lightweight and fast machine, ideal for daily coursework and design tasks.',
    price: 155000,
    category: 'Electronics & Laptops',
    condition: 'New',
    university: 'COMSATS University Islamabad',
    sellerName: 'Muzammil A.',
    image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80',
    status: 'Approved',
    createdAt: '2026-10-18',
  },
  {
    id: 4,
    title: 'Urban Backpack',
    description: 'Water-resistant backpack with laptop sleeve and storage compartments.',
    price: 4200,
    category: 'Backpacks & Bags',
    condition: 'New',
    university: 'Air University',
    sellerName: 'Sara M.',
    image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80',
    status: 'Approved',
    createdAt: '2026-10-17',
  },
  {
    id: 5,
    title: 'Wireless Noise Cancelling Headphones',
    description: 'Great battery life and clear sound for lectures, gaming and travel.',
    price: 18000,
    category: 'Headphones & Accessories',
    condition: 'New',
    university: 'Bahria University Islamabad',
    sellerName: 'Usman T.',
    image: 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80',
    status: 'Approved',
    createdAt: '2026-10-16',
  },
  {
    id: 6,
    title: 'Study Desk Lamp',
    description: 'Modern LED desk lamp with adjustable brightness and USB charging port.',
    price: 2600,
    category: 'Hostel & Room Essentials',
    condition: 'New',
    university: 'NUML Islamabad',
    sellerName: 'Zoya F.',
    image: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80',
    status: 'Approved',
    createdAt: '2026-10-15',
  },
  {
    id: 7,
    title: 'Handmade Ceramic Mug Set',
    description: 'Set of 4 handmade ceramic mugs for hostel rooms and gifting.',
    price: 1800,
    category: 'Handmade Products',
    condition: 'New',
    university: 'IIUI',
    sellerName: 'Mahnoor S.',
    image: 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=80',
    status: 'Pending',
    createdAt: '2026-10-12',
  },
  {
    id: 8,
    title: 'Sneaker Size 40',
    description: 'Minimal running sneakers in clean condition, lightly worn only a few times.',
    price: 8000,
    category: 'Sneakers & Footwear',
    condition: 'Pre-loved',
    university: 'Riphah International University Islamabad',
    sellerName: 'Nimra Q.',
    image: 'https://images.unsplash.com/photo-1543508282-6319a3e2621f?auto=format&fit=crop&w=900&q=80',
    status: 'Approved',
    createdAt: '2026-10-11',
  },
];

const currentUser = {
  name: 'Ayesha B.',
  role: 'verified-seller',
  university: 'NUST',
};

const state = {
  search: '',
  selectedCategory: 'All',
  selectedUniversity: 'All Universities',
  favorites: [1, 3],
  draft: {
    title: '',
    description: '',
    price: '',
    category: categories[0],
    condition: 'New',
    university: 'NUST',
  },
};

const formatPrice = (amount) =>
  new Intl.NumberFormat('en-PK', {
    style: 'currency',
    currency: 'PKR',
    maximumFractionDigits: 0,
  }).format(amount);

const getVisibleProducts = () => {
  return products.filter((product) => {
    if (product.status !== 'Approved') return false;

    const searchText = `${product.title} ${product.description}`.toLowerCase();
    const matchesSearch = searchText.includes(state.search.toLowerCase());
    const matchesCategory = state.selectedCategory === 'All' || product.category === state.selectedCategory;
    const matchesUniversity = state.selectedUniversity === 'All Universities' || product.university === state.selectedUniversity;

    return matchesSearch && matchesCategory && matchesUniversity;
  });
};

const renderFilters = () => {
  const categorySelect = document.getElementById('categoryFilter');
  const universitySelect = document.getElementById('universityFilter');

  categorySelect.innerHTML = '<option value="All">All Categories</option>' +
    categories.map((category) => `<option value="${category}">${category}</option>`).join('');

  universitySelect.innerHTML = '<option value="All Universities">All Universities</option>' +
    universities.map((uni) => `<option value="${uni}">${uni}</option>`).join('');

  categorySelect.value = state.selectedCategory;
  universitySelect.value = state.selectedUniversity;
};

const renderFavorites = () => {
  const favoritesList = document.getElementById('favoritesList');
  const favorites = products.filter((product) => state.favorites.includes(product.id));

  if (!favorites.length) {
    favoritesList.innerHTML = '<li class="muted">No saved items yet.</li>';
    return;
  }

  favoritesList.innerHTML = favorites
    .map(
      (product) => `
        <li>
          <span>${product.title}</span>
          <strong>${formatPrice(product.price)}</strong>
        </li>
      `
    )
    .join('');
};

const renderMyListings = () => {
  const myListings = document.getElementById('myListings');
  const sellerListings = products.filter((product) => product.sellerName === currentUser.name);

  if (!sellerListings.length) {
    myListings.innerHTML = '<li class="muted">No listings yet.</li>';
    return;
  }

  myListings.innerHTML = sellerListings
    .map(
      (product) => `
        <li>
          <span>${product.title}</span>
          <strong>${product.status}</strong>
        </li>
      `
    )
    .join('');
};

const renderProducts = () => {
  const visibleProducts = getVisibleProducts();
  const productGrid = document.getElementById('productGrid');
  const resultCount = document.getElementById('resultCount');
  const activeListingCount = document.getElementById('activeListingCount');

  activeListingCount.textContent = String(visibleProducts.length);
  resultCount.textContent = `${visibleProducts.length} items`;

  if (!visibleProducts.length) {
    productGrid.innerHTML = `
      <div class="empty-state">
        <h3>No results found</h3>
        <p>Try changing the filters or search phrasing to discover more items.</p>
      </div>
    `;
    return;
  }

  productGrid.innerHTML = visibleProducts
    .map(
      (product) => `
        <article class="product-card">
          <div class="image-wrap">
            <img src="${product.image}" alt="${product.title}" />
            <button class="favorite-button ${state.favorites.includes(product.id) ? 'active' : ''}" data-id="${product.id}" type="button" aria-label="Toggle favorite">
              ♥
            </button>
          </div>
          <div class="card-body">
            <div class="meta-row">
              <span class="pill">${product.condition}</span>
              <span class="university-pill">${product.university}</span>
            </div>
            <h3>${product.title}</h3>
            <p class="price">${formatPrice(product.price)}</p>
            <div class="category-line">${product.category}</div>
            <p class="seller">Seller: ${product.sellerName}</p>
          </div>
        </article>
      `
    )
    .join('');

  document.querySelectorAll('.favorite-button').forEach((button) => {
    button.addEventListener('click', () => {
      const productId = Number(button.dataset.id);
      if (state.favorites.includes(productId)) {
        state.favorites = state.favorites.filter((id) => id !== productId);
      } else {
        state.favorites = [...state.favorites, productId];
      }
      render();
    });
  });
};

const render = () => {
  renderFilters();
  renderProducts();
  renderFavorites();
  renderMyListings();
  document.getElementById('universitiesCount').textContent = String(universities.length);
};

const openSellModal = () => {
  const container = document.getElementById('sellModalContainer');
  container.innerHTML = `
    <div class="modal-backdrop" role="dialog" aria-modal="true">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Sell a product</h3>
          <button class="close-button" type="button" id="closeSellModal">×</button>
        </div>

        <form class="sell-form" id="sellForm">
          <label>
            Title
            <input type="text" id="titleField" value="${state.draft.title}" required />
          </label>

          <label>
            Description
            <textarea id="descriptionField" rows="4" required>${state.draft.description}</textarea>
          </label>

          <div class="double-field">
            <label>
              Price (PKR)
              <input type="number" min="1" id="priceField" value="${state.draft.price}" required />
            </label>

            <label>
              Condition
              <select id="conditionField">
                <option value="New" ${state.draft.condition === 'New' ? 'selected' : ''}>New</option>
                <option value="Pre-loved" ${state.draft.condition === 'Pre-loved' ? 'selected' : ''}>Pre-loved</option>
              </select>
            </label>
          </div>

          <div class="double-field">
            <label>
              Category
              <select id="categoryField">
                ${categories.map((category) => `<option value="${category}" ${state.draft.category === category ? 'selected' : ''}>${category}</option>`).join('')}
              </select>
            </label>

            <label>
              University affiliation
              <select id="universityField">
                ${universities.map((uni) => `<option value="${uni}" ${state.draft.university === uni ? 'selected' : ''}>${uni}</option>`).join('')}
              </select>
            </label>
          </div>

          <div class="modal-actions">
            <button type="button" class="secondary-button" id="cancelSellModal">Cancel</button>
            <button type="submit" class="primary-button">Submit for Review</button>
          </div>
        </form>
      </div>
    </div>
  `;

  document.getElementById('closeSellModal').addEventListener('click', closeSellModal);
  document.getElementById('cancelSellModal').addEventListener('click', closeSellModal);

  document.getElementById('sellForm').addEventListener('submit', (event) => {
    event.preventDefault();

    const title = document.getElementById('titleField').value.trim();
    const description = document.getElementById('descriptionField').value.trim();
    const price = Number(document.getElementById('priceField').value);
    const category = document.getElementById('categoryField').value;
    const condition = document.getElementById('conditionField').value;
    const university = document.getElementById('universityField').value;

    if (!title || !description || !price || !category || !condition || !university) {
      return;
    }

    products.unshift({
      id: Date.now(),
      title,
      description,
      price,
      category,
      condition,
      university,
      sellerName: currentUser.name,
      image: 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80',
      status: 'Pending',
      createdAt: new Date().toISOString().slice(0, 10),
    });

    closeSellModal();
    render();
  });
};

const closeSellModal = () => {
  document.getElementById('sellModalContainer').innerHTML = '';
};

const bindEvents = () => {
  document.getElementById('searchInput').addEventListener('input', (event) => {
    state.search = event.target.value;
    renderProducts();
  });

  document.getElementById('categoryFilter').addEventListener('change', (event) => {
    state.selectedCategory = event.target.value;
    renderProducts();
  });

  document.getElementById('universityFilter').addEventListener('change', (event) => {
    state.selectedUniversity = event.target.value;
    renderProducts();
  });

  document.getElementById('clearFilters').addEventListener('click', () => {
    state.search = '';
    state.selectedCategory = 'All';
    state.selectedUniversity = 'All Universities';
    document.getElementById('searchInput').value = '';
    render();
  });

  document.getElementById('openSellModal').addEventListener('click', openSellModal);
  document.getElementById('openSellModalSecondary').addEventListener('click', openSellModal);
};

render();
bindEvents();
