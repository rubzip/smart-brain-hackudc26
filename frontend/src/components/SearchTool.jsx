import React, { useState } from 'react';

const SearchTool = ({ onSearch, onClear }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [selectedTags, setSelectedTags] = useState([]);

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
    };

    const handleClear = () => {
        setQuery('');
        setSelectedTags([]);
        onClear();
    };

    if (!isOpen) {
        return (
            <button className="search-toggle-btn premium-btn" onClick={() => setIsOpen(true)}>
                <span className="search-icon">🔍</span> Search Brain
            </button>
        );
    }

    return (
        <article className="panel search-tool-panel">
            <header className="search-tool-header">
                <div className="header-left">
                    <span className="search-icon-small">🔍</span>
                    <h3>Search</h3>
                </div>
                <button className="close-tool-btn" onClick={() => setIsOpen(false)}>✕</button>
            </header>

            <div className="search-tool-body">
                <div className="search-input-wrapper">
                    <input
                        type="text"
                        placeholder="Search for files or videos..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    />
                </div>

                <div className="search-categories">
                    <label className="section-label-tiny">Filter by Category</label>
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

                <footer className="search-tool-footer">
                    <button className="clear-link-btn" onClick={handleClear}>Clear</button>
                    <button className="search-submit-btn" onClick={handleSearch}>Search</button>
                </footer>
            </div>
        </article>
    );
};

export default SearchTool;
