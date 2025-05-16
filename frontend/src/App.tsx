import React, { useState, useEffect, useRef, useMemo } from 'react';
import { ConnectionProvider, WalletProvider, useWallet } from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets';
import { WalletModalProvider, WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';
import './App.css';

// Import wallet adapter CSS
require('@solana/wallet-adapter-react-ui/styles.css');

interface Message {
  text: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  isHtml?: boolean;
}

function ChatApp() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { publicKey } = useWallet();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !publicKey) return;

    const userMessage: Message = {
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      let wallet_address = publicKey.toString();
      let query = `For the wallet address ${wallet_address}, ${inputValue}`;
      const response = await fetch('http://localhost:8082/post/query_response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          summary: query,
        })
      });

      const data = await response.json();
      console.log(data);
      
      // Check if the response contains HTML
      const isHtml = /<[a-z][\s\S]*>/i.test(data.summary);
      
      const assistantMessage: Message = {
        text: data.summary,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        isHtml: isHtml
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGetChainData = async () => {
    if (!address.trim() || !publicKey) return;

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/chain/summary/${address}`);
      const data = await response.json();

      const assistantMessage: Message = {
        text: `Chain data for ${address}:\n${JSON.stringify(data, null, 2)}`,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-container">
      <header className="header">
        <div className="logo">Soldapper.dev</div>
        <WalletMultiButton className="wallet-btn" />
      </header>
      <main className="chat-container">
        <div className="messages-container">
          {!publicKey && (
            <div className="message assistant-message">
              <div className="message-content">
                Please connect your wallet to start chatting
              </div>
            </div>
          )}
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.sender === 'user' ? 'user-message' : 'assistant-message'}`}
            >
              <div className="message-content">
                {message.isHtml ? (
                  <div dangerouslySetInnerHTML={{ __html: message.text }} />
                ) : (
                  message.text
                )}
              </div>
              <div className="message-timestamp">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message assistant-message">
              <div className="message-content">
                <div className="loading-dots">
                  <span>.</span><span>.</span><span>.</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>
      <footer className="input-footer">
        <div className="input-bar">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={publicKey ? "Ask anything" : "Connect wallet to chat"}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={!publicKey}
          />
          <button 
            className="icon-btn" 
            onClick={handleSendMessage}
            disabled={!publicKey}
          >
            <span role="img" aria-label="send">➤</span>
          </button>
        </div>
      </footer>
    </div>
  );
}

function App() {
  // The network can be set to 'devnet', 'testnet', or 'mainnet-beta'
  const network = WalletAdapterNetwork.Devnet;

  // You can also provide a custom RPC endpoint
  const endpoint = useMemo(() => clusterApiUrl(network), [network]);

  // @solana/wallet-adapter-wallets includes all the adapters but supports tree shaking and lazy loading
  const wallets = useMemo(
    () => [
      new PhantomWalletAdapter(),
    ],
    []
  );

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <ChatApp />
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}

export default App;
