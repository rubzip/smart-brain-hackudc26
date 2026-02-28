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
                <header className="chat-window-header">
                    <h2>Add to Brain 🧠</h2>
                    <button className="close-chat" onClick={onClose}>✕</button>
                </header>

                <p className="modal-subtitle-premium">Expand your digital knowledge by saving new resources.</p>

                <div className="tab-switcher-premium">
                    <button
                        className={`tab-link ${activeTab === 'url' ? 'active' : ''}`}
                        onClick={() => setActiveTab('url')}
                    >
                        🌐 URL Link
                    </button>
                    <button
                        className={`tab-link ${activeTab === 'upload' ? 'active' : ''}`}
                        onClick={() => setActiveTab('upload')}
                    >
                        📁 Local File
                    </button>
                </div>

                <div className="add-item-body">
                    {activeTab === 'url' ? (
                        <div className="input-section">
                            <div className="input-group-premium">
                                <label>Title (Optional)</label>
                                <input
                                    type="text"
                                    placeholder="Enter a descriptive title"
                                    value={urlInfo.title}
                                    onChange={(e) => setUrlInfo({ ...urlInfo, title: e.target.value })}
                                />
                            </div>
                            <div className="input-group-premium">
                                <label>Resource URL</label>
                                <input
                                    type="url"
                                    placeholder="https://example.com/article"
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
                                            <span className="uploader-icon" style={{ fontSize: '2.5rem' }}>📤</span>
                                            <span style={{ fontWeight: 700 }}>Click to browse or drop file</span>
                                            <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>PDF, TXT, DOCX supported</span>
                                        </>
                                    )}
                                </label>
                            </div>
                        </div>
                    )}

                    <div className="category-section-premium">
                        <label className="section-label-tiny">Target Category</label>
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
                            {status === 'saving' ? 'Processing...' : status === 'success' ? 'Successfully Added! ✨' : 'Save to Brain'}
                        </button>
                        {status === 'error' && <p className="error-text-mini">Failed to save. Try again.</p>}
                    </footer>
                </div>
            </section>
        </div>
    );
};


export default AddItem;
