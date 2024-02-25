import logo from './logo.svg';
import './App.css';
import { BarChart } from '@mui/x-charts/BarChart'

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
  return (
    <div className="App min-h-screen bg-gradient-to-b from-sky-200 to-sky-600 text-zinc-300 opacity-95 overflow-x-hidden text-slate-800 px-5">
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
