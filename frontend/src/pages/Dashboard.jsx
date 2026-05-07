import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import api from '../services/api';
import { Activity, Heart, Bell } from 'lucide-react';

const Dashboard = () => {
  const { user, loading } = useContext(AuthContext);
  const [wishlist, setWishlist] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    if (user) {
      api.get('products/wishlist/')
        .then(res => setWishlist(res.data.results || res.data))
        .catch(err => console.error(err));
        
      api.get('products/alerts/')
        .then(res => setAlerts(res.data.results || res.data))
        .catch(err => console.error(err));
    }
  }, [user]);

  if (loading) return <div className="text-center py-20">Loading...</div>;
  if (!user) return <Navigate to="/login" />;

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-dark">Welcome, {user.username}!</h1>
        <p className="text-gray-500">Here's your shopping activity.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-10">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
          <div className="bg-red-100 p-4 rounded-full text-red-500 mr-4">
            <Heart size={24} />
          </div>
          <div>
            <p className="text-gray-500 text-sm">Wishlist Items</p>
            <h3 className="text-2xl font-bold">{wishlist.length}</h3>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
          <div className="bg-blue-100 p-4 rounded-full text-blue-500 mr-4">
            <Bell size={24} />
          </div>
          <div>
            <p className="text-gray-500 text-sm">Active Alerts</p>
            <h3 className="text-2xl font-bold">{alerts.length}</h3>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
          <div className="bg-green-100 p-4 rounded-full text-green-500 mr-4">
            <Activity size={24} />
          </div>
          <div>
            <p className="text-gray-500 text-sm">Affiliate Clicks</p>
            <h3 className="text-2xl font-bold">0</h3>
          </div>
        </div>
      </div>

      {/* Lists */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-bold mb-4 flex items-center"><Heart className="mr-2 text-red-500" size={20}/> Your Wishlist</h2>
          {wishlist.length === 0 ? (
            <p className="text-gray-500 italic">No items in your wishlist.</p>
          ) : (
            <ul className="divide-y">
              {wishlist.map(item => (
                <li key={item.id} className="py-3 flex justify-between items-center">
                  <span>{item.product_name || `Product #${item.product}`}</span>
                  <span className="font-semibold text-primary">₹{item.target_price || 'Any'}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-bold mb-4 flex items-center"><Bell className="mr-2 text-blue-500" size={20}/> Price Alerts</h2>
          {alerts.length === 0 ? (
            <p className="text-gray-500 italic">No active price alerts.</p>
          ) : (
            <ul className="divide-y">
              {alerts.map(item => (
                <li key={item.id} className="py-3 flex justify-between items-center">
                  <span>{item.product_name || `Product #${item.product}`}</span>
                  <div>
                    <span className="font-semibold text-gray-700 block text-right">Target: ₹{item.target_price}</span>
                    <span className={`text-sm ${item.is_triggered ? 'text-green-500' : 'text-orange-500'}`}>
                      {item.is_triggered ? 'Triggered!' : 'Pending'}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
