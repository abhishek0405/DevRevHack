/* eslint-disable eqeqeq */
import logo from './logo.svg';
import './App.css';
import { BarChart } from '@mui/x-charts/BarChart'
import { PieChart } from '@mui/x-charts/PieChart'
import React, { useState, useEffect } from 'react'

const uData = [4000, 3000, 2000, 2780, 1890, 2390, 3490];
const pData = [2400, 1398, 9800, 3908, 4800, 3800, 4300];
const xLabels = [
  'Page A',
  'Page B',
  'Page C',
  'Page D',
  'Page E',
  'Page F',
  'Page G',
];
function App() {


  const [reviewData, setReviewData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
        try {
            const response = await fetch('https://devrevhacklimbo.onrender.com/data');
            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }
            const data = await response.json();
            setReviewData(data);
        } catch (error) {
            console.error('Error fetching review data:', error);
        }
    };

    fetchData();
}, [])
  
  const countSentiments = (reviews) => {
    let counts = [
      { id: 0, value: 0, label: 'Positive' },
      { id: 1, value: 0, label: 'Negative' },
      { id: 2, value: 0, label: 'Neutral' },
  ];

  reviews.forEach(review => {
      switch (review.sentiment) {
          case 'Positive':
              counts[0].value++;
              break;
          case 'Negative':
              counts[1].value++;
              break;
          case 'Neutral':
              counts[2].value++;
              break;
          default:
              break;
      }
  });

  return counts;
  }






  return (
    <div className="App min-h-screen bg-gradient-to-b from-sky-200 to-sky-600 opacity-95 overflow-x-hidden text-zinc-800 px-5">
       <div class="container mx-auto px-5 py-3 flex justify-between items-center">
        <span class="text-xl font-semibold">DevRev Insights</span>
      </div>
      <div class="container m-2">
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-3 gap-4">
    <div class="bg-white bg-opacity-75 rounded-lg p-4 shadow-md"><h2 class="text-lg font-semibold mb-4">Positive Reviews</h2>
      <p class="text-3xl font-bold">150</p>

    
    </div>
    <div class="bg-white bg-opacity-75 rounded-lg p-4 shadow-md">
    <h2 class="text-lg font-semibold mb-4">Issues Reported</h2>
      <p class="text-3xl font-bold">20</p>
    </div>
    <div class="bg-white bg-opacity-75 rounded-lg p-4 shadow-md">
    <h2 class="text-lg font-semibold mb-4">Feature Requests</h2>
      <p class="text-3xl font-bold">10</p>
    </div>
    <div class="bg-white bg-opacity-75 rounded-lg p-4 shadow-md">
    <BarChart
        width={500}
        height={300}
        series={[
          { data: pData, label: 'pv', id: 'pvId' },
          { data: uData, label: 'uv', id: 'uvId' },
        ]}
        xAxis={[{ data: xLabels, scaleType: 'band' }]}
      />
    </div>
    <div class="bg-white bg-opacity-75 rounded-lg p-4 shadow-md">
    <PieChart
      series={[
        {
          data: countSentiments(reviewData),
        },
      ]}
      width={400}
      height={200}
    />
    </div>
    <div class="bg-white bg-opacity-75 rounded-lg p-4 shadow-md">
    <BarChart
        width={500}
        height={300}
        series={[
          { data: pData, label: 'pv', id: 'pvId' },
          { data: uData, label: 'uv', id: 'uvId' },
        ]}
        xAxis={[{ data: xLabels, scaleType: 'band' }]}
      />
    </div>
  </div>
</div>

     
    </div>
  );
}

export default App;
