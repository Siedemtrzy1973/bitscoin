import React, { useState, useEffect, useCallback } from 'react';
import { 
  ThemeProvider, 
  createTheme, 
  CssBaseline,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  Box
} from '@mui/material';
import { 
  AccountBalanceWallet,
  Send,
  Layers,
  TrendingUp,
  Add
} from '@mui/icons-material';
import axios from 'axios';
import io from 'socket.io-client';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#ff6b35',
    },
    secondary: {
      main: '#f7931a',
    },
    background: {
      default: '#0d1117',
      paper: '#161b22',
    },
  },
});

const API_BASE = 'http://localhost:5000/api';

function App() {
  const [status, setStatus] = useState({});
  const [addresses, setAddresses] = useState([]);
  const [blockchain, setBlockchain] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState('');
  const [sendForm, setSendForm] = useState({ to: '', amount: '' });
  const [newAddressLabel, setNewAddressLabel] = useState('');
  const [mining, setMining] = useState(false);
  const [alerts, setAlerts] = useState([]);

  const addAlert = useCallback((message, severity) => {
    const alert = { id: Date.now(), message, severity };
    setAlerts(prev => [alert, ...prev.slice(0, 4)]);
    setTimeout(() => {
      setAlerts(prev => prev.filter(a => a.id !== alert.id));
    }, 5000);
  }, []);

  const loadData = useCallback(async () => {
    try {
      const [statusRes, addressesRes, blockchainRes] = await Promise.all([
        axios.get(`${API_BASE}/status`),
        axios.get(`${API_BASE}/wallet/addresses`),
        axios.get(`${API_BASE}/blockchain`)
      ]);

      setStatus(statusRes.data);
      setAddresses(addressesRes.data.addresses);
      setBlockchain(blockchainRes.data.blocks.slice(-10)); // Last 10 blocks
      setMining(statusRes.data.mining);
    } catch (error) {
      addAlert('Error loading data', 'error');
    }
  }, [addAlert]);

  useEffect(() => {
    const socket = io('http://localhost:5000');
    
    loadData();
    
    // WebSocket listeners
    socket.on('new_block', (data) => {
      addAlert(`🎉 New block mined! #${data.index} - Reward: ${data.reward} BSC`, 'success');
      loadData();
    });

    socket.on('transaction', (data) => {
      addAlert(`💸 Transaction: ${data.amount} BSC sent`, 'info');
      loadData();
    });

    socket.on('new_address', (data) => {
      addAlert(`🆕 New address created: ${data.label}`, 'success');
      loadData();
    });

    return () => socket.disconnect();
  }, [loadData, addAlert]);

  const createAddress = async () => {
    try {
      await axios.post(`${API_BASE}/wallet/create`, { label: newAddressLabel });
      setNewAddressLabel('');
      loadData();
    } catch (error) {
      addAlert('Error creating address', 'error');
    }
  };

  const sendTransaction = async () => {
    try {
      await axios.post(`${API_BASE}/send`, {
        from: selectedAddress,
        to: sendForm.to,
        amount: sendForm.amount
      });
      setSendForm({ to: '', amount: '' });
      addAlert('Transaction sent successfully!', 'success');
    } catch (error) {
      addAlert(error.response?.data?.error || 'Transaction failed', 'error');
    }
  };

  const toggleMining = async () => {
    try {
      if (mining) {
        await axios.post(`${API_BASE}/mining/stop`);
      } else {
        await axios.post(`${API_BASE}/mining/start`, { address: selectedAddress });
      }
      setMining(!mining);
    } catch (error) {
      addAlert('Mining toggle failed', 'error');
    }
  };

  const totalBalance = addresses.reduce((sum, addr) => sum + addr.balance, 0);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" sx={{ background: 'linear-gradient(45deg, #ff6b35 30%, #f7931a 90%)' }}>
        <Toolbar>
          <AccountBalanceWallet sx={{ mr: 2 }} />
          <Typography variant="h4" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            BitsCoin 2025
          </Typography>
          <Chip 
            label={`${status.blockchain?.blocks || 0} Blocks`} 
            color="secondary" 
            sx={{ mr: 1 }}
          />
          <Chip 
            label={mining ? '⛏️ Mining' : '⏸️ Stopped'} 
            color={mining ? 'success' : 'default'}
          />
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3 }}>
        {/* Alerts */}
        <Box sx={{ mb: 2 }}>
          {alerts.map(alert => (
            <Alert key={alert.id} severity={alert.severity} sx={{ mb: 1 }}>
              {alert.message}
            </Alert>
          ))}
        </Box>

        <Grid container spacing={3}>
          {/* Wallet Overview */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  <AccountBalanceWallet sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Wallet Overview
                </Typography>
                <Typography variant="h3" color="primary" gutterBottom>
                  {totalBalance.toFixed(2)} BSC
                </Typography>
                
                <Box sx={{ mt: 2, mb: 2 }}>
                  <TextField
                    fullWidth
                    label="New Address Label"
                    value={newAddressLabel}
                    onChange={(e) => setNewAddressLabel(e.target.value)}
                    sx={{ mb: 1 }}
                  />
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={createAddress}
                    fullWidth
                  >
                    Create New Address
                  </Button>
                </Box>

                <List>
                  {addresses.map((addr, index) => (
                    <ListItem 
                      key={addr.address}
                      button
                      selected={selectedAddress === addr.address}
                      onClick={() => setSelectedAddress(addr.address)}
                    >
                      <ListItemText
                        primary={addr.label || `Address ${index + 1}`}
                        secondary={
                          <Box>
                            <Typography variant="body2">
                              {addr.address.substring(0, 20)}...
                            </Typography>
                            <Typography variant="h6" color="primary">
                              {addr.balance.toFixed(2)} BSC
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Send Transaction */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  <Send sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Send BitsCoin
                </Typography>
                
                <TextField
                  fullWidth
                  label="Recipient Address"
                  value={sendForm.to}
                  onChange={(e) => setSendForm({...sendForm, to: e.target.value})}
                  sx={{ mb: 2 }}
                />
                
                <TextField
                  fullWidth
                  label="Amount (BSC)"
                  type="number"
                  value={sendForm.amount}
                  onChange={(e) => setSendForm({...sendForm, amount: e.target.value})}
                  sx={{ mb: 2 }}
                />
                
                <Button
                  variant="contained"
                  onClick={sendTransaction}
                  disabled={!selectedAddress || !sendForm.to || !sendForm.amount}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Send Transaction
                </Button>

                <Button
                  variant={mining ? "outlined" : "contained"}
                  color={mining ? "error" : "success"}
                  onClick={toggleMining}
                  disabled={!selectedAddress}
                  fullWidth
                  startIcon={<TrendingUp />}
                >
                  {mining ? 'Stop Mining' : 'Start Mining'}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Blocks */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  <Layers sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Recent Blocks
                </Typography>
                
                <List>
                  {blockchain.map((block) => (
                    <ListItem key={block.index}>
                      <ListItemText
                        primary={`Block #${block.index}`}
                        secondary={
                          <Box>
                            <Typography variant="body2">
                              Hash: {block.hash.substring(0, 40)}...
                            </Typography>
                            <Typography variant="body2">
                              Data: {block.data.substring(0, 60)}...
                            </Typography>
                            <Typography variant="body2">
                              Time: {new Date(block.timestamp * 1000).toLocaleString()}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
}

export default App;
