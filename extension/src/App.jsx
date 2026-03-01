/**
 * SPDX-License-Identifier: AGPL-3.0-or-later
 * Copyright (C) 2026 Smart Brain Contributors
 * This file is part of Smart Brain.
 * See LICENSE at the project root for full terms.
 */

import React, { useState, useEffect } from 'react';

// Cross-browser compatibility: Firefox uses 'browser' API, Chrome uses 'chrome' API
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;
const API_BASE_URL = 'http://localhost:5000/api/v1';

const App = () => {
    const [pageInfo, setPageInfo] = useState({ title: '', url: '', category: 'Work' });
    const [status, setStatus] = useState('idle'); // idle, saving, success, error

    const categories = [
        { id: 'Work', label: 'Work', emoji: '💼' },
        { id: 'Personal', label: 'Personal', emoji: '🏠' },
        { id: 'Watch Later', label: 'Watch Later', emoji: '⏳' }
    ];

    useEffect(() => {
        // Get current tab info
        if (browserAPI && browserAPI.tabs) {
            browserAPI.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
                const activeTab = tabs[0];
                if (activeTab) {
                    setPageInfo(prev => ({
                        ...prev,
                        title: activeTab.title || '',
                        url: activeTab.url || ''
                    }));
                }
            }).catch(err => {
                console.warn('Tab query failed, using mock data:', err);
            });
        }
    }, []);

    const handleSave = async () => {
        if (!pageInfo.url) return;
        setStatus('saving');
        try {
            const response = await fetch(`${API_BASE_URL}/items/urls`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: pageInfo.url,
                    title: pageInfo.title || null,
                    tags: [pageInfo.category]
                }),
            });

            if (response.ok) {
                setStatus('success');
                setTimeout(() => setStatus('idle'), 3000);
            } else {
                setStatus('error');
            }
        } catch (err) {
            console.error('Save failed:', err);
            setStatus('error');
        }
    };

    return (
        <div className="extension-container glass">
            <header className="add-item-header">
                <div className="header-top">
                    <span className="brain-icon">🧠</span>
                    <h2>Smart Brain</h2>
                </div>
                <p className="modal-subtitle-tiny">Instant knowledge preservation.</p>
            </header>

            <div className="add-item-body">
                <div className="detected-info-premium">
                    <span className="detected-label">Detected Page</span>
                    <h3 className="detected-title">{pageInfo.title || 'Untitled Page'}</h3>
                    <span className="detected-url">{pageInfo.url}</span>
                </div>

                <div className="category-section-premium">
                    <label className="section-label-tiny">Save to Category</label>
                    <div className="category-list-vertical">
                        {categories.map((cat) => (
                            <div
                                key={cat.id}
                                className={`category-row-item ${pageInfo.category === cat.id ? 'selected' : ''}`}
                                onClick={() => setPageInfo({ ...pageInfo, category: cat.id })}
                            >
                                <span className="cat-emoji">{cat.emoji}</span>
                                <span className="cat-label-text">{cat.label}</span>
                                {pageInfo.category === cat.id && <span className="cat-checkmark">✓</span>}
                            </div>
                        ))}
                    </div>
                </div>

                <footer className="add-item-footer">
                    <button
                        className={`save-brain-btn ${status === 'saving' ? 'loading' : ''} ${status === 'success' ? 'success' : ''}`}
                        onClick={handleSave}
                        disabled={status === 'saving' || !pageInfo.url}
                    >
                        {status === 'saving' ? (
                            <span className="loading-icon">⏳</span>
                        ) : status === 'success' ? (
                            'Saved to Brain! ✨'
                        ) : (
                            'Save to Brain'
                        )}
                    </button>
                    {status === 'error' && <p className="error-text-mini">Failed to save. Is the backend running?</p>}
                </footer>
            </div>
        </div>
    );
};

export default App;
