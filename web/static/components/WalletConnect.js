import React, { useState } from 'react';
import {
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    CircularProgress,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Box
} from '@mui/material';

export default function WalletConnect({ onConnect, loading }) {
    const [open, setOpen] = useState(false);
    const [walletId, setWalletId] = useState('');
    const [walletType, setWalletType] = useState('bitcoin');

    const handleConnect = () => {
        onConnect({ wallet_id: walletId, wallet_type: walletType });
        setOpen(false);
    };

    return (
        <>
            <Button
                variant="contained"
                color="primary"
                onClick={() => setOpen(true)}
                disabled={loading}
                sx={{
                    minWidth: '150px',
                    height: '40px'
                }}
            >
                {loading ? <CircularProgress size={24} /> : 'Connect Wallet'}
            </Button>

            <Dialog open={open} onClose={() => setOpen(false)}>
                <DialogTitle>Connect Wallet</DialogTitle>
                <DialogContent>
                    <Box sx={{ mt: 2 }}>
                        <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel>Wallet Type</InputLabel>
                            <Select
                                value={walletType}
                                onChange={(e) => setWalletType(e.target.value)}
                                label="Wallet Type"
                            >
                                <MenuItem value="bitcoin">Bitcoin</MenuItem>
                                <MenuItem value="lightning">Lightning</MenuItem>
                                <MenuItem value="web5">Web5</MenuItem>
                            </Select>
                        </FormControl>
                        <TextField
                            autoFocus
                            margin="dense"
                            label="Wallet ID"
                            type="text"
                            fullWidth
                            value={walletId}
                            onChange={(e) => setWalletId(e.target.value)}
                        />
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)}>Cancel</Button>
                    <Button onClick={handleConnect} variant="contained">
                        Connect
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
} 