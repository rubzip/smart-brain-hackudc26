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
                <header className="chat-window-header">
                    <h2>Search Brain 🔍</h2>
                    <button className="close-chat" onClick={onClose}>✕</button>
                </header>

                <p className="modal-subtitle-premium">Locate any resource across your entire digital knowledge base.</p>

                <div className="search-tool-body">
                    <div className="search-input-wrapper">
                        <input
                            type="text"
                            placeholder="Type keywords (e.g., 'Clean Code', 'MIT')..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            autoFocus
                        />
                    </div>

                    <div className="search-categories">
                        <label className="section-label-tiny">Filter by categories</label>
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

                    <footer className="search-tool-footer" style={{ marginTop: '1.5rem' }}>
                        <button className="clear-link-btn" onClick={handleClear}>Reset filters</button>
                        <button className="search-submit-btn" onClick={handleSearch} style={{ padding: '14px 40px', fontSize: '1.05rem' }}>
                            Perform Search
                        </button>
                    </footer>
                </div>
            </article>
        </div>
    );
};


export default SearchTool;
