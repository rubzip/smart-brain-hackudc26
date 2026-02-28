import React, { useState } from 'react';
import { API_BASE_URL } from '../config';

const AddItem = ({ isOpen, onClose }) => {
    const [activeTab, setActiveTab] = useState('url'); // 'url' or 'upload'
    const [status, setStatus] = useState('idle'); // 'idle', 'saving', 'success', 'error'
    const [urlInfo, setUrlInfo] = useState({ title: '', url: '', category: 'Work' });
    const [fileInfo, setFileInfo] = useState({ file: null, category: 'Work' });

    if (!isOpen) return null;

    const categories = [
        { id: 'Work', label: 'Work', emoji: '💼' },
        { id: 'Personal', label: 'Personal', emoji: '🏠' },
        { id: 'Watch Later', label: 'Watch Later', emoji: '⏳' }
    ];

    const handleUrlSave = async () => {
        if (!urlInfo.url) return;
        setStatus('saving');
        try {
            const response = await fetch(`${API_BASE_URL}/items/urls`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: urlInfo.url,
                    title: urlInfo.title || null,
                    tags: [urlInfo.category]
                }),
            });

            if (response.ok) {
                setStatus('success');
                setUrlInfo({ title: '', url: '', category: 'Work' });
                setTimeout(() => {
                    setStatus('idle');
                    onClose();
                }, 2000);
            } else {
                setStatus('error');
            }
        } catch (err) {
            console.error('URL save failed:', err);
            setStatus('error');
        }
    };

    const handleFileUpload = async () => {
        if (!fileInfo.file) return;
        setStatus('saving');
        const formData = new FormData();
        formData.append('file', fileInfo.file);

        try {
            const response = await fetch(`${API_BASE_URL}/items/files`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                setStatus('success');
                setFileInfo({ file: null, category: 'Work' });
                setTimeout(() => {
                    setStatus('idle');
                    onClose();
                }, 2000);
            } else {
                setStatus('error');
            }
        } catch (err) {
            console.error('File upload failed:', err);
            setStatus('error');
        }
    };

    const currentData = activeTab === 'url' ? urlInfo : fileInfo;
    const setCategory = (catId) => {
        if (activeTab === 'url') {
            setUrlInfo({ ...urlInfo, category: catId });
        } else {
            setFileInfo({ ...fileInfo, category: catId });
        }
    };

    return (
        <div className="chat-window-overlay" onClick={onClose}>
            <section className="chat-window-container glass add-item-overlay" onClick={(e) => e.stopPropagation()}>
                <header className="add-item-header">
                    <div className="header-top">
                        <div className="brain-icon">🧠</div>
                        <h2>Add to Brain</h2>
                        <button className="close-chat" onClick={onClose} style={{ marginLeft: 'auto' }}>✕</button>
                    </div>
                    <div className="tab-switcher-premium">
                        <button
                            className={`tab-link ${activeTab === 'url' ? 'active' : ''}`}
                            onClick={() => setActiveTab('url')}
                        >
                            URL
                        </button>
                        <button
                            className={`tab-link ${activeTab === 'upload' ? 'active' : ''}`}
                            onClick={() => setActiveTab('upload')}
                        >
                            File
                        </button>
                    </div>
                </header>

                <div className="add-item-body">
                    {activeTab === 'url' ? (
                        <div className="input-section">
                            <div className="input-group-premium">
                                <label>Title (Optional)</label>
                                <input
                                    type="text"
                                    placeholder="Article or video title"
                                    value={urlInfo.title}
                                    onChange={(e) => setUrlInfo({ ...urlInfo, title: e.target.value })}
                                />
                            </div>
                            <div className="input-group-premium">
                                <label>URL</label>
                                <input
                                    type="url"
                                    placeholder="https://youtube.com/..."
                                    value={urlInfo.url}
                                    onChange={(e) => setUrlInfo({ ...urlInfo, url: e.target.value })}
                                />
                            </div>
                        </div>
                    ) : (
                        <div className="input-section">
                            <div className="file-uploader-premium">
                                <input
                                    type="file"
                                    id="file-brain-input"
                                    onChange={(e) => setFileInfo({ ...fileInfo, file: e.target.files[0] })}
                                    hidden
                                />
                                <label htmlFor="file-brain-input" className="uploader-box">
                                    {fileInfo.file ? (
                                        <div className="selected-file">
                                            <span className="file-icon">📄</span>
                                            <span className="file-name-text">{fileInfo.file.name}</span>
                                        </div>
                                    ) : (
                                        <>
                                            <span className="uploader-icon">📁</span>
                                            <span>Click to browse files</span>
                                        </>
                                    )}
                                </label>
                            </div>
                        </div>
                    )}

                    <div className="category-section-premium">
                        <label className="section-label-tiny">Category</label>
                        <div className="category-list-vertical">
                            {categories.map(cat => (
                                <div
                                    key={cat.id}
                                    className={`category-row-item ${currentData.category === cat.id ? 'selected' : ''}`}
                                    onClick={() => setCategory(cat.id)}
                                >
                                    <span className="cat-emoji">{cat.emoji}</span>
                                    <span className="cat-label-text">{cat.label}</span>
                                    {currentData.category === cat.id && <span className="cat-checkmark">✓</span>}
                                </div>
                            ))}
                        </div>
                    </div>

                    <footer className="add-item-footer">
                        <button
                            className={`save-brain-btn ${status === 'saving' ? 'loading' : ''} ${status === 'success' ? 'success' : ''}`}
                            onClick={activeTab === 'url' ? handleUrlSave : handleFileUpload}
                            disabled={status === 'saving' || (activeTab === 'url' ? !urlInfo.url : !fileInfo.file)}
                        >
                            {status === 'saving' ? 'Processing...' : status === 'success' ? 'Saved Successfully!' : 'Save to Brain'}
                        </button>
                        {status === 'error' && <p className="error-text-mini">Failed to save. Try again.</p>}
                    </footer>
                </div>
            </section>
        </div>
    );
};


export default AddItem;
