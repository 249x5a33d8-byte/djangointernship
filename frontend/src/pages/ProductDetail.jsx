import React, { useEffect, useState, useContext } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { ExternalLink, Heart, Bell, AlertTriangle, TrendingDown } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const ProductDetail = () => {
  const { id } = useParams();
  const { user } = useContext(AuthContext);
  const [product, setProduct] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const prodRes = await api.get(`products/${id}/`);
        setProduct(prodRes.data);
        
        try {
          const predRes = await api.get(`predictions/${id}/`);
          setPrediction(predRes.data);
        } catch (e) {
          console.error("No prediction available", e);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [id]);

  const handleWishlist = async () => {
    if (!user) return alert("Please login first");
    try {
      await api.post('products/wishlist/', { product_id: id });
      alert("Added to wishlist!");
    } catch (e) {
      alert("Already in wishlist or error occurred.");
    }
  };

  const handleAffiliateClick = () => {
    window.open(`http://localhost:8000/api/affiliate/redirect/${id}/`, '_blank');
  };

  if (loading) return <div className="text-center py-20">Loading...</div>;
  if (!product) return <div className="text-center py-20">Product not found.</div>;

  const chartData = prediction ? {
    labels: prediction.predictions.map(p => p.date),
    datasets: [
      {
        label: 'Predicted Price (₹)',
        data: prediction.predictions.map(p => p.predicted_price),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.3,
      }
    ],
  } : null;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-8">
        <div className="grid md:grid-cols-2 gap-8 p-8">
          <div className="flex justify-center items-center bg-gray-50 rounded-xl p-8">
            <img src={product.image_url} alt={product.name} className="max-h-96 object-contain" />
          </div>
          
          <div className="flex flex-col justify-center">
            <div className="mb-2">
              <span className={`text-sm px-3 py-1 rounded-full font-medium ${product.vendor === 'Amazon' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'}`}>
                {product.vendor}
              </span>
            </div>
            <h1 className="text-3xl font-bold text-dark mb-4">{product.name}</h1>
            <p className="text-gray-600 mb-6">{product.description}</p>
            
            <div className="flex items-baseline mb-6">
              <span className="text-4xl font-extrabold text-dark">₹{product.price}</span>
              {product.original_price && product.original_price > product.price && (
                <>
                  <span className="text-lg text-gray-400 line-through ml-3">₹{product.original_price}</span>
                  <span className="text-green-500 font-semibold ml-3">{product.discount_percentage}% OFF</span>
                </>
              )}
            </div>

            <div className="flex gap-4 mb-8">
              <button onClick={handleAffiliateClick} className="flex-1 bg-primary text-white py-3 rounded-xl font-bold flex items-center justify-center hover:bg-blue-700 transition shadow-md hover:shadow-lg">
                View on {product.vendor} <ExternalLink size={18} className="ml-2" />
              </button>
              <button onClick={handleWishlist} className="px-6 py-3 border-2 border-gray-200 text-gray-600 rounded-xl font-bold flex items-center justify-center hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition">
                <Heart size={20} />
              </button>
            </div>
            
            {prediction && prediction.recommendation && (
              <div className="flex flex-col gap-4">
                <div className={`p-4 rounded-xl border-l-4 flex items-start ${prediction.recommendation.action === 'wait' ? 'bg-orange-50 border-orange-500 text-orange-800' : 'bg-green-50 border-green-500 text-green-800'}`}>
                  <div className="mr-3 mt-1">
                    {prediction.recommendation.action === 'wait' ? <AlertTriangle size={24} /> : <TrendingDown size={24} />}
                  </div>
                  <div>
                    <h4 className="font-bold text-lg mb-1">Our ML Recommendation</h4>
                    <p>{prediction.recommendation.message}</p>
                  </div>
                </div>
                
                {prediction.recommendation.best_month && (
                  <div className="bg-blue-50 border-l-4 border-blue-500 text-blue-800 p-4 rounded-xl flex items-start">
                    <div className="mr-3 mt-1">
                      <TrendingDown size={24} />
                    </div>
                    <div>
                      <h4 className="font-bold text-lg mb-1">Historically Best Time to Buy</h4>
                      <p>Based on our historical data, <strong>{prediction.recommendation.best_month}</strong> is usually the best month to purchase this item to get the lowest price.</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {prediction && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
          <h2 className="text-2xl font-bold text-dark mb-6">Price Prediction (Next 30 Days)</h2>
          <div className="h-80 w-full">
            <Line 
              data={chartData} 
              options={{ 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'top' },
                },
                scales: {
                  y: { min: Math.min(...prediction.predictions.map(p => p.predicted_price)) * 0.95 }
                }
              }} 
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;
