import React, { useState } from 'react';

const SearchTool = ({ isOpen, onClose, onSearch, onClear }) => {
    const [query, setQuery] = useState('');
    const [selectedTags, setSelectedTags] = useState([]);

    if (!isOpen) return null;

    const categories = [
        { id: 'Work', label: 'Work', emoji: '💼' },
        { id: 'Personal', label: 'Personal', emoji: '🏠' },
        { id: 'Watch Later', label: 'Watch Later', emoji: '⏳' }
    ];

    const toggleTag = (tagId) => {
        setSelectedTags(prev =>
            prev.includes(tagId)
                ? prev.filter(t => t !== tagId)
                : [...prev, tagId]
        );
    };

    const handleSearch = () => {
        if (!query && selectedTags.length === 0) return;
        onSearch({ query, tags: selectedTags });
        onClose();
    };

    const handleClear = () => {
        setQuery('');
        setSelectedTags([]);
        onClear();
    };

    return (
        <div className="chat-window-overlay" onClick={onClose}>
            <article className="chat-window-container glass search-tool-overlay" onClick={(e) => e.stopPropagation()}>
                <header className="search-tool-header">
                    <div className="header-left">
                        <span className="search-icon-small">🔍</span>
                        <h3>Search</h3>
                    </div>
                    <button className="close-chat" onClick={onClose}>✕</button>
                </header>

                <div className="search-tool-body">
                    <div className="search-input-wrapper">
                        <input
                            type="text"
                            placeholder="Find files, videos, or articles..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            autoFocus
                        />
                    </div>

                    <div className="search-categories">
                        <label className="section-label-tiny">Filter by Brain Category</label>
                        <div className="categories-grid-tiny">
                            {categories.map(cat => (
                                <button
                                    key={cat.id}
                                    className={`cat-chip-tiny ${selectedTags.includes(cat.id) ? 'active' : ''}`}
                                    onClick={() => toggleTag(cat.id)}
                                >
                                    <span className="cat-emoji-tiny">{cat.emoji}</span>
                                    <span className="cat-label-tiny">{cat.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    <footer className="search-tool-footer" style={{ marginTop: '1rem' }}>
                        <button className="clear-link-btn" onClick={handleClear} style={{ fontSize: '0.95rem' }}>Clear filters</button>
                        <button className="search-submit-btn" onClick={handleSearch} style={{ padding: '12px 32px', fontSize: '1rem' }}>
                            Search Brain
                        </button>
                    </footer>
                </div>
            </article>
        </div>
    );
};


export default SearchTool;
