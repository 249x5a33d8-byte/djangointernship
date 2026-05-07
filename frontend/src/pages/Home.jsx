import React from 'react';
import { Link } from 'react-router-dom';
import { Search, TrendingDown, Bell, Star } from 'lucide-react';

const Home = () => {
  return (
    <div className="min-h-screen bg-light">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 to-indigo-800 text-white py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-6">
            Shop Smarter, Not Harder
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 mb-10 max-w-3xl mx-auto">
            Our Machine Learning engine predicts future prices so you know exactly when to buy and when to wait.
          </p>
          <div className="flex justify-center space-x-4">
            <Link to="/products" className="bg-white text-blue-600 px-8 py-3 rounded-full font-semibold text-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all">
              Start Browsing
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-16 text-dark">Why use IntelliShop?</h2>
        <div className="grid md:grid-cols-3 gap-12">
          
          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-shadow text-center">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-blue-600">
              <TrendingDown size={32} />
            </div>
            <h3 className="text-xl font-bold mb-4">Price Predictions</h3>
            <p className="text-gray-600">Our ML model analyzes historical data to tell you if the price will drop soon.</p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-shadow text-center">
            <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-purple-600">
              <Search size={32} />
            </div>
            <h3 className="text-xl font-bold mb-4">Smart Comparisons</h3>
            <p className="text-gray-600">Instantly compare prices between Amazon and Flipkart to find the best deal.</p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-shadow text-center">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-green-600">
              <Bell size={32} />
            </div>
            <h3 className="text-xl font-bold mb-4">Price Alerts</h3>
            <p className="text-gray-600">Set your target price and we'll alert you the moment it drops.</p>
          </div>

        </div>
      </section>
    </div>
  );
};

export default Home;
