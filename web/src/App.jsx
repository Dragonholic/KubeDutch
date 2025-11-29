import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';

// IMPORTANT: Replace with your deployed contract address!
const CONTRACT_ADDRESS = "0x9b30FA9E01cF86AE9C39d22aD46819Af782bcdc7"; 

// Minimum ABI to read events
const CONTRACT_ABI = [
  "event UsageLogged(string indexed username, uint256 duration, uint256 cost, uint256 timestamp)"
];

function App() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [totalCost, setTotalCost] = useState("0");

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      let provider;
      
      // Use Metamask if available, otherwise fallback to public RPC
      if (window.ethereum) {
        provider = new ethers.BrowserProvider(window.ethereum);
      } else {
        // Sepolia Public RPC
        provider = new ethers.JsonRpcProvider("https://rpc.sepolia.org");
      }

      // If address is not set, don't crash
      if (CONTRACT_ADDRESS === "0x0000000000000000000000000000000000000000") {
        console.warn("Contract address not set.");
        setLoading(false);
        return;
      }

      const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
      
      const currentBlock = await provider.getBlockNumber();
      // Query last 5000 blocks to avoid RPC limits
      const filter = contract.filters.UsageLogged();
      const events = await contract.queryFilter(filter, currentBlock - 5000, currentBlock);

      const parsedLogs = events.map(event => {
        // Handle potential object (Indexed event argument)
        let uName = event.args[0];
        if (typeof uName === 'object' && uName !== null) {
          uName = uName.hash || "Unknown";
        }

        return {
          username: uName,
          duration: Number(event.args[1]),
          cost: ethers.formatEther(event.args[2]),
          timestamp: new Date(Number(event.args[3]) * 1000).toLocaleString()
        };
      }).reverse();

      setLogs(parsedLogs);
      
      const total = events.reduce((acc, curr) => acc + curr.args[2], 0n);
      setTotalCost(ethers.formatEther(total));

    } catch (error) {
      console.error("Failed to fetch logs:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-10 font-sans">
      <div className="max-w-4xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-green-400 mb-2">KubeDutch Dashboard</h1>
          <p className="text-gray-400">Standard K8s Minecraft Usage Ledger on Sepolia</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700">
            <h2 className="text-xl font-semibold text-gray-300 mb-2">Total Usage Cost</h2>
            <p className="text-3xl font-mono text-yellow-400">{totalCost} ETH</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700">
            <h2 className="text-xl font-semibold text-gray-300 mb-2">Total Sessions</h2>
            <p className="text-3xl font-mono text-blue-400">{logs.length}</p>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 overflow-hidden">
          <div className="p-4 bg-gray-700 flex justify-between items-center">
            <h3 className="font-bold text-lg">Recent Usage Logs</h3>
            <button onClick={fetchLogs} className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm transition">
              Refresh
            </button>
          </div>
          
          {loading ? (
            <div className="p-10 text-center text-gray-400">Loading blockchain data...</div>
          ) : (
            <table className="w-full text-left">
              <thead className="bg-gray-900 text-gray-400">
                <tr>
                  <th className="p-4">Time</th>
                  <th className="p-4">User</th>
                  <th className="p-4">Duration</th>
                  <th className="p-4 text-right">Cost (ETH)</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, index) => (
                  <tr key={index} className="border-b border-gray-700 hover:bg-gray-750 transition">
                    <td className="p-4 text-gray-400 text-sm">{log.timestamp}</td>
                    <td className="p-4 font-medium text-white">{log.username}</td>
                    <td className="p-4 text-gray-300">{log.duration}s</td>
                    <td className="p-4 text-right font-mono text-yellow-500">{log.cost}</td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr>
                    <td colSpan="4" className="p-10 text-center text-gray-500">No logs found (or waiting for data).</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
        
        <footer className="mt-10 text-center text-gray-500 text-sm">
          <p className="break-all">Contract: {CONTRACT_ADDRESS}</p>
        </footer>
      </div>
    </div>
  );
}

export default App;

