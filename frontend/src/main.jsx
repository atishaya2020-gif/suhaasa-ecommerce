import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AnimatePresence, motion } from 'framer-motion';
import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Check,
  ChevronDown,
  Heart,
  Menu,
  Moon,
  Search,
  ShoppingBag,
  Sparkles,
  User,
  Sun,
  X,
} from 'lucide-react';
import './styles.css';

const REAL_IMAGES = {
  // Distinct editorial / product photography. Sources are Unsplash images marked free to use under the Unsplash License.
  hero: 'https://images.unsplash.com/photo-1743229995753-69be4b438204?auto=format&fit=crop&w=1800&q=90',
  kurtaA: 'https://images.unsplash.com/photo-1760287364328-e30221615f2e?auto=format&fit=crop&w=1200&q=88',
  kurtaB: 'https://images.unsplash.com/photo-1743229995505-d6374996df1c?auto=format&fit=crop&w=1200&q=88',
  kurtaC: 'https://images.unsplash.com/photo-1742800786544-e935375035e3?auto=format&fit=crop&w=1200&q=88',
  kurtaD: 'https://images.unsplash.com/photo-1742800788220-1e42256d6022?auto=format&fit=crop&w=1200&q=88',
  kurtaE: 'https://images.unsplash.com/photo-1762780700690-3fbb53fcd4e5?auto=format&fit=crop&w=1200&q=88',
  kurtaF: 'https://images.unsplash.com/photo-1769063382706-8156b3b33eac?auto=format&fit=crop&w=1200&q=88',
  bedsheetA: 'https://images.unsplash.com/photo-1631049421450-348ccd7f8949?auto=format&fit=crop&w=1200&q=88',
  bedsheetB: 'https://images.unsplash.com/photo-1627383837817-d4fc073f72e8?auto=format&fit=crop&w=1200&q=88',
  bedsheetC: 'https://images.unsplash.com/photo-1589154587853-da70e391f38a?auto=format&fit=crop&w=1200&q=88',
  bedsheetD: 'https://images.unsplash.com/photo-1648395957856-ed5a83bb200e?auto=format&fit=crop&w=1200&q=88',
  towelA: 'https://images.unsplash.com/photo-1788059317676-28c0eda2a736?auto=format&fit=crop&w=1200&q=88',
  towelB: 'https://images.unsplash.com/photo-1702432631344-3fb6b053fb3f?auto=format&fit=crop&w=1200&q=88',
  towelC: 'https://images.unsplash.com/photo-1565775913442-79337915b869?auto=format&fit=crop&w=1200&q=88',
  towelD: 'https://images.unsplash.com/photo-1620733723572-11c53f73a416?auto=format&fit=crop&w=1200&q=88',
  categoryKurtas: 'https://images.unsplash.com/photo-1742800786544-e935375035e3?auto=format&fit=crop&w=1200&q=88',
  categoryBedsheets: 'https://images.unsplash.com/photo-1572805773780-a02f06ea4798?auto=format&fit=crop&w=1200&q=88',
  categoryTowels: 'https://images.unsplash.com/photo-1766727923667-4686db7e9bcb?auto=format&fit=crop&w=1200&q=88',
  categoryCollections: 'https://images.unsplash.com/photo-1769275061356-a038b498c4a7?auto=format&fit=crop&w=1400&q=90',
};

const categories = [
  { name: 'Kurtas', eyebrow: 'Everyday elegance', count: '6 pieces', image: REAL_IMAGES.categoryKurtas, fallback: '/demo/category-kurtas.svg' },
  { name: 'Bedsheets', eyebrow: 'Comfort in every thread', count: '4 pieces', image: REAL_IMAGES.categoryBedsheets, fallback: '/demo/category-bedsheets.svg' },
  { name: 'Towels', eyebrow: 'Softness, reimagined', count: '4 pieces', image: REAL_IMAGES.categoryTowels, fallback: '/demo/category-towels.svg' },
  { name: 'Collections', eyebrow: 'Explore SUHAASA', count: '14 pieces', image: REAL_IMAGES.categoryCollections, fallback: '/demo/category-collections.svg' },
];

const fallbackProducts = [
  { id: 1, sku: 'SH-KRT-001', name: 'Sandalwood Handblock Kurta', category: 'Kurtas', price: '₹1,899', oldPrice: '₹2,299', tag: 'New', image: REAL_IMAGES.kurtaA, image2: REAL_IMAGES.kurtaB, description: 'A softly structured handblock kurta in a warm, earthy palette — designed for easy days, slow mornings and evenings that stretch a little longer.', fabric: '100% cotton', color: 'Sandalwood', sizes: ['S','M','L','XL'], stock: 18, rating: 4.8, reviews: 24, care: 'Gentle machine wash with similar colours. Dry in shade.', highlights: ['Handblock-inspired print', 'Relaxed everyday silhouette', 'Breathable cotton'] },
  { id: 2, sku: 'SH-HOM-001', name: 'Rosewood Printed Bedsheet', category: 'Bedsheets', price: '₹1,499', oldPrice: '₹1,899', tag: 'Bestseller', image: REAL_IMAGES.bedsheetA, image2: REAL_IMAGES.bedsheetB, description: 'A generous, breathable bedsheet with a quietly expressive print, made to bring warmth and texture to everyday spaces.', fabric: '100% cotton', color: 'Rosewood', sizes: ['Double'], stock: 31, rating: 4.9, reviews: 42, dimensions: '225 × 270 cm', care: 'Machine wash cold. Tumble dry low or line dry.', highlights: ['Soft breathable weave', 'Generous double-bed size', 'Easy everyday care'] },
  { id: 3, sku: 'SH-TWL-001', name: 'Clay Bloom Cotton Towel Set', category: 'Towels', price: '₹799', oldPrice: '', tag: 'Soft cotton', image: REAL_IMAGES.towelA, image2: REAL_IMAGES.towelB, description: 'A plush everyday towel set with a calm clay-inspired tone and a soft hand feel for the rituals that start and end your day.', fabric: 'Premium cotton', color: 'Clay', sizes: ['Set of 2'], stock: 27, rating: 4.7, reviews: 18, dimensions: '70 × 140 cm each', care: 'Machine wash cold. Avoid bleach.', highlights: ['Soft looped texture', 'Quick-drying weave', 'Set of two bath towels'] },
  { id: 4, sku: 'SH-KRT-002', name: 'Madder Floral Kurta Set', category: 'Kurtas', price: '₹2,299', oldPrice: '₹2,799', tag: 'Limited', image: REAL_IMAGES.kurtaB, image2: REAL_IMAGES.kurtaC, description: 'A floral kurta set with an easy silhouette and a softly vintage palette, created for occasions that call for something special without feeling overdone.', fabric: '100% cotton', color: 'Madder Rose', sizes: ['S','M','L','XL'], stock: 9, rating: 4.9, reviews: 16, care: 'Gentle machine wash. Wash dark colours separately.', highlights: ['Coordinated two-piece set', 'Soft floral motif', 'Occasion-ready comfort'] },
  { id: 5, sku: 'SH-KRT-003', name: 'Neem Leaf Block Kurta', category: 'Kurtas', price: '₹1,799', oldPrice: '', tag: 'Everyday', image: REAL_IMAGES.kurtaC, image2: REAL_IMAGES.kurtaD, description: 'A calm botanical-inspired kurta with an easy fit and a muted palette that works from morning errands to evening plans.', fabric: '100% cotton', color: 'Neem Green', sizes: ['S','M','L','XL'], stock: 22, rating: 4.6, reviews: 13, care: 'Gentle wash inside out. Dry in shade.', highlights: ['Botanical motif', 'Easy regular fit', 'Soft everyday cotton'] },
  { id: 6, sku: 'SH-KRT-004', name: 'Indigo Dusk Kurta', category: 'Kurtas', price: '₹2,099', oldPrice: '₹2,499', tag: 'New', image: REAL_IMAGES.kurtaD, image2: REAL_IMAGES.kurtaE, description: 'A deep indigo silhouette with quiet detailing and a relaxed shape, made for understated occasions.', fabric: 'Cotton slub', color: 'Indigo', sizes: ['S','M','L','XL'], stock: 14, rating: 4.8, reviews: 21, care: 'Cold wash separately. Do not wring.', highlights: ['Textured cotton slub', 'Relaxed silhouette', 'Deep indigo palette'] },
  { id: 7, sku: 'SH-KRT-005', name: 'Terracotta Bloom Kurta', category: 'Kurtas', price: '₹1,999', oldPrice: '', tag: 'Handblock', image: REAL_IMAGES.kurtaE, image2: REAL_IMAGES.kurtaF, description: 'Warm terracotta tones and a softly patterned finish give this everyday kurta its distinctive character.', fabric: 'Handblock cotton', color: 'Terracotta', sizes: ['S','M','L','XL'], stock: 12, rating: 4.7, reviews: 11, care: 'Gentle hand wash recommended. Dry in shade.', highlights: ['Handblock-inspired pattern', 'Warm terracotta tone', 'Lightweight cotton'] },
  { id: 8, sku: 'SH-KRT-006', name: 'Ivory Everyday Kurta', category: 'Kurtas', price: '₹1,699', oldPrice: '', tag: 'Essential', image: REAL_IMAGES.kurtaF, image2: REAL_IMAGES.kurtaA, description: 'An understated ivory staple designed to pair effortlessly with the rest of your wardrobe.', fabric: 'Cotton voile', color: 'Ivory', sizes: ['S','M','L','XL'], stock: 25, rating: 4.8, reviews: 29, care: 'Gentle wash. Iron on low heat.', highlights: ['Wardrobe essential', 'Lightweight voile', 'Easy-to-style neutral'] },
  { id: 9, sku: 'SH-HOM-002', name: 'Sage Garden Bedsheet', category: 'Bedsheets', price: '₹1,699', oldPrice: '₹1,999', tag: 'New', image: REAL_IMAGES.bedsheetB, image2: REAL_IMAGES.bedsheetC, description: 'A soft sage palette and gentle botanical rhythm bring a calm, lived-in feeling to the bedroom.', fabric: '100% cotton', color: 'Sage', sizes: ['Double'], stock: 19, rating: 4.8, reviews: 20, dimensions: '225 × 270 cm', care: 'Machine wash cold. Dry in shade.', highlights: ['Botanical-inspired print', 'Soft sage palette', 'Breathable cotton'] },
  { id: 10, sku: 'SH-HOM-003', name: 'Indigo Stripe Bedsheet', category: 'Bedsheets', price: '₹1,599', oldPrice: '', tag: 'Classic', image: REAL_IMAGES.bedsheetC, image2: REAL_IMAGES.bedsheetD, description: 'A timeless indigo bedding layer with subtle stripe texture for a room that feels collected rather than decorated.', fabric: 'Percale cotton', color: 'Indigo', sizes: ['Double'], stock: 16, rating: 4.7, reviews: 15, dimensions: '225 × 270 cm', care: 'Machine wash cold. Wash dark colours separately.', highlights: ['Classic stripe texture', 'Crisp percale feel', 'Everyday double-bed size'] },
  { id: 11, sku: 'SH-HOM-004', name: 'Sandstone Everyday Bedsheet', category: 'Bedsheets', price: '₹1,399', oldPrice: '₹1,699', tag: 'Best value', image: REAL_IMAGES.bedsheetD, image2: REAL_IMAGES.bedsheetA, description: 'Warm neutral bedding designed to sit quietly beneath cushions, throws and the rhythms of everyday life.', fabric: '100% cotton', color: 'Sandstone', sizes: ['Double'], stock: 34, rating: 4.6, reviews: 32, dimensions: '225 × 270 cm', care: 'Machine wash cold. Tumble dry low.', highlights: ['Warm neutral colour', 'Soft cotton weave', 'Easy-care essential'] },
  { id: 12, sku: 'SH-TWL-002', name: 'Rose Petal Towel Set', category: 'Towels', price: '₹899', oldPrice: '₹1,099', tag: 'Soft cotton', image: REAL_IMAGES.towelB, image2: REAL_IMAGES.towelC, description: 'A soft rose-toned towel set with a plush hand feel and an understated woven texture.', fabric: 'Combed cotton', color: 'Rose Petal', sizes: ['Set of 2'], stock: 21, rating: 4.8, reviews: 17, dimensions: '70 × 140 cm each', care: 'Machine wash cold. Avoid fabric softener.', highlights: ['Combed cotton', 'Plush hand feel', 'Set of two bath towels'] },
  { id: 13, sku: 'SH-TWL-003', name: 'Sage Spa Towel Set', category: 'Towels', price: '₹849', oldPrice: '', tag: 'New', image: REAL_IMAGES.towelC, image2: REAL_IMAGES.towelD, description: 'Fresh sage tones and soft loops bring a quiet spa feeling to everyday bath rituals.', fabric: 'Premium cotton', color: 'Sage', sizes: ['Set of 2'], stock: 15, rating: 4.7, reviews: 12, dimensions: '70 × 140 cm each', care: 'Machine wash cold. Dry thoroughly between uses.', highlights: ['Spa-inspired palette', 'Soft cotton loops', 'Quick everyday drying'] },
  { id: 14, sku: 'SH-TWL-004', name: 'Ivory Cloud Towel Set', category: 'Towels', price: '₹799', oldPrice: '', tag: 'Essential', image: REAL_IMAGES.towelD, image2: REAL_IMAGES.towelA, description: 'A clean ivory towel set that keeps the bathroom palette warm, simple and timeless.', fabric: 'Ring-spun cotton', color: 'Ivory', sizes: ['Set of 2'], stock: 29, rating: 4.9, reviews: 35, dimensions: '70 × 140 cm each', care: 'Machine wash cold. Avoid bleach.', highlights: ['Ring-spun cotton', 'Timeless ivory tone', 'Soft everyday essential'] },
];

