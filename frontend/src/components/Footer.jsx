import React from 'react';

const Footer = ({ onChatClick }) => {
    return (
        <footer className="bottom-bar">
            <section className="panel bottom-item" id="add-item-panel">
                <h2>Add new thing</h2>
                <button type="button" className="action-btn">+ New item</button>
            </section>

            <section className="panel bottom-item" id="chat-panel">
                <h2>Ask your Brain</h2>
                <div className="chat-row">
                    <button
                        type="button"
                        className="action-btn"
                        style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}
                        onClick={onChatClick}
                    >
                        <span style={{ fontSize: '1.2rem' }}>💬</span> Open AI Chat
                    </button>
                </div>
            </section>
        </footer>
    );
};

export default Footer;
