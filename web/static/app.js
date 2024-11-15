function Dashboard() {
    const [walletId, setWalletId] = React.useState('');
    const [analysis, setAnalysis] = React.useState(null);
    const [error, setError] = React.useState(null);

    const connectWallet = async () => {
        try {
            const response = await fetch(`/api/wallet/connect/${walletId}`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Failed to connect wallet');
            getAnalysis();
        } catch (err) {
            setError(err.message);
        }
    };

    const getAnalysis = async () => {
        try {
            const response = await fetch(`/api/wallet/${walletId}/analysis`);
            if (!response.ok) throw new Error('Failed to get analysis');
            const data = await response.json();
            setAnalysis(data);
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="dashboard">
            <h1>33dash Bitcoin Dashboard</h1>
            
            <div className="wallet-form">
                <input 
                    type="text" 
                    value={walletId} 
                    onChange={(e) => setWalletId(e.target.value)}
                    placeholder="Enter wallet ID"
                />
                <button onClick={connectWallet}>Connect Wallet</button>
            </div>

            {error && <div className="error">{error}</div>}

            {analysis && (
                <div className="analysis">
                    <h2>Analysis Results</h2>
                    <p>Risk Score: {analysis.risk_score}</p>
                    <h3>Recommendations:</h3>
                    <ul>
                        {analysis.recommendations.map((rec, i) => (
                            <li key={i}>{rec}</li>
                        ))}
                    </ul>
                    <h3>Predicted Trends:</h3>
                    <ul>
                        {Object.entries(analysis.predicted_trends).map(([trend, value]) => (
                            <li key={trend}>{trend}: {value}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

ReactDOM.render(<Dashboard />, document.getElementById('root')); 