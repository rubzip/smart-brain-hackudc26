/**
 * SPDX-License-Identifier: AGPL-3.0-or-later
 * Copyright (C) 2026 Smart Brain Contributors
 * This file is part of Smart Brain.
 * See LICENSE at the project root for full terms.
 */

import React, { useState, useEffect } from 'react';

// Cross-browser compatibility: Firefox uses 'browser' API, Chrome uses 'chrome' API
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

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
        // Get current tab info (works in both Chrome and Firefox)
        if (browserAPI && browserAPI.tabs) {
            browserAPI.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
                const activeTab = tabs[0];
                setPageInfo({
                    title: activeTab.title || '',
                    url: activeTab.url || ''
                });
            }).catch(() => {
                // Fallback for development or errors
                setPageInfo({ title: 'Mock Page', url: 'https://example.com' });
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
        <div className="add-item-panel extension-container">
            <header className="add-item-header">
                <div className="header-top">
                    <div className="brain-icon">🧠</div>
                    <h2>Smart Brain</h2>
                </div>
            </header>

            <div className="add-item-body">
                <div className="input-section">
                    <div className="input-group-premium">
                        <label>Title</label>
                        <input
                            type="text"
                            placeholder="Title"
                            value={pageInfo.title}
                            onChange={(e) => setPageInfo({ ...pageInfo, title: e.target.value })}
                        />
                    </div>
                    <div className="input-group-premium">
                        <label>URL</label>
                        <input
                            type="url"
                            placeholder="URL"
                            value={pageInfo.url}
                            onChange={(e) => setPageInfo({ ...pageInfo, url: e.target.value })}
                        />
                    </div>
                </div>

                <div className="category-section-premium">
                    <label className="section-label-tiny">Category</label>
                    <div className="category-list-vertical">
                        {categories.map((cat) => (
                            <div
                                key={cat.id}
                                className={`category-row-item ${category === cat.id ? 'selected' : ''}`}
                                onClick={() => setCategory(cat.id)}
                            >
                                <span className="cat-emoji">{cat.emoji}</span>
                                <span className="cat-label-text">{cat.label}</span>
                                {category === cat.id && <span className="cat-checkmark">✓</span>}
                            </div>
                        ))}
                    </div>
                </div>

                <footer className="add-item-footer">
                    <button
                        className={`save-brain-btn ${status === 'saving' ? 'loading' : ''} ${status === 'success' ? 'success' : ''}`}
                        onClick={handleSave}
                        disabled={status === 'saving'}
                    >
                        {status === 'saving' ? 'Saving...' : status === 'success' ? 'Saved Successfully!' : 'Save to Brain'}
                    </button>
                    {status === 'error' && <p className="error-text-mini">Failed to save. Try again.</p>}
                </footer>
            </div>
        </div>
    );
};

export default App;
