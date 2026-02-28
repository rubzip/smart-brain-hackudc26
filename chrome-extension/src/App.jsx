import React, { useState, useEffect } from 'react';

const App = () => {
    const [pageInfo, setPageInfo] = useState({ title: '', url: '' });
    const [category, setCategory] = useState('Work');
    const [status, setStatus] = useState('idle'); // idle, saving, success, error

    const categories = [
        { id: 'Work', label: 'Work', emoji: '💼' },
        { id: 'Personal', label: 'Personal', emoji: '🏠' },
        { id: 'Watch Later', label: 'Watch Later', emoji: '⏳' }
    ];

    useEffect(() => {
        // Get current tab info
        if (typeof chrome !== 'undefined' && chrome.tabs) {
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                const activeTab = tabs[0];
                setPageInfo({
                    title: activeTab.title || '',
                    url: activeTab.url || ''
                });
            });
        } else {
            // Mock for development
            setPageInfo({ title: 'Mock Page', url: 'https://example.com' });
        }
    }, []);

    const handleSave = async () => {
        setStatus('saving');
        try {
            const response = await fetch('http://localhost:5000/api/v1/items/urls', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: pageInfo.url,
                    title: pageInfo.title,
                    tags: [category]
                }),
            });

            if (response.ok) {
                setStatus('success');
            } else {
                setStatus('error');
            }
        } catch (err) {
            console.error('Save failed:', err);
            setStatus('error');
        }
    };

    return (
        <div className="container">
            <header>
                <div className="icon-wrapper">🧠</div>
                <h1>Smart Brain</h1>
            </header>

            <div className="section">
                <div className="page-details">
                    <div className="title-field">{pageInfo.title || 'Untitled'}</div>
                    <div className="url-field">{pageInfo.url}</div>
                </div>
            </div>

            <div className="section">
                <div className="section-label">Category</div>
                <div className="category-list">
                    {categories.map((cat) => (
                        <div
                            key={cat.id}
                            className={`category-item ${category === cat.id ? 'selected' : ''}`}
                            onClick={() => setCategory(cat.id)}
                        >
                            <span className="emoji">{cat.emoji}</span>
                            <span className="label">{cat.label}</span>
                            {category === cat.id && <span className="check">✓</span>}
                        </div>
                    ))}
                </div>
            </div>

            <footer className="footer-actions">
                <button
                    className={`save-btn ${status === 'saving' ? 'loading' : ''}`}
                    onClick={handleSave}
                    disabled={status === 'saving'}
                >
                    {status === 'saving' ? 'Saving...' : status === 'success' ? 'Added to Brain' : 'Save to Brain'}
                </button>
                {status === 'error' && <div className="status-msg error">Failed to save</div>}
                {status === 'success' && <div className="status-msg success">Saved to database!</div>}
            </footer>
        </div>
    );
};

export default App;
