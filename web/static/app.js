import { createDashboard } from './components/Dashboard.js';
import { WalletManager } from './services/WalletManager.js';
import { AnalyticsService } from './services/AnalyticsService.js';

class FinancialDashboard {
    constructor() {
        this.walletManager = new WalletManager();
        this.analyticsService = new AnalyticsService();
        this.state = {
            walletConnected: false,
            loading: false,
            error: null,
            data: null
        };
    }

    async init() {
        try {
            await this.checkWalletConnection();
            this.render();
            this.setupEventListeners();
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.setState({ error: error.message });
        }
    }

    async checkWalletConnection() {
        try {
            const status = await this.walletManager.checkConnection();
            this.setState({ walletConnected: status.connected });
            if (status.connected) {
                await this.fetchDashboardData();
            }
        } catch (error) {
            console.error('Wallet connection check failed:', error);
        }
    }

    async fetchDashboardData() {
        this.setState({ loading: true });
        try {
            const walletData = await this.walletManager.getWalletInfo();
            const analytics = await this.analyticsService.analyzeTransactions(
                walletData.transactions
            );
            
            this.setState({
                data: {
                    wallet: walletData,
                    analytics: analytics
                },
                loading: false
            });
        } catch (error) {
            this.setState({
                error: 'Failed to fetch dashboard data',
                loading: false
            });
        }
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.render();
    }

    setupEventListeners() {
        document.addEventListener('wallet-connected', async () => {
            await this.fetchDashboardData();
        });

        document.addEventListener('refresh-data', async () => {
            await this.fetchDashboardData();
        });
    }

    render() {
        const rootElement = document.getElementById('root');
        createDashboard(rootElement, {
            ...this.state,
            onConnect: () => this.walletManager.connect(),
            onRefresh: () => this.fetchDashboardData()
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new FinancialDashboard();
    dashboard.init();
}); 