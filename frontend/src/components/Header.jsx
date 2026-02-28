import React from 'react';

const Header = ({ onAddClick, onSearchClick, onChatClick }) => {
    return (
        <header className="top-nav panel">
            <h1 className="app-title">Smart Brain <span className="logo-emoji">🧠</span></h1>
            <nav className="nav-actions" aria-label="Quick navigation">
                <button className="nav-link-btn" onClick={onAddClick}>
                    <span className="nav-btn-icon">+</span> Add items
                </button>
                <button className="nav-link-btn" onClick={onSearchClick}>
                    <span className="nav-btn-icon">🔍</span> Search
                </button>
                <button className="nav-link-btn" onClick={onChatClick}>
                    <span className="nav-btn-icon">💬</span> Chat
                </button>
            </nav>
        </header>
    );
};

export default Header;

