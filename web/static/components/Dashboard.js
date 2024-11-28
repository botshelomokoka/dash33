import React, { useState, useEffect } from 'react';
import { 
    Box, 
    Container, 
    Typography, 
    Paper, 
    Grid,
    Button,
    Alert
} from '@mui/material';

import WalletConnect from './WalletConnect';
import TransactionList from './TransactionList';
import AnalysisPanel from './AnalysisPanel';
import LightningPanel from './LightningPanel';
import Web5Panel from './Web5Panel';

export default function Dashboard() {
    const [walletData, setWalletData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleWalletConnect = async (connectData) => {
        try {
            setLoading(true);
            const response = await fetch('/api/v1/wallet/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(connectData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to connect wallet');
            }
            
            await fetchDashboardData(connectData.wallet_id);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="lg">
            <Box sx={{ my: 4 }}>
                <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 3
                }}>
                    <Typography variant="h4" component="h1">
                        33dash Bitcoin Dashboard
                    </Typography>
                    <WalletConnect 
                        onConnect={handleWalletConnect}
                        loading={loading}
                    />
                </Box>
                
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}
                
                <Grid container spacing={3}>
                    <Grid item xs={12}>
                        <Paper sx={{ 
                            p: 3,
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center'
                        }}>
                            <Typography variant="h6" gutterBottom>
                                Total Balance
                            </Typography>
                            <Typography variant="h3">
                                {walletData ? 
                                    `₿ ${walletData.wallet_info.balance.toFixed(8)}` :
                                    '₿ 0.00000000'
                                }
                            </Typography>
                        </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={8}>
                        <Paper sx={{ p: 2 }}>
                            <TransactionList 
                                transactions={walletData?.wallet_info.transactions || []}
                            />
                        </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 2 }}>
                            <AnalysisPanel 
                                analysis={walletData?.analysis}
                            />
                        </Paper>
                    </Grid>
                    
                    {walletData?.lightning_status && (
                        <Grid item xs={12} md={6}>
                            <Paper sx={{ p: 2 }}>
                                <LightningPanel 
                                    status={walletData.lightning_status}
                                />
                            </Paper>
                        </Grid>
                    )}
                    
                    {walletData?.web5_status && (
                        <Grid item xs={12} md={6}>
                            <Paper sx={{ p: 2 }}>
                                <Web5Panel 
                                    status={walletData.web5_status}
                                />
                            </Paper>
                        </Grid>
                    )}
                </Grid>
            </Box>
        </Container>
    );
} 