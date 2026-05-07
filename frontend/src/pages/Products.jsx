import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Search, Filter, Star } from 'lucide-react';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  useEffect(() => {
    // Fetch categories
    api.get('products/categories/')
      .then(res => setCategories(res.data.results || res.data))
      .catch(console.error);
      
    fetchProducts();
  }, []);

  const fetchProducts = (q = '', cat = '') => {
    setLoading(true);
    let url = 'products/?';
    if (q) url += `search=${q}&`;
    if (cat) url += `category=${cat}`;
    
    api.get(url)
      .then(res => {
        setProducts(res.data.results || res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchProducts(search, selectedCategory);
  };

  const handleCategoryChange = (e) => {
    const cat = e.target.value;
    setSelectedCategory(cat);
    fetchProducts(search, cat);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
        <h1 className="text-3xl font-bold text-dark">Explore Products</h1>
        
        <form onSubmit={handleSearch} className="flex w-full md:w-auto gap-2">
          <div className="relative w-full md:w-64">
            <input 
              type="text" 
              placeholder="Search..." 
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          </div>
          <select 
            className="border border-gray-300 rounded-lg px-4 py-2 bg-white"
            value={selectedCategory}
            onChange={handleCategoryChange}
          >
            <option value="">All Categories</option>
            {categories.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <button type="submit" className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
            <Filter size={18} />
          </button>
        </form>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.length === 0 ? (
            <div className="col-span-full text-center text-gray-500 py-10">No products found.</div>
          ) : (
            products.map(p => (
              <Link to={`/products/${p.id}`} key={p.id} className="bg-white rounded-xl shadow-sm hover:shadow-lg transition overflow-hidden group">
                <div className="h-48 overflow-hidden bg-gray-100 flex items-center justify-center p-4">
                  <img src={p.image_url} alt={p.name} className="max-h-full max-w-full object-contain group-hover:scale-110 transition duration-300" />
                </div>
                <div className="p-4 border-t border-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-gray-800 line-clamp-2">{p.name}</h3>
                  </div>
                  <div className="flex items-center text-yellow-500 mb-2 text-sm">
                    <Star size={14} className="fill-current" />
                    <span className="ml-1 text-gray-600">{p.rating} ({p.review_count})</span>
                  </div>
                  <div className="flex justify-between items-end mt-4">
                    <div>
                      <span className="text-xl font-bold text-dark">₹{p.price}</span>
                      {p.original_price && p.original_price > p.price && (
                        <span className="text-xs text-gray-400 line-through ml-2">₹{p.original_price}</span>
                      )}
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${p.vendor === 'Amazon' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'}`}>
                      {p.vendor}
                    </span>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default Products;