const ease = [0.22, 1, 0.36, 1];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

function formatPrice(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN')}`;
}

function normalizeProduct(product) {
  const variants = Array.isArray(product.variants) ? product.variants : [];
  const images = Array.isArray(product.images) ? product.images : [];
  const activeVariants = variants.filter((variant) => variant.is_active !== false);
  const stock = activeVariants.reduce((sum, variant) => sum + Number(variant.stock_quantity || 0), 0);
  const sizes = activeVariants.map((variant) => variant.name);
  const primaryImage = images.find((image) => image.is_primary) || images[0];
  return {
    id: product.id,
    sku: product.sku,
    name: product.name,
    slug: product.slug,
    category: product.category?.name || product.category || '',
    price: formatPrice(product.price),
    oldPrice: product.compare_at_price ? formatPrice(product.compare_at_price) : '',
    tag: product.tag || (product.is_new ? 'New' : product.is_bestseller ? 'Bestseller' : 'Essential'),
    image: primaryImage?.src || primaryImage?.url || product.primary_image || '',
    image2: images.find((image) => image !== primaryImage)?.src || images[1]?.url || primaryImage?.src || '',
    description: product.description || '',
    fabric: product.fabric || '',
    color: product.color || '',
    sizes: sizes.length ? sizes : ['Standard'],
    variants: activeVariants.map((variant) => ({
      id: variant.id,
      name: variant.name,
      sku: variant.sku,
      stockQuantity: Number(variant.stock_quantity || 0),
      inStock: variant.in_stock !== false && Number(variant.stock_quantity || 0) > 0,
    })),
    stock,
    rating: Number(product.rating || 0),
    reviews: Number(product.review_count || 0),
    dimensions: product.dimensions || '',
    care: product.care || '',
    highlights: Array.isArray(product.highlights) ? product.highlights : [],
    isFeatured: Boolean(product.is_featured),
    isNew: Boolean(product.is_new),
    isBestseller: Boolean(product.is_bestseller),
  };
}

const GUEST_TOKEN_KEY = 'suhaasa_guest_token';
const ACCESS_TOKEN_KEY = 'suhaasa_access_token';
const REFRESH_TOKEN_KEY = 'suhaasa_refresh_token';

function getGuestToken() {
  let token = window.localStorage.getItem(GUEST_TOKEN_KEY);
  if (!token) {
    token = crypto.randomUUID();
    window.localStorage.setItem(GUEST_TOKEN_KEY, token);
  }
  return token;
}

