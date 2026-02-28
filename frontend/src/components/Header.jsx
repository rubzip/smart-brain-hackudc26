import React from 'react';

const Header = () => {
    return (
        <header className="top-nav panel">
            <h1 className="app-title">Smart Brain <span className="logo-emoji">🧠</span></h1>
            <nav className="nav-actions" aria-label="Quick navigation">
                <a className="nav-link" href="#add-item-panel">Add items</a>
                <a className="nav-link" href="#chat-panel">Chat</a>
            </nav>
        </header>
    );
};

export default Header;