async function commerceRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set('Accept', 'application/json');
  headers.set('Content-Type', 'application/json');
  headers.set('X-SUHAASA-GUEST-TOKEN', getGuestToken());
  const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY);
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`);
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `Commerce API returned ${response.status}`);
  }
  if (payload.token && payload.token !== getGuestToken()) {
    window.localStorage.setItem(GUEST_TOKEN_KEY, payload.token);
  }
  return payload;
}

function normalizeCartItem(item) {
  const product = normalizeProduct(item.product || {});
  return {
    ...product,
    cartItemId: item.id,
    variantId: item.variant_id,
    size: item.variant_name || product.sizes?.[0] || 'Standard',
    quantity: Number(item.quantity || 1),
    price: formatPrice(item.unit_price),
  };
}

function normalizeCommerceState(state) {
  return {
    ...state,
    cart: Array.isArray(state.cart) ? state.cart.map(normalizeCartItem) : [],
    wishlist_product_ids: Array.isArray(state.wishlist_product_ids) ? state.wishlist_product_ids.map(Number) : [],
  };
}

async function fetchCommerceState() {
  return normalizeCommerceState(await commerceRequest('/commerce/state/'));
}

async function authRequest(path, body) {
  const headers = new Headers({ Accept: 'application/json', 'Content-Type': 'application/json', 'X-SUHAASA-GUEST-TOKEN': getGuestToken() });
  const response = await fetch(`${API_BASE_URL}${path}`, { method: 'POST', headers, body: JSON.stringify(body) });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.detail || Object.values(payload).flat?.().join?.(' ') || `Auth API returned ${response.status}`;
    throw new Error(message);
  }
  if (payload.access) window.localStorage.setItem(ACCESS_TOKEN_KEY, payload.access);
  if (payload.refresh) window.localStorage.setItem(REFRESH_TOKEN_KEY, payload.refresh);
  return payload;
}

async function fetchCurrentUser() {
  const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY);
  if (!accessToken) return null;
  const headers = new Headers({ Accept: 'application/json', Authorization: `Bearer ${accessToken}` });
  const response = await fetch(`${API_BASE_URL}/auth/me/`, { headers });
  if (response.status === 401) {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    return null;
  }
  if (!response.ok) throw new Error(`Account API returned ${response.status}`);
  return response.json();
}

async function fetchOrders() {
  const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY);
  if (!accessToken) return [];
  const response = await fetch(`${API_BASE_URL}/orders/`, {
    headers: { Accept: 'application/json', Authorization: `Bearer ${accessToken}` },
  });
  const payload = await response.json().catch(() => []);
  if (!response.ok) throw new Error(payload.detail || `Orders API returned ${response.status}`);
  return Array.isArray(payload) ? payload : payload.results || [];
}

async function fetchOrderDetail(orderNumber) {
  return commerceRequest(`/orders/${encodeURIComponent(orderNumber)}/`);
}

async function fetchAddresses() {
  return commerceRequest('/auth/addresses/');
}

async function fetchProducts() {
  const response = await fetch(`${API_BASE_URL}/products/`);
  if (!response.ok) throw new Error(`Product API returned ${response.status}`);
  const payload = await response.json();
  const items = Array.isArray(payload) ? payload : payload.results || [];
  const detailed = await Promise.all(items.map(async (item) => {
    const detailResponse = await fetch(`${API_BASE_URL}/products/${item.slug}/`);
    if (!detailResponse.ok) return item;
    return detailResponse.json();
  }));
  return detailed.map(normalizeProduct);
}


async function loadRazorpayScript() {
  if (window.Razorpay) return true;
  await new Promise((resolve, reject) => {
    const existing = document.querySelector('script[data-razorpay-checkout]');
    if (existing) {
      existing.addEventListener('load', resolve, { once: true });
      existing.addEventListener('error', reject, { once: true });
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    script.dataset.razorpayCheckout = 'true';
    script.onload = resolve;
    script.onerror = () => reject(new Error('Unable to load secure payment checkout. Please check your internet connection.'));
    document.body.appendChild(script);
  });
  return Boolean(window.Razorpay);
}

function imageFallback(event, fallback) {
  if (event.currentTarget.dataset.fallbackApplied) return;
  event.currentTarget.dataset.fallbackApplied = 'true';
  event.currentTarget.src = fallback;
}

function App() {
  const [dark, setDark] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [liked, setLiked] = useState([]);
  const [activeProduct, setActiveProduct] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [view, setView] = useState('home');
  const [shopCategory, setShopCategory] = useState('All');
  const [sortBy, setSortBy] = useState('featured');
  const [catalogFilter, setCatalogFilter] = useState('All');
  const [cartItems, setCartItems] = useState([]);
  const [products, setProducts] = useState(fallbackProducts);
  const [commerceReady, setCommerceReady] = useState(false);
  const [user, setUser] = useState(null);
  const [accountOpen, setAccountOpen] = useState(false);
  const [checkoutAfterAuth, setCheckoutAfterAuth] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? 'dusk' : 'light';
  }, [dark]);

  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchProducts(), fetchCommerceState(), fetchCurrentUser()]).then(([items, state, currentUser]) => {
      if (cancelled) return;
      if (items.length) setProducts(items);
      setCartItems(state.cart || []);
      setLiked(state.wishlist_product_ids || []);
      setUser(currentUser?.user || null);
      if (currentUser?.commerce) {
        setCartItems(normalizeCommerceState(currentUser.commerce).cart || []);
        setLiked(currentUser.commerce.wishlist_product_ids || []);
      }
      setCommerceReady(true);
    }).catch((error) => {
      console.warn('SUHAASA commerce API unavailable; keeping local UI state until the API is reachable.', error);
      if (!cancelled) setCommerceReady(false);
    });
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    document.body.style.overflow = menuOpen || cartOpen || searchOpen || activeProduct ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [menuOpen, cartOpen, searchOpen, activeProduct]);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key !== 'Escape') return;
      setMenuOpen(false);
      setCartOpen(false);
      setSearchOpen(false);
      setActiveProduct(null);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const likedCount = liked.length;
  const openWishlist = () => {
    setShopCategory('All');
    setCatalogFilter('Wishlist');
    setView('shop');
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const openStory = () => {
    setView('home');
    setMenuOpen(false);
    requestAnimationFrame(() => document.getElementById('story')?.scrollIntoView({ behavior: 'smooth' }));
  };
  const openShop = (category = 'All') => {
    setShopCategory(category);
    setView('shop');
    setMenuOpen(false);
    setSearchOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const toggleLike = async (id) => {
    const isLiked = liked.includes(id);
    setLiked((current) => isLiked ? current.filter((x) => x !== id) : [...current, id]);
    if (!commerceReady) return;
    try {
      const state = isLiked
        ? await commerceRequest(`/commerce/wishlist/items/${id}/`, { method: 'DELETE' })
        : await commerceRequest('/commerce/wishlist/items/', { method: 'POST', body: JSON.stringify({ product_id: id }) });
      setLiked(state.wishlist_product_ids || []);
    } catch (error) {
      setLiked((current) => isLiked ? [...current, id] : current.filter((x) => x !== id));
      console.error(error);
    }
  };

  const addToCartLock = useRef(new Set());

  const addToCart = async (product, options = {}) => {
    const size = options.size || product.sizes?.[0] || 'Standard';
    const variant = product.variants?.find((item) => item.name === size) || product.variants?.[0];
    const quantity = Math.max(1, Number(options.quantity || 1));
    if (!commerceReady || !variant) return;

    // Prevent a double submission from a double-click, rapid click, or an
    // overlapping React event while the previous Add-to-bag request is pending.
    const lockKey = `${variant.id}:${size}`;
    if (addToCartLock.current.has(lockKey)) return;
    addToCartLock.current.add(lockKey);

    try {
      const state = await commerceRequest('/commerce/cart/items/', {
        method: 'POST',
        body: JSON.stringify({ variant_id: variant.id, quantity }),
      });
      setCartItems((state.cart || []).map(normalizeCartItem));
      setActiveProduct(null);
      setCartOpen(true);

      // Keep the action locked briefly after a successful response as well.
      // This closes the small race where a very fast double-click happens
      // after the first request has completed but before the second click
      // event is delivered. A later deliberate click still works normally.
      window.setTimeout(() => addToCartLock.current.delete(lockKey), 750);
    } catch (error) {
      addToCartLock.current.delete(lockKey);
      window.alert(error.message);
    }
  };

  const updateCartQuantity = async (itemId, quantity) => {
    if (!commerceReady) return;
    try {
      const state = await commerceRequest(`/commerce/cart/items/${itemId}/`, {
        method: 'PATCH',
        body: JSON.stringify({ quantity }),
      });
      setCartItems((state.cart || []).map(normalizeCartItem));
    } catch (error) {
      window.alert(error.message);
    }
  };

  const removeCartItem = async (itemId) => {
    if (!commerceReady) return;
    try {
      const state = await commerceRequest(`/commerce/cart/items/${itemId}/`, { method: 'DELETE' });
      setCartItems((state.cart || []).map(normalizeCartItem));
    } catch (error) {
      console.error(error);
    }
  };

  const handleAuthSuccess = (payload) => {
    setUser(payload.user);
    const state = normalizeCommerceState(payload.commerce || {});
    setCartItems(state.cart || []);
    setLiked(state.wishlist_product_ids || []);
    setCommerceReady(true);
    setAccountOpen(false);
    if (checkoutAfterAuth) {
      setCheckoutAfterAuth(false);
      setView('checkout');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const startCheckout = () => {
    setCartOpen(false);
    if (!user) {
      setCheckoutAfterAuth(true);
      setAccountOpen(true);
      return;
    }
    setView('checkout');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLogout = () => {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    setUser(null);
    setAccountOpen(false);
    fetchCommerceState().then((state) => {
      setCartItems(state.cart || []);
      setLiked(state.wishlist_product_ids || []);
    }).catch(() => {});
  };

  return (
    <div className="site-shell">
      <AnnouncementBar />
      <Header
        dark={dark}
        setDark={setDark}
        menuOpen={menuOpen}
        setMenuOpen={setMenuOpen}
        setCartOpen={setCartOpen}
        setSearchOpen={(open) => { setSearchOpen(open); if (open) setSearchQuery(''); }}
        user={user}
        onAccount={() => setAccountOpen(true)}
        likedCount={likedCount}
        cartCount={cartItems.reduce((sum, item) => sum + item.quantity, 0)}
        onShop={() => openShop('All')}
        onKurtas={() => openShop('Kurtas')}
        onHomeTextiles={() => openShop('Bedsheets')}
        onWishlist={openWishlist}
        onStory={openStory}
        onHome={() => { setView('home'); setMenuOpen(false); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
      />

      <AnimatePresence>{searchOpen && <SearchOverlay products={products} query={searchQuery} setQuery={setSearchQuery} onClose={() => setSearchOpen(false)} onCategory={(category) => openShop(category)} onProduct={(product) => { setSelectedProduct(product); setSearchOpen(false); setView('product'); window.scrollTo({ top: 0, behavior: 'smooth' }); }} />}</AnimatePresence>
      <AnimatePresence>{menuOpen && <MobileMenu onClose={() => setMenuOpen(false)} onShop={() => openShop('All')} onKurtas={() => openShop('Kurtas')} onHomeTextiles={() => openShop('Bedsheets')} onWishlist={openWishlist} onStory={openStory} onHome={() => { setView('home'); setMenuOpen(false); window.scrollTo({ top: 0, behavior: 'smooth' }); }} />}</AnimatePresence>

      <main>
        <AnimatePresence mode="wait">
          {view === 'shop' ? (
            <motion.div key="shop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <ShopPage
                products={products}
                category={shopCategory}
                setCategory={setShopCategory}
                catalogFilter={catalogFilter}
                setCatalogFilter={setCatalogFilter}
                sortBy={sortBy}
                setSortBy={setSortBy}
                liked={liked}
                toggleLike={toggleLike}
                onQuickView={setActiveProduct}
                onProductDetail={(product) => { setSelectedProduct(product); setView('product'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                onBack={() => { setView('home'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
              />
            </motion.div>
          ) : view === 'checkout' ? (
            <motion.div key="checkout" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
              <CheckoutPage items={cartItems} setItems={setCartItems} user={user} onBack={() => { setView('shop'); window.scrollTo({ top: 0, behavior: 'smooth' }); }} />
            </motion.div>
          ) : view === 'product' && selectedProduct ? (
            <motion.div key="product" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
              <ProductDetail
                product={selectedProduct}
                liked={liked.includes(selectedProduct.id)}
                onToggleLike={() => toggleLike(selectedProduct.id)}
                onAdd={addToCart}
                onBack={() => { setView('shop'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                onQuickView={setActiveProduct}
              />
            </motion.div>
          ) : (
            <motion.div key="home" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <Hero onShop={() => { setCatalogFilter('All'); setView('shop'); }} />
              <Marquee />
              <CategorySection onCategory={(name) => { setShopCategory(name); setView('shop'); }} />
              <StorySection />
              <ProductSection products={products.filter((product) => [1,2,3,4,6,9,12,14].includes(product.id))} liked={liked} toggleLike={toggleLike} onQuickView={setActiveProduct} onProductDetail={(product) => { setSelectedProduct(product); setView('product'); window.scrollTo({ top: 0, behavior: 'smooth' }); }} onShop={() => setView('shop')} />
              <CraftSection />
              <Newsletter />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <Footer />

      <AccountModal open={accountOpen} user={user} onClose={() => { setAccountOpen(false); setCheckoutAfterAuth(false); }} onSuccess={handleAuthSuccess} onUserUpdate={(nextUser) => setUser(nextUser)} onCommerceUpdate={(state) => { const next = normalizeCommerceState(state || {}); setCartItems(next.cart || []); setLiked(next.wishlist_product_ids || []); }} onLogout={handleLogout} />
      <AnimatePresence>
        {cartOpen && <CartDrawer items={cartItems} onUpdateQuantity={updateCartQuantity} onRemove={removeCartItem} onClose={() => setCartOpen(false)} onShop={() => { setCartOpen(false); setView('shop'); }} onCheckout={startCheckout} />}
        {activeProduct && <ProductModal product={activeProduct} onClose={() => setActiveProduct(null)} onAdd={addToCart} />}
      </AnimatePresence>
    </div>
  );
}

function AnnouncementBar() {
  return (
    <div className="announcement">
      <span>Complimentary shipping on orders above ₹1,499</span>
      <span className="announcement-dot">·</span>
      <span>Made with a little more care</span>
    </div>
  );
}

function AccountModal({ open, user, onClose, onSuccess, onUserUpdate, onCommerceUpdate, onLogout }) {
  const [section, setSection] = useState('overview');
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [profile, setProfile] = useState({ first_name: '', last_name: '', phone: '' });
  const [addressForm, setAddressForm] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => {
    if (!open) return;
    setSection('overview'); setSelectedOrder(null); setAddressForm(null); setError(''); setNotice('');
    setProfile({ first_name: user?.first_name || '', last_name: user?.last_name || '', phone: '' });
  }, [open, user]);

  if (!open || !user) {
    if (!open) return null;
    return <AccountAuthModal open={open} onSuccess={onSuccess} onClose={onClose} />;
  }

  const loadOrders = async () => {
    setBusy(true); setError('');
    try { setOrders(await fetchOrders()); setSection('orders'); }
    catch (err) { setError(err.message || 'Unable to load your orders.'); }
    finally { setBusy(false); }
  };

  const loadOrder = async (orderNumber) => {
    setBusy(true); setError('');
    try { setSelectedOrder(await fetchOrderDetail(orderNumber)); setSection('order'); }
    catch (err) { setError(err.message || 'Unable to load this order.'); }
    finally { setBusy(false); }
  };

  const loadAddresses = async () => {
    setBusy(true); setError('');
    try { setAddresses(await fetchAddresses()); setSection('addresses'); }
    catch (err) { setError(err.message || 'Unable to load your addresses.'); }
    finally { setBusy(false); }
  };

  const loadProfile = async () => {
    setBusy(true); setError('');
    try {
      const payload = await commerceRequest('/auth/me/');
      setProfile({ first_name: payload.user?.first_name || '', last_name: payload.user?.last_name || '', phone: payload.profile?.phone || '' });
      setSection('profile');
    } catch (err) { setError(err.message || 'Unable to load your profile.'); }
    finally { setBusy(false); }
  };

  const saveProfile = async (event) => {
    event.preventDefault(); setBusy(true); setError(''); setNotice('');
    try {
      const payload = await commerceRequest('/auth/me/', { method: 'PATCH', body: JSON.stringify(profile) });
      onUserUpdate(payload.user);
      setNotice('Your profile has been saved.');
    } catch (err) { setError(err.message || 'Unable to save your profile.'); }
    finally { setBusy(false); }
  };

  const saveAddress = async (event) => {
    event.preventDefault(); setBusy(true); setError(''); setNotice('');
    try {
      const path = addressForm.id ? `/auth/addresses/${addressForm.id}/` : '/auth/addresses/';
      const method = addressForm.id ? 'PATCH' : 'POST';
      await commerceRequest(path, { method, body: JSON.stringify(addressForm) });
      setAddresses(await fetchAddresses()); setAddressForm(null); setNotice('Address saved.');
    } catch (err) { setError(err.message || 'Unable to save the address.'); }
    finally { setBusy(false); }
  };

  const deleteAddress = async (id) => {
    if (!window.confirm('Remove this saved address?')) return;
    setBusy(true); setError('');
    try { await commerceRequest(`/auth/addresses/${id}/`, { method: 'DELETE' }); setAddresses(await fetchAddresses()); }
    catch (err) { setError(err.message || 'Unable to remove the address.'); }
    finally { setBusy(false); }
  };

  const reorder = async (orderNumber) => {
    setBusy(true); setError(''); setNotice('');
    try {
      const result = await commerceRequest(`/orders/${encodeURIComponent(orderNumber)}/reorder/`, { method: 'POST', body: JSON.stringify({}) });
      onCommerceUpdate(result.commerce);
      setNotice(result.skipped?.length ? `Added ${result.added.length} item(s). ${result.skipped.length} item(s) could not be added.` : 'Previous items were added to your bag.');
      setSection('orders');
    } catch (err) { setError(err.message || 'Unable to reorder this purchase.'); }
    finally { setBusy(false); }
  };

  const statusSteps = ['placed', 'processing', 'shipped', 'delivered'];
  const statusIndex = selectedOrder ? statusSteps.indexOf(selectedOrder.status) : -1;

  const renderNav = () => <div className="account-nav">
    <button className={section === 'overview' ? 'active' : ''} onClick={() => setSection('overview')}>Overview</button>
    <button className={section === 'orders' || section === 'order' ? 'active' : ''} onClick={loadOrders}>Orders</button>
    <button className={section === 'profile' ? 'active' : ''} onClick={loadProfile}>Profile</button>
    <button className={section === 'addresses' ? 'active' : ''} onClick={loadAddresses}>Addresses</button>
  </div>;

  return <div className="account-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
    <motion.div className="account-modal account-dashboard-modal" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
      <button className="icon-btn account-close" onClick={onClose}><X size={19} /></button>
      <span className="kicker">Your SUHAASA account</span>
      <h2>{user.first_name ? `Hello, ${user.first_name}.` : 'Your account.'}</h2>
      <p>{user.email}</p>
      {renderNav()}
      {error && <div className="account-error">{error}</div>}
      {notice && <div className="account-notice">{notice}</div>}

      {section === 'overview' && <div className="account-panel-grid">
        <button className="account-panel-card" onClick={loadOrders}><span className="kicker">Purchases</span><strong>My orders</strong><small>View order history, payment and delivery status.</small></button>
        <button className="account-panel-card" onClick={loadProfile}><span className="kicker">Personal</span><strong>Profile</strong><small>Keep your name and phone number up to date.</small></button>
        <button className="account-panel-card" onClick={loadAddresses}><span className="kicker">Delivery</span><strong>Saved addresses</strong><small>Manage home, work and other delivery addresses.</small></button>
      </div>}

      {section === 'orders' && <div className="account-section">
        <div className="account-section-head"><div><span className="kicker">Purchase history</span><h3>My <em>orders.</em></h3></div><span className="account-count">{orders.length} {orders.length === 1 ? 'order' : 'orders'}</span></div>
        {busy && <div className="account-loading">Loading your orders…</div>}
        {!busy && !orders.length && <div className="orders-empty"><ShoppingBag size={24}/><p>You haven't placed an order yet.</p></div>}
        <div className="orders-list">{orders.map(order => <article className="order-card" key={order.id}>
          <button className="order-card-main" onClick={() => loadOrder(order.order_number)}>
            <div className="order-card-head"><div><span className="kicker">{order.order_number}</span><small>{new Date(order.created_at).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'})}</small></div><strong>₹{Number(order.total).toLocaleString('en-IN')}</strong></div>
            <div className="order-card-status"><span className={`order-status status-${order.status}`}>{order.status.replaceAll('_',' ')}</span><span className={`order-status payment-${order.payment_status}`}>{order.payment_status}</span></div>
            <div className="order-card-items">{order.items.slice(0,3).map(item => <div key={item.id}><span>{item.product_name} · {item.variant_name} × {item.quantity}</span><strong>₹{Number(item.line_total).toLocaleString('en-IN')}</strong></div>)}{order.items.length>3 && <small>+ {order.items.length-3} more item(s)</small>}</div>
          </button>
          <button className="text-link order-view-link" onClick={() => loadOrder(order.order_number)}>View details <ArrowRight size={14}/></button>
        </article>)}</div>
      </div>}

      {section === 'order' && selectedOrder && <div className="account-section">
        <button className="account-back-link" onClick={() => setSection('orders')}><ArrowRight size={15} style={{transform:'rotate(180deg)'}}/> All orders</button>
        <div className="account-section-head"><div><span className="kicker">{selectedOrder.order_number}</span><h3>Order <em>details.</em></h3></div><button className="account-secondary-btn compact" onClick={() => reorder(selectedOrder.order_number)} disabled={busy}>{busy ? 'Working…' : 'Reorder'}</button></div>
        <div className="order-timeline">{statusSteps.map((step,index) => <div className={`timeline-step ${selectedOrder.status === 'cancelled' ? '' : index <= statusIndex ? 'done' : ''}`} key={step}><span>{index+1}</span><small>{step}</small></div>)}</div>
        {selectedOrder.status === 'cancelled' && <div className="order-cancelled-note">This order was cancelled.</div>}
        <div className="order-detail-grid"><div className="order-detail-card"><span className="kicker">Items</span>{selectedOrder.items.map(item=><div className="detail-item" key={item.id}><img src={item.image_url || '/demo/product-placeholder.svg'} alt=""/><div><strong>{item.product_name}</strong><small>{item.variant_name} · Qty {item.quantity}</small><small>₹{Number(item.unit_price).toLocaleString('en-IN')} each</small></div><b>₹{Number(item.line_total).toLocaleString('en-IN')}</b></div>)}</div>
        <div className="order-detail-side"><div className="order-detail-card"><span className="kicker">Delivery</span><p><strong>{selectedOrder.full_name}</strong><br/>{selectedOrder.address_line1}{selectedOrder.address_line2 ? `, ${selectedOrder.address_line2}` : ''}<br/>{selectedOrder.city}, {selectedOrder.state} — {selectedOrder.pincode}<br/>{selectedOrder.phone}</p><small>{selectedOrder.shipping_method === 'express' ? 'Express delivery' : 'Standard delivery'}</small></div>
        <div className="order-detail-card"><span className="kicker">Payment</span><p><strong>{selectedOrder.payment_status === 'paid' ? 'Paid' : selectedOrder.payment_status}</strong><br/>{selectedOrder.payment?.gateway ? selectedOrder.payment.gateway : 'Online payment'}{selectedOrder.payment?.gateway_payment_id ? ` · ${selectedOrder.payment.gateway_payment_id}` : ''}</p></div>
        <div className="order-detail-card order-total-card"><div><span>Subtotal</span><b>₹{Number(selectedOrder.subtotal).toLocaleString('en-IN')}</b></div><div><span>Shipping</span><b>{Number(selectedOrder.shipping_amount) ? `₹${Number(selectedOrder.shipping_amount).toLocaleString('en-IN')}` : 'Free'}</b></div><div className="grand"><span>Total</span><b>₹{Number(selectedOrder.total).toLocaleString('en-IN')}</b></div></div></div></div>
      </div>}

      {section === 'profile' && <form className="account-section account-form profile-form" onSubmit={saveProfile}><div className="account-section-head"><div><span className="kicker">Personal information</span><h3>Your <em>profile.</em></h3></div></div><div className="account-name-row"><input value={profile.first_name} onChange={e=>setProfile({...profile,first_name:e.target.value})} placeholder="First name" autoComplete="given-name"/><input value={profile.last_name} onChange={e=>setProfile({...profile,last_name:e.target.value})} placeholder="Last name" autoComplete="family-name"/></div><input value={user.email || ''} readOnly aria-label="Email address"/><input value={profile.phone} onChange={e=>setProfile({...profile,phone:e.target.value})} placeholder="Phone number" autoComplete="tel"/><small className="field-note">Your sign-in email cannot be changed here because it is the identity used for your account.</small><button className="primary-btn" disabled={busy}>{busy ? 'Saving…' : 'Save profile'} <Check size={16}/></button></form>}

      {section === 'addresses' && <div className="account-section"><div className="account-section-head"><div><span className="kicker">Delivery details</span><h3>Saved <em>addresses.</em></h3></div><button className="primary-btn compact" onClick={()=>setAddressForm({label:'home',full_name:`${user.first_name||''} ${user.last_name||''}`.trim(),phone:'',address_line1:'',address_line2:'',city:'',state:'',pincode:'',is_default:addresses.length===0})}>Add address</button></div>{!addresses.length && !addressForm && <div className="orders-empty"><p>No saved addresses yet.</p></div>}<div className="address-list">{addresses.map(address=><article className="address-card" key={address.id}><div><span className="kicker">{address.label}{address.is_default ? ' · Default' : ''}</span><strong>{address.full_name}</strong><p>{address.address_line1}{address.address_line2 ? `, ${address.address_line2}` : ''}<br/>{address.city}, {address.state} — {address.pincode}<br/>{address.phone}</p></div><div className="address-actions"><button className="text-link" onClick={()=>setAddressForm({...address})}>Edit</button><button className="text-link danger-link" onClick={()=>deleteAddress(address.id)} disabled={busy}>Remove</button></div></article>)}</div>{addressForm && <form className="address-editor account-form" onSubmit={saveAddress}><div className="account-section-head"><div><span className="kicker">{addressForm.id ? 'Edit address' : 'New address'}</span><h3>{addressForm.id ? 'Update it.' : 'Add one.'}</h3></div></div><div className="form-grid account-address-grid"><label>Label<select value={addressForm.label} onChange={e=>setAddressForm({...addressForm,label:e.target.value})}><option value="home">Home</option><option value="work">Work</option><option value="other">Other</option></select></label><label>Full name<input value={addressForm.full_name} onChange={e=>setAddressForm({...addressForm,full_name:e.target.value})} required/></label><label>Phone<input value={addressForm.phone} onChange={e=>setAddressForm({...addressForm,phone:e.target.value})} required/></label><label className="full-field">Address<input value={addressForm.address_line1} onChange={e=>setAddressForm({...addressForm,address_line1:e.target.value})} required/></label><label className="full-field">Apartment / locality<input value={addressForm.address_line2} onChange={e=>setAddressForm({...addressForm,address_line2:e.target.value})}/></label><label>City<input value={addressForm.city} onChange={e=>setAddressForm({...addressForm,city:e.target.value})} required/></label><label>State<input value={addressForm.state} onChange={e=>setAddressForm({...addressForm,state:e.target.value})} required/></label><label>PIN code<input value={addressForm.pincode} onChange={e=>setAddressForm({...addressForm,pincode:e.target.value})} inputMode="numeric" maxLength={6} required/></label></div><label className="address-default"><input type="checkbox" checked={!!addressForm.is_default} onChange={e=>setAddressForm({...addressForm,is_default:e.target.checked})}/> Make this my default address</label><div className="address-editor-actions"><button type="button" className="account-secondary-btn compact" onClick={()=>setAddressForm(null)}>Cancel</button><button className="primary-btn compact" disabled={busy}>{busy?'Saving…':'Save address'}</button></div></form>}</div>}

      <div className="account-footer-actions"><button className="account-secondary-btn" onClick={onLogout}>Sign out</button></div>
    </motion.div>
  </div>;
}

function AccountAuthModal({ open, onSuccess, onClose }) {
  const [mode, setMode] = useState('login'); const [email,setEmail]=useState(''); const [password,setPassword]=useState(''); const [firstName,setFirstName]=useState(''); const [lastName,setLastName]=useState(''); const [busy,setBusy]=useState(false); const [error,setError]=useState('');
  if (!open) return null;
  const submit=async(e)=>{e.preventDefault();setBusy(true);setError('');try{const payload=await authRequest(mode==='login'?'/auth/login/':'/auth/register/',mode==='login'?{email,password}:{email,password,first_name:firstName,last_name:lastName});onSuccess(payload);}catch(err){setError(err.message);}finally{setBusy(false);}};
  return <div className="account-backdrop" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><motion.div className="account-modal" initial={{opacity:0,y:18}} animate={{opacity:1,y:0}}><button className="icon-btn account-close" onClick={onClose}><X size={19}/></button><span className="kicker">SUHAASA account</span><h2>{mode==='login'?'Welcome back.':'Create your account.'}</h2><p>{mode==='login'?'Sign in to keep your bag and wishlist with you.':'Create an account to save your bag, wishlist and orders.'}</p><form className="account-form" onSubmit={submit}>{mode==='register'&&<div className="account-name-row"><input value={firstName} onChange={e=>setFirstName(e.target.value)} placeholder="First name" autoComplete="given-name"/><input value={lastName} onChange={e=>setLastName(e.target.value)} placeholder="Last name" autoComplete="family-name"/></div>}<input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email address" autoComplete="email" required/><input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" autoComplete={mode==='login'?'current-password':'new-password'} minLength={8} required/>{error&&<div className="account-error">{error}</div>}<button className="primary-btn full" disabled={busy}>{busy?'Please wait…':mode==='login'?'Sign in':'Create account'} <ArrowRight size={16}/></button></form><button className="account-switch" onClick={()=>setMode(mode==='login'?'register':'login')}>{mode==='login'?'New to SUHAASA? Create an account':'Already have an account? Sign in'}</button></motion.div></div>;
}

function Header({ dark, setDark, menuOpen, setMenuOpen, setCartOpen, setSearchOpen, likedCount, cartCount, onShop, onKurtas, onHomeTextiles, onWishlist, onStory, onHome, user, onAccount }) {
  return (
    <header className="header">
      <button className="mobile-menu-btn icon-btn" onClick={() => setMenuOpen(!menuOpen)} aria-label="Open menu">
        {menuOpen ? <X size={21} /> : <Menu size={21} />}
      </button>
      <button className="brand-mark brand-button" onClick={onHome} aria-label="SUHAASA home">
        <img src="/suhaasa-logo.jpg" alt="SUHAASA logo" />
      </button>
      <nav className="desktop-nav">
        <button onClick={onHome}>Home</button>
        <button onClick={onShop}>Shop</button>
        <button onClick={onKurtas}>Kurtas</button>
        <button onClick={onHomeTextiles}>Home Textiles</button>
        <button onClick={onStory}>Our Story</button>
      </nav>
      <div className="header-actions">
        <button className="icon-btn" onClick={() => setSearchOpen(true)} aria-label="Search"><Search size={19} /></button>
        <button className="icon-btn heart-btn" onClick={onWishlist} aria-label={`Wishlist${likedCount ? ` (${likedCount})` : ''}` }>
          <Heart size={19} fill={likedCount ? 'currentColor' : 'none'} />
          {likedCount > 0 && <span className="tiny-badge">{likedCount}</span>}
        </button>
        <button className="icon-btn" onClick={onAccount} aria-label={user ? 'Open account' : 'Sign in'}><User size={18} /></button>
        <button className="icon-btn" onClick={() => setDark(!dark)} aria-label="Toggle theme">
          <AnimatePresence mode="wait" initial={false}>
            <motion.span key={dark ? 'sun' : 'moon'} initial={{ rotate: -45, opacity: 0, scale: .6 }} animate={{ rotate: 0, opacity: 1, scale: 1 }} exit={{ rotate: 45, opacity: 0, scale: .6 }}>
              {dark ? <Sun size={18} /> : <Moon size={18} />}
            </motion.span>
          </AnimatePresence>
        </button>
        <button className="cart-btn" onClick={() => setCartOpen(true)} aria-label="Open cart">
          <ShoppingBag size={19} />
          <span>Bag</span>
          <span className="cart-count">{cartCount}</span>
        </button>
      </div>
    </header>
  );
}

function Hero({ onShop }) {
  return (
    <section className="hero" id="top">
      <div className="hero-copy">
        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .7, ease }} className="eyebrow"><Sparkles size={13} /> The new season edit</motion.div>
        <motion.h1 initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .9, delay: .1, ease }}>
          Woven with <em>grace.</em>
          <br />Made for living.
        </motion.h1>
        <motion.p initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .7, delay: .22, ease }}>
          Timeless Indian textiles, thoughtful silhouettes and everyday comforts — curated for homes and wardrobes that feel like you.
        </motion.p>
        <motion.div className="hero-actions" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .7, delay: .34, ease }}>
          <button className="primary-btn" onClick={onShop}>Explore collection <ArrowRight size={17} /></button>
          <a className="text-link" href="#story">Discover SUHAASA <ArrowDownRight size={16} /></a>
        </motion.div>
      </div>
      <motion.div className="hero-visual" initial={{ opacity: 0, scale: .97 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 1.1, ease }}>
        <div className="hero-image" />
        <div className="hero-stamp">SUHAASA<br /><span>Est. 2026</span></div>
        <div className="hero-caption"><span>01</span><span>Quiet luxury, Indian soul.</span></div>
      </motion.div>
      <div className="hero-bottom-note">Scroll to explore <ChevronDown size={16} /></div>
    </section>
  );
}

function Marquee() {
  return <div className="marquee-wrap"><div className="marquee-track">{Array.from({ length: 2 }).map((_, i) => <React.Fragment key={i}><span>CRAFTED WITH INTENTION</span><b>✦</b><span>TIMELESS TEXTILES</span><b>✦</b><span>EVERYDAY ELEGANCE</span><b>✦</b><span>SUHAASA</span><b>✦</b></React.Fragment>)}</div></div>;
}

function CategorySection({ onCategory }) {
  return (
    <section className="section categories-section" id="collections">
      <div className="section-heading split-heading">
        <div><span className="kicker">01 / Explore</span><h2>Made for every<br /><em>corner of life.</em></h2></div>
        <p>From the first layer of your morning to the last detail of your home, discover pieces designed to live beautifully.</p>
      </div>
      <div className="category-grid">
        {categories.map((category, index) => (
          <motion.button onClick={() => onCategory(category.name === 'Collections' ? 'All' : category.name)} className={`category-card category-${index + 1}`} key={category.name} whileHover="hover">
            <motion.div className="category-image" style={{ backgroundImage: `url(${category.image}), url(${category.fallback})` }} variants={{ scale: 1.03 }} transition={{ duration: .7, ease }} />
            <div className="image-shade" />
            <div className="category-meta"><span>{category.eyebrow}</span><h3>{category.name}</h3><small>{category.count}</small></div>
            <motion.div className="round-arrow" variants={{ x: 4, y: -4 }}><ArrowUpRight size={17} /></motion.div>
          </motion.button>
        ))}
      </div>
    </section>
  );
}

function StorySection() {
  return (
    <section className="story section" id="story">
      <div className="story-image"><div className="story-image-label">02 / The SUHAASA story</div><div className="story-quote">“The beauty is in<br /><em>the everyday.</em>”</div></div>
      <div className="story-copy">
        <span className="kicker">02 / Our story</span>
        <h2>Tradition,<br /><em>softened for today.</em></h2>
        <p>SUHAASA is a celebration of Indian craft, familiar textures and the quiet details that make a space — or an outfit — feel personal.</p>
        <p>We look for honest materials, gentle colours and designs that don't need to shout to be noticed.</p>
        <a className="underlined-link" href="#featured">More about SUHAASA <ArrowRight size={15} /></a>
      </div>
    </section>
  );
}

function ProductSection({ products, liked, toggleLike, onQuickView, onShop, onProductDetail }) {
  return (
    <section className="section product-section" id="featured">
      <div className="section-heading split-heading product-heading">
        <div><span className="kicker">03 / Curated</span><h2>Quietly <em>special.</em></h2></div>
        <button className="underlined-link link-button" onClick={onShop}>View all products <ArrowRight size={15} /></button>
      </div>
      <div className="product-grid">
        {products.map((product, index) => (
          <motion.article className="product-card" key={product.id} initial={{ opacity: 0, y: 22 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-60px' }} transition={{ duration: .65, delay: index * .07, ease }}>
            <div className="product-image-wrap" onClick={() => onProductDetail(product)}>
              <img src={product.image} onError={(e) => imageFallback(e, '/demo/sandalwood-kurta.svg')} alt={product.name} />
              <span className="product-tag">{product.tag}</span>
              <button className={`wishlist-btn ${liked.includes(product.id) ? 'liked' : ''}`} onClick={(e) => { e.stopPropagation(); toggleLike(product.id); }} aria-label={`${liked.includes(product.id) ? 'Remove' : 'Add'} ${product.name} ${liked.includes(product.id) ? 'from' : 'to'} wishlist`}><Heart size={18} fill={liked.includes(product.id) ? 'currentColor' : 'none'} /></button>
              <button className="quick-view" aria-label={`Quick view ${product.name}`} onClick={(e) => { e.stopPropagation(); onQuickView(product); }}>Quick view <ArrowUpRight size={14} /></button>
            </div>
            <div className="product-info">
              <div><span className="product-category">{product.category}</span><h3>{product.name}</h3><small className="product-rating">★ {product.rating} <span>({product.reviews})</span></small></div>
              <div className="price"><strong>{product.price}</strong>{product.oldPrice && <del>{product.oldPrice}</del>}</div>
            </div>
          </motion.article>
        ))}
      </div>
    </section>
  );
}

function CraftSection() {
  return (
    <section className="craft section">
      <div className="craft-inner">
        <span className="kicker">04 / The SUHAASA way</span>
        <h2>Good things take<br /><em>a little time.</em></h2>
        <div className="craft-points">
          <div><span>01</span><h3>Thoughtful materials</h3><p>Natural-feel fabrics chosen for comfort and everyday use.</p></div>
          <div><span>02</span><h3>Considered design</h3><p>Quiet patterns and silhouettes made to stay relevant.</p></div>
          <div><span>03</span><h3>Made to be lived in</h3><p>Pieces that become more familiar with every use.</p></div>
        </div>
      </div>
    </section>
  );
}

function Newsletter() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const submit = (e) => { e.preventDefault(); if (email.trim()) setSubmitted(true); };
  return (
    <section className="newsletter section" id="newsletter">
      <div className="newsletter-card">
        <div><span className="kicker">05 / Stay awhile</span><h2>A little SUHAASA,<br /><em>straight to your inbox.</em></h2></div>
        <div className="newsletter-form-wrap">
          <p>New collections, thoughtful finds and occasional notes from us. No noise.</p>
          <form onSubmit={submit} className="newsletter-form">
            <input type="email" placeholder="Your email address" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <button type="submit" aria-label="Subscribe">{submitted ? <Check size={18} /> : <ArrowRight size={18} />}</button>
          </form>
          {submitted && <small className="success-note">You're on the list. Thank you.</small>}
        </div>
      </div>
    </section>
  );
}

function Footer() {
  const [info, setInfo] = useState(null);
  useEffect(() => {
    if (!info) return undefined;
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const onKeyDown = (event) => { if (event.key === 'Escape') setInfo(null); };
    window.addEventListener('keydown', onKeyDown);
    return () => { document.body.style.overflow = previous; window.removeEventListener('keydown', onKeyDown); };
  }, [info]);
  const close = () => setInfo(null);
  const infoCopy = {
    contact: { title: 'Contact SUHAASA', body: 'For the approval version, the brand contact details are intentionally kept separate from the UI. The final business email, phone number and social handles can be connected here once supplied.' },
    shipping: { title: 'Shipping', body: 'Complimentary shipping is currently shown for orders above ₹1,499. Standard and express delivery options are represented in checkout. Final delivery timelines and serviceable locations will be connected to the confirmed store policy.' },
    returns: { title: 'Returns & exchanges', body: 'The product experience includes a dedicated returns area so the final policy can be connected without changing the design. Return window, eligibility, exchange rules and exclusions will be added from the brand-approved policy.' },
    faqs: { title: 'Frequently asked questions', body: 'The final FAQ content will cover sizing, fabric care, shipping, returns, order changes and payment. The interaction is ready; the answers can be supplied during the backend/content phase.' },
  };
  return (
    <>
      <footer className="footer" id="footer">
        <div className="footer-main">
          <div className="footer-brand"><img src="/suhaasa-logo.jpg" alt="SUHAASA" /><p>Timeless textiles for<br />homes and wardrobes.</p></div>
          <div className="footer-links">
            <div><span>Shop</span><a href="#collections">Kurtas</a><a href="#collections">Bedsheets</a><a href="#collections">Towels</a><a href="#featured">New arrivals</a></div>
            <div><span>Help</span><button onClick={() => setInfo('contact')}>Contact</button><button onClick={() => setInfo('shipping')}>Shipping</button><button onClick={() => setInfo('returns')}>Returns</button><button onClick={() => setInfo('faqs')}>FAQs</button></div>
            <div><span>Stay connected</span><a href="#newsletter">Join the mailing list</a><a href="#story">Our story</a></div>
          </div>
        </div>
        <div className="footer-bottom"><span>© 2026 SUHAASA. All rights reserved.</span><span>Made with intention.</span></div>
      </footer>
      <AnimatePresence>
        {info && <motion.div className="footer-info-backdrop" role="presentation" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(event) => { if (event.target === event.currentTarget) close(); }}>
          <motion.div className="footer-info-modal" role="dialog" aria-modal="true" aria-labelledby="footer-info-title" initial={{ opacity: 0, y: 18, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 10 }} onClick={(event) => event.stopPropagation()}>
            <button className="icon-btn footer-info-close" onClick={close} aria-label="Close information"><X /></button>
            <span className="kicker">SUHAASA information</span>
            <h2 id="footer-info-title">{infoCopy[info].title}</h2>
            <p>{infoCopy[info].body}</p>
            <button className="primary-btn" onClick={close}>Close <X size={15} /></button>
          </motion.div>
        </motion.div>}
      </AnimatePresence>
    </>
  );
}

function SearchOverlay({ products, query, setQuery, onClose, onCategory, onProduct }) {
  const normalized = query.trim().toLowerCase();
  const results = normalized
    ? products.filter((product) => `${product.name} ${product.category} ${product.tag}`.toLowerCase().includes(normalized)).slice(0, 5)
    : [];
  const chooseCategory = (category) => onCategory(category);
  return <motion.div className="overlay search-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <button className="overlay-close" onClick={onClose} aria-label="Close search"><X size={22} /></button>
    <div className="search-content">
      <span className="kicker">Search SUHAASA</span>
      <h2>What are you looking for?</h2>
      <div className="big-search"><Search size={22} /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Try “kurta”, “bedsheet”..." /><kbd>Esc</kbd></div>
      {normalized ? (
        <div className="search-results">
          {results.length ? results.map((product) => <button className="search-result" key={product.id} onClick={() => onProduct(product)}><img src={product.image} alt="" /><span><small>{product.category}</small><strong>{product.name}</strong></span><b>{product.price}</b></button>) : <p className="search-empty">No pieces found. Try another search.</p>}
        </div>
      ) : (
        <div className="search-suggestions"><span>Popular:</span><button onClick={() => chooseCategory('Kurtas')}>Kurtas</button><button onClick={() => chooseCategory('Bedsheets')}>Bedsheets</button><button onClick={() => chooseCategory('Towels')}>Towels</button><button onClick={() => chooseCategory('All')}>New arrivals</button></div>
      )}
    </div>
  </motion.div>;
}

function MobileMenu({ onClose, onShop, onKurtas, onHomeTextiles, onWishlist, onStory, onHome }) {
  return <motion.div className="mobile-menu" initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }} transition={{ duration: .45, ease }}><div className="mobile-menu-top"><img src="/suhaasa-logo.jpg" alt="SUHAASA" /><button className="icon-btn" onClick={onClose} aria-label="Close menu"><X /></button></div><nav><button onClick={onHome}>Home <ArrowRight /></button><button onClick={onShop}>Shop <ArrowRight /></button><button onClick={onKurtas}>Kurtas <ArrowRight /></button><button onClick={onHomeTextiles}>Home textiles <ArrowRight /></button><button onClick={onWishlist}>Wishlist <ArrowRight /></button><button onClick={onStory}>Our story <ArrowRight /></button></nav><div className="mobile-menu-note">Made for everyday living.<br /><em>SUHAASA</em></div></motion.div>;
}

function CartDrawer({ items, onUpdateQuantity, onRemove, onClose, onShop, onCheckout }) {
  const subtotal = items.reduce((sum, item) => sum + Number(item.price.replace(/[^0-9]/g, '')) * item.quantity, 0);
  const updateQty = (item, delta) => onUpdateQuantity(item.cartItemId, Math.max(1, item.quantity + delta));
  const remove = (item) => onRemove(item.cartItemId);
  return <motion.div className="drawer-backdrop" role="presentation" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}><motion.aside role="dialog" aria-modal="true" aria-labelledby="cart-title" className="cart-drawer" initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} transition={{ duration: .45, ease }}><div className="drawer-head"><div><span className="kicker">Your bag</span><h2 id="cart-title">{items.reduce((sum, item) => sum + item.quantity, 0)} {items.reduce((sum, item) => sum + item.quantity, 0) === 1 ? 'item' : 'items'}</h2></div><button className="icon-btn" onClick={onClose}><X /></button></div>{items.length ? <><div className="cart-items">{items.map(item => <div className="cart-item" key={item.cartItemId}><img src={item.image} alt={item.name} /><div className="cart-item-info"><span>{item.category}</span><h3>{item.name}</h3><small>Size {item.size}</small><div className="cart-item-bottom"><div className="qty-control"><button type="button" aria-label={`Decrease ${item.name} quantity`} onClick={() => updateQty(item, -1)}>−</button><b aria-live="polite">{item.quantity}</b><button type="button" aria-label={`Increase ${item.name} quantity`} onClick={() => updateQty(item, 1)}>+</button></div><strong>₹{Number(item.price.replace(/[^0-9]/g, '')) * item.quantity}</strong></div><button className="remove-link" onClick={() => remove(item)}>Remove</button></div></div>)}</div><div className="cart-summary"><div className="shipping-progress"><div><span>{subtotal >= 1499 ? 'You unlocked free shipping.' : `Add ₹${(1499 - subtotal).toLocaleString('en-IN')} for free shipping.`}</span><span>{Math.min(100, Math.round(subtotal / 1499 * 100))}%</span></div><span className="progress-track"><i style={{width:`${Math.min(100, subtotal / 1499 * 100)}%`}} /></span></div><div><span>Subtotal</span><strong>₹{subtotal.toLocaleString('en-IN')}</strong></div><p>Shipping and taxes calculated at checkout.</p><button className="primary-btn full" onClick={onCheckout}>Proceed to checkout <ArrowRight size={17} /></button></div></> : <div className="cart-empty"><ShoppingBag size={28} /><h3>Your bag is waiting.</h3><p>Beautiful things are better when they're chosen slowly.</p><button className="primary-btn" onClick={onShop}>Explore collection</button></div>}</motion.aside></motion.div>;
}

function CheckoutPage({ items, setItems, user, onBack }) {
  const [placedOrder, setPlacedOrder] = useState(null);
  const [shipping, setShipping] = useState('standard');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    name: user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() : '',
    email: user?.email || '',
    phone: '', address: '', address_line2: '', city: '', state: '', pincode: '',
  });

  useEffect(() => {
    if (!user) return;
    setForm(current => ({ ...current, name: current.name || `${user.first_name || ''} ${user.last_name || ''}`.trim(), email: current.email || user.email || '' }));
    commerceRequest('/auth/addresses/').then(addresses => {
      const address = addresses.find(item => item.is_default) || addresses[0];
      if (!address) return;
      setForm(current => ({ ...current, name: current.name || address.full_name, phone: current.phone || address.phone, address: current.address || address.address_line1, address_line2: current.address_line2 || address.address_line2 || '', city: current.city || address.city, state: current.state || address.state, pincode: current.pincode || address.pincode }));
    }).catch(() => {});
  }, [user]);

  const subtotal = items.reduce((sum, item) => sum + Number(item.price.replace(/[^0-9]/g, '')) * item.quantity, 0);
  const shippingCost = subtotal >= 1499 && shipping === 'standard' ? 0 : shipping === 'express' ? 149 : 99;
  const total = subtotal + shippingCost;
  const update = (key, value) => setForm(current => ({ ...current, [key]: value }));
  const canPlace = form.name && form.email && form.phone && form.address && form.city && form.state && form.pincode && !busy;

  const placeOrder = async () => {
    if (!canPlace) return;
    setBusy(true); setError('');
    try {
      const order = await commerceRequest('/orders/create/', {
        method: 'POST',
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          phone: form.phone,
          address: form.address,
          city: form.city,
          state: form.state,
          pincode: form.pincode,
          shipping_method: shipping,
        }),
      });

      const payment = await commerceRequest('/payments/create/', {
        method: 'POST',
        body: JSON.stringify({ order_number: order.order_number }),
      });

      await loadRazorpayScript();
      const razorpay = new window.Razorpay({
        key: payment.key_id,
        amount: payment.amount,
        currency: payment.currency,
        name: 'SUHAASA',
        description: `SUHAASA order ${payment.order_number}`,
        order_id: payment.gateway_order_id,
        prefill: {
          name: payment.name,
          email: payment.email,
          contact: payment.phone,
        },
        theme: { color: '#6a493b' },
        handler: async (response) => {
          try {
            const verified = await commerceRequest('/payments/verify/', {
              method: 'POST',
              body: JSON.stringify({
                order_number: order.order_number,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              }),
            });
            setPlacedOrder(verified);
            setItems([]);
          } catch (verifyError) {
            setError(verifyError.message || 'Payment was received but could not be verified. Please contact SUHAASA support.');
          } finally {
            setBusy(false);
          }
        },
        modal: {
          ondismiss: () => {
            setError('Payment was cancelled. Your order is saved and you can retry payment.');
            setBusy(false);
          },
        },
      });
      razorpay.on('payment.failed', (response) => {
        setError(response?.error?.description || 'Payment failed. Your order is saved and you can retry payment.');
        setBusy(false);
      });
      razorpay.open();
    } catch (err) {
      setError(err.message || 'We could not place your order. Please try again.');
    } finally {
      setBusy(false);
    }
  };

  if (placedOrder) {
    return <section className="checkout-page section"><div className="checkout-success"><div className="success-mark"><Check size={25}/></div><span className="kicker">Order confirmed</span><h1>Thank you for choosing <em>SUHAASA.</em></h1><p>Your order <strong>{placedOrder.order_number}</strong> has been created successfully. Payment has been securely received and your order is now confirmed.</p><div className="success-order-total"><span>Order {placedOrder.order_number}</span><strong>₹{Number(placedOrder.total).toLocaleString('en-IN')}</strong></div><div className="success-confirmation-meta"><span>{placedOrder.items?.length || 0} line item(s)</span><span>{placedOrder.shipping_method === 'express' ? 'Express delivery' : 'Standard delivery'}</span><span>Payment received</span></div><div className="success-actions"><button className="primary-btn" onClick={onBack}>Continue shopping <ArrowRight size={16}/></button></div></div></section>;
  }

  if (!items.length) return <section className="checkout-page section"><button className="back-link" onClick={onBack}><ArrowRight size={15} style={{ transform:'rotate(180deg)' }} /> Back to collection</button><div className="checkout-empty"><ShoppingBag size={28}/><h1>Your bag is empty.</h1><p>Add something you love before heading to checkout.</p><button className="primary-btn" onClick={onBack}>Explore collection <ArrowRight size={16}/></button></div></section>;

  if (!user) return <section className="checkout-page section"><div className="checkout-login-required"><div className="success-mark"><User size={23}/></div><span className="kicker">Account required</span><h1>Sign in to <em>continue.</em></h1><p>SUHAASA orders are available to signed-in customers so your purchases, payments and order history stay connected to your account.</p><button className="primary-btn" onClick={onBack}>Return to bag <ArrowRight size={16}/></button></div></section>;

  return <section className="checkout-page section">
    <div className="checkout-top"><button className="back-link" onClick={onBack}><ArrowRight size={15} style={{ transform:'rotate(180deg)' }} /> Back to collection</button><div className="checkout-steps"><span className="active">01 Details</span><span className="active">02 Delivery</span><span>03 Confirmation</span></div></div>
    <div className="checkout-layout">
      <div className="checkout-form">
        <span className="kicker">Secure checkout</span><h1>Make it <em>yours.</em></h1><p className="checkout-intro">Your order total, shipping charge and stock are confirmed by the SUHAASA backend when you place the order.</p>
        <div className="form-section"><div className="form-heading"><span>01</span><h2>Contact</h2></div><div className="form-grid"><label>Full name<input value={form.name} onChange={e=>update('name',e.target.value)} placeholder="Your name" autoComplete="name" /></label><label>Email<input type="email" value={form.email} onChange={e=>update('email',e.target.value)} placeholder="you@example.com" autoComplete="email" /></label><label>Phone<input value={form.phone} onChange={e=>update('phone',e.target.value)} placeholder="+91 98765 43210" autoComplete="tel" /></label></div></div>
        <div className="form-section"><div className="form-heading"><span>02</span><h2>Delivery address</h2></div><div className="form-grid"><label className="full-field">Address<input value={form.address} onChange={e=>update('address',e.target.value)} placeholder="House / flat, street, locality" autoComplete="street-address" /></label><label className="full-field">Apartment / locality<input value={form.address_line2} onChange={e=>update('address_line2',e.target.value)} placeholder="Apartment, landmark (optional)" /></label><label>City<input value={form.city} onChange={e=>update('city',e.target.value)} placeholder="City" autoComplete="address-level2" /></label><label>State<input value={form.state} onChange={e=>update('state',e.target.value)} placeholder="State" autoComplete="address-level1" /></label><label>PIN code<input value={form.pincode} onChange={e=>update('pincode',e.target.value)} placeholder="000000" inputMode="numeric" autoComplete="postal-code" /></label></div></div>
        <div className="form-section"><div className="form-heading"><span>03</span><h2>Delivery</h2></div><div className="shipping-options"><button type="button" className={shipping==='standard'?'selected':''} onClick={()=>setShipping('standard')}><span><b>Standard delivery</b><small>3–6 business days</small></span><strong>{subtotal >= 1499 ? 'Free' : '₹99'}</strong></button><button type="button" className={shipping==='express'?'selected':''} onClick={()=>setShipping('express')}><span><b>Express delivery</b><small>1–3 business days</small></span><strong>₹149</strong></button></div></div>
        <div className="form-section"><div className="form-heading"><span>04</span><h2>Payment</h2></div><div className="payment-preview"><div><span className="payment-icon">◈</span><span><b>Secure online payment</b><small>Razorpay checkout supports UPI, cards and net banking in test/live mode.</small></span></div><span className="payment-status">Secure</span></div></div>
        {error && <div className="account-error checkout-error">{error}</div>}
        <button className="primary-btn checkout-submit" disabled={!canPlace} onClick={placeOrder}>{busy ? 'Opening secure payment…' : 'Pay securely'} <ArrowRight size={17}/></button>
        <small className="checkout-disclaimer">You will complete payment in Razorpay's secure checkout. Your SUHAASA order total is calculated by the backend.</small>
      </div>
      <aside className="checkout-summary"><div className="summary-head"><span className="kicker">Your order</span><strong>{items.reduce((sum,item)=>sum+item.quantity,0)} items</strong></div><div className="summary-items">{items.map(item=><div className="summary-item" key={`${item.cartItemId}-${item.variantId}`}><img src={item.image} alt=""/><div><span>{item.category}</span><h3>{item.name}</h3><small>{item.size} · Qty {item.quantity}</small></div><strong>₹{(Number(item.price.replace(/[^0-9]/g,''))*item.quantity).toLocaleString('en-IN')}</strong></div>)}</div><div className="summary-totals"><div><span>Subtotal</span><strong>₹{subtotal.toLocaleString('en-IN')}</strong></div><div><span>Shipping</span><strong>{shippingCost ? `₹${shippingCost}` : 'Free'}</strong></div><div className="grand-total"><span>Total</span><strong>₹{total.toLocaleString('en-IN')}</strong></div></div><div className="summary-note"><Sparkles size={15}/><span>Thoughtfully packed with the same care as the pieces inside.</span></div></aside>
    </div>
  </section>;
}

function ProductDetail({ product, liked, onToggleLike, onAdd, onBack, onQuickView }) {
  const [size, setSize] = useState(product.sizes?.[0] || (product.category === 'Kurtas' ? 'M' : 'Standard'));
  const [quantity, setQuantity] = useState(1);
  const [activeImage, setActiveImage] = useState(product.image);
  const [openInfo, setOpenInfo] = useState('details');
  const [sizeGuide, setSizeGuide] = useState(false);
  const sizes = product.sizes || (product.category === 'Kurtas' ? ['S','M','L','XL'] : ['Standard']);
  const price = Number(product.price.replace(/[^0-9]/g, ''));

  return (
    <section className="product-detail section">
      <button className="back-link detail-back" onClick={onBack}><ArrowRight size={15} style={{ transform:'rotate(180deg)' }} /> Back to collection</button>
      <div className="detail-grid">
        <div className="detail-gallery">
          <motion.div className="detail-main-image" layoutId={`product-${product.id}`}>
            <img src={activeImage} onError={(e) => imageFallback(e, '/demo/sandalwood-kurta.svg')} alt={product.name} />
            <span className="detail-tag">{product.tag}</span>
          </motion.div>
          <div className="detail-thumbs">
            {[product.image, product.image2].filter(Boolean).map((img, i) => (
              <button key={img} className={activeImage === img ? 'active' : ''} onClick={() => setActiveImage(img)}>
                <img src={img} onError={(e) => imageFallback(e, '/demo/sandalwood-kurta.svg')} alt={`${product.name} view ${i + 1}`} />
              </button>
            ))}
          </div>
        </div>
        <div className="detail-copy">
          <div className="detail-eyebrow"><span className="product-category">{product.category}</span><span>•</span><span>{product.tag}</span></div>
          <h1>{product.name}</h1>
          <div className="detail-price"><strong>{product.price}</strong>{product.oldPrice && <del>{product.oldPrice}</del>}</div><div className="detail-meta-row"><span>★ {product.rating}</span><span>{product.reviews} reviews</span><span>SKU {product.sku}</span></div>
          <p className="detail-description">{product.description}</p>
          <div className="detail-rule" /><div className="detail-highlights">{(product.highlights || []).map((item) => <span key={item}>{item}</span>)}</div>
          <div className="selector-block">
            <div className="selector-label"><span>{product.category === 'Kurtas' ? 'Select size' : 'Format'}</span>{product.category === 'Kurtas' && <button onClick={() => setSizeGuide(true)}>Size guide</button>}</div>
            <div className="size-selector">{sizes.map(s => <button key={s} className={size === s ? 'selected' : ''} onClick={() => setSize(s)}>{s}</button>)}</div>
          </div>
          <div className="selector-block">
            <div className="selector-label"><span>Quantity</span><span className="stock-note">In stock · ready to ship</span></div>
            <div className="detail-quantity"><button type="button" aria-label="Decrease quantity" onClick={() => setQuantity(q => Math.max(1, q - 1))}>−</button><b aria-live="polite">{quantity}</b><button type="button" aria-label="Increase quantity" onClick={() => setQuantity(q => q + 1)}>+</button></div>
          </div>
          <div className="detail-actions">
            <button className="primary-btn detail-add" onClick={() => onAdd(product, { size, quantity })}>Add to bag <ShoppingBag size={17} /></button>
            <button className={`detail-wishlist ${liked ? 'liked' : ''}`} onClick={onToggleLike}><Heart size={18} fill={liked ? 'currentColor' : 'none'} /> {liked ? 'Saved' : 'Save to wishlist'}</button>
          </div>
          <div className="detail-accordions">
            {[
              ['details', 'Details', `${product.description} Crafted as part of the SUHAASA everyday collection.`],
              ['fabric', 'Fabric & care', `${product.fabric || 'Thoughtfully selected textile'}. ${product.care || 'Machine wash gently with similar colours. Dry in shade where possible.'}${product.dimensions ? ` Size: ${product.dimensions}.` : ''}`],
              ['shipping', 'Shipping & returns', 'Complimentary shipping on orders above ₹1,499. Returns and exchange details will be connected to the final store policy.'],
            ].map(([key, title, text]) => <div className={`detail-accordion ${openInfo === key ? 'open' : ''}`} key={key}><button onClick={() => setOpenInfo(openInfo === key ? '' : key)}><span>{title}</span><ChevronDown size={16} /></button><AnimatePresence initial={false}>{openInfo === key && <motion.p initial={{ height:0, opacity:0 }} animate={{ height:'auto', opacity:1 }} exit={{ height:0, opacity:0 }}>{text}</motion.p>}</AnimatePresence></div>)}
          </div>
          <div className="detail-note"><Sparkles size={15} /><span>Thoughtfully chosen. Designed to stay with you.</span></div>
        </div>
      </div>
      <div className="detail-bottom">
        <div><span className="kicker">The finer details</span><h2>Made to become part of <em>your everyday.</em></h2></div>
        <p>Every SUHAASA piece is selected for the feeling it brings into a room, a wardrobe, or a familiar daily ritual. We keep the palette calm, the details considered and the experience unhurried.</p>
      </div>
      <AnimatePresence>{sizeGuide && <motion.div className="size-guide-backdrop" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} onClick={() => setSizeGuide(false)}><motion.div className="size-guide-modal" initial={{y:18, opacity:0}} animate={{y:0, opacity:1}} exit={{y:12, opacity:0}} onClick={e => e.stopPropagation()}><div className="size-guide-head"><div><span className="kicker">SUHAASA fit guide</span><h2>Find your <em>easy fit.</em></h2></div><button className="icon-btn" onClick={() => setSizeGuide(false)}><X /></button></div><p>Use this as a starting point for our relaxed everyday silhouettes. If you prefer a looser fit, consider sizing up.</p><div className="size-table"><div><b>Size</b><b>Bust</b><b>Length</b></div><div><span>S</span><span>34–36 in</span><span>44 in</span></div><div><span>M</span><span>36–38 in</span><span>45 in</span></div><div><span>L</span><span>38–40 in</span><span>46 in</span></div><div><span>XL</span><span>40–42 in</span><span>47 in</span></div></div><small>Measurements are approximate and may vary slightly by style.</small></motion.div></motion.div>}</AnimatePresence>
    </section>
  );
}

function ProductModal({ product, onClose, onAdd }) {
  const [size, setSize] = useState(product.sizes?.[0] || 'M');
  const [quantity, setQuantity] = useState(1);
  return <motion.div className="modal-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}><motion.div className="product-modal" role="dialog" aria-modal="true" aria-labelledby="quick-view-title" initial={{ opacity: 0, y: 20, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 10 }} transition={{ duration: .35, ease }} onClick={(e) => e.stopPropagation()}><button className="modal-close icon-btn" onClick={onClose}><X /></button><div className="modal-image"><img src={product.image} onError={(e) => imageFallback(e, '/demo/sandalwood-kurta.svg')} alt={product.name} /></div><div className="modal-copy"><span className="product-category">{product.category}</span><h2 id="quick-view-title">{product.name}</h2><div className="modal-price">{product.price} {product.oldPrice && <del>{product.oldPrice}</del>}</div><p>{product.description}</p><div className="modal-meta"><span>★ {product.rating} · {product.reviews} reviews</span><span>{product.color} · {product.fabric}</span><span>{product.stock < 10 ? `Only ${product.stock} left` : 'In stock · ready to ship'}</span></div><div className="size-row"><span>{product.category === 'Kurtas' ? 'Size' : 'Format'}</span>{(product.sizes || ['Standard']).map(s => <button key={s} className={size === s ? 'selected' : ''} onClick={() => setSize(s)}>{s}</button>)}</div><div className="quantity-row"><span>Quantity</span><div className="qty-control"><button type="button" aria-label="Decrease quantity" onClick={() => setQuantity(q => Math.max(1, q - 1))}>−</button><b aria-live="polite">{quantity}</b><button type="button" aria-label="Increase quantity" onClick={() => setQuantity(q => q + 1)}>+</button></div></div><button className="primary-btn full" onClick={() => onAdd(product, { size, quantity })}>Add to bag <ShoppingBag size={17} /></button></div></motion.div></motion.div>;
}

function ShopPage({ products, category, setCategory, catalogFilter, setCatalogFilter, sortBy, setSortBy, liked, toggleLike, onQuickView, onProductDetail, onBack }) {
  const [mobileFilters, setMobileFilters] = useState(false);
  const categoriesForFilter = ['All', 'Kurtas', 'Bedsheets', 'Towels'];
  const filtered = products.filter(p => {
    const categoryMatch = category === 'All' || p.category === category;
    const wishlistMatch = catalogFilter !== 'Wishlist' || liked.includes(p.id);
    return categoryMatch && wishlistMatch;
  });
  const sorted = [...filtered].sort((a,b) => {
    if (sortBy === 'price-low') return Number(a.price.replace(/[^0-9]/g,'')) - Number(b.price.replace(/[^0-9]/g,''));
    if (sortBy === 'price-high') return Number(b.price.replace(/[^0-9]/g,'')) - Number(a.price.replace(/[^0-9]/g,''));
    if (sortBy === 'rating') return b.rating - a.rating || b.reviews - a.reviews;
    return a.id - b.id;
  });
  const activeLabel = catalogFilter === 'Wishlist' ? 'Wishlist' : category;
  return <section className="shop-page section">
    <div className="shop-hero">
      <button className="back-link" onClick={onBack}><ArrowRight size={15} style={{ transform:'rotate(180deg)' }} /> Back to home</button>
      <span className="kicker">The SUHAASA shop</span>
      <h1>Pieces for <em>living beautifully.</em></h1>
      <p>Explore clothing and home textiles selected for comfort, character and everyday rituals.</p>
    </div>
    <div className="catalog-summary">
      <div><strong>{products.length}</strong><span>pieces in the collection</span></div>
      <div><strong>3</strong><span>everyday categories</span></div>
      <div><strong>100%</strong><span>cotton-led edit</span></div>
    </div>
    <div className="shop-toolbar">
      <div className="filter-tabs">
        {categoriesForFilter.map(name => <button key={name} className={catalogFilter !== 'Wishlist' && category === name ? 'active' : ''} onClick={() => { setCategory(name); setCatalogFilter('All'); }}>{name}</button>)}
        <button className={catalogFilter === 'Wishlist' ? 'active' : ''} onClick={() => setCatalogFilter('Wishlist')}>Wishlist {liked.length ? `(${liked.length})` : ''}</button>
      </div>
      <div className="shop-sort"><button className="mobile-filter-btn" onClick={() => setMobileFilters(!mobileFilters)}>Filter <ChevronDown size={15} /></button><label>Sort by <select value={sortBy} onChange={e => setSortBy(e.target.value)}><option value="featured">Featured</option><option value="price-low">Price: low to high</option><option value="price-high">Price: high to low</option><option value="rating">Top rated</option></select></label></div>
    </div>
    {mobileFilters && <motion.div className="mobile-filter-panel" initial={{ height:0, opacity:0 }} animate={{ height:'auto', opacity:1 }}><span>Category</span>{categoriesForFilter.map(name => <button key={name} className={category === name && catalogFilter !== 'Wishlist' ? 'active' : ''} onClick={() => { setCategory(name); setCatalogFilter('All'); setMobileFilters(false); }}>{name}</button>)}<button className={catalogFilter === 'Wishlist' ? 'active' : ''} onClick={() => { setCatalogFilter('Wishlist'); setMobileFilters(false); }}>Wishlist</button></motion.div>}
    <div className="shop-count"><span>{sorted.length} {sorted.length === 1 ? 'piece' : 'pieces'} · {activeLabel}</span><span>{catalogFilter === 'Wishlist' ? 'Your saved pieces' : 'Curated for you'}</span></div>
    {sorted.length ? <div className="product-grid shop-grid">{sorted.map((product, index) => {
      const stockLabel = product.stock <= 10 ? `Only ${product.stock} left` : 'In stock';
      return <motion.article className="product-card" key={product.id} initial={{ opacity:0, y:24 }} animate={{ opacity:1, y:0 }} transition={{ duration:.5, delay:index*.06, ease }}>
        <div className="product-image-wrap" onClick={() => onProductDetail(product)}><img src={product.image} onError={(e) => imageFallback(e, '/demo/sandalwood-kurta.svg')} alt={product.name} /><span className="product-tag">{product.tag}</span><button className={`wishlist-btn ${liked.includes(product.id) ? 'liked' : ''}`} onClick={(e) => { e.stopPropagation(); toggleLike(product.id); }} aria-label={`${liked.includes(product.id) ? 'Remove' : 'Add'} ${product.name} ${liked.includes(product.id) ? 'from' : 'to'} wishlist`}><Heart size={18} fill={liked.includes(product.id) ? 'currentColor' : 'none'} /></button><button className="quick-view" aria-label={`Quick view ${product.name}`} onClick={(e) => { e.stopPropagation(); onQuickView(product); }}>Quick view <ArrowUpRight size={14} /></button></div>
        <div className="product-info"><div><span className="product-category">{product.category} · {product.color}</span><h3>{product.name}</h3><small className="product-rating">★ {product.rating} <span>({product.reviews})</span></small><div className="product-specs"><span>{product.fabric}</span><span>{product.sizes?.join(' · ')}</span></div><div className={`stock-note ${product.stock <= 10 ? 'low-stock' : ''}`}><span className="stock-dot" />{stockLabel}</div></div><div className="price"><strong>{product.price}</strong>{product.oldPrice && <del>{product.oldPrice}</del>}</div></div>
      </motion.article>;
    })}</div> : <div className="empty-catalog"><Heart size={25} /><h3>No saved pieces yet.</h3><p>Tap the heart on any product to build your SUHAASA wishlist.</p><button className="primary-btn" onClick={() => { setCatalogFilter('All'); setCategory('All'); }}>Explore collection <ArrowRight size={16}/></button></div>}
  </section>;
}


createRoot(document.getElementById('root')).render(<App />);
