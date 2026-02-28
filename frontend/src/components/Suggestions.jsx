import React from 'react';

const Suggestions = ({ suggestions, currentSuggestion, prevSuggestion, nextSuggestion, setCurrentSuggestion }) => {
    const getYoutubeId = (url) => {
        if (!url) return null;
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    };

    return (
        <section className="panel right-column suggestion-carousel-panel">
            <h2>Your Brain Suggestions</h2>
            <p className="section-description">Your content recommendations for today</p>
            <div className="carousel-container">
                <button className="carousel-btn prev" onClick={prevSuggestion}>←</button>

                <div className="carousel-track">
                    {suggestions.map((item, index) => {
                        const youtubeId = getYoutubeId(item.youtube_url);
                        return (
                            <div
                                key={item.id}
                                className={`suggestion-card ${index === currentSuggestion ? 'active' : ''}`}
                                style={{ transform: `translateX(${(index - currentSuggestion) * 105}%)` }}
                            >
                                <div className="card-content-wrapper">
                                    {youtubeId ? (
                                        <div className="video-embed">
                                            <iframe
                                                width="100%"
                                                src={`https://www.youtube.com/embed/${youtubeId}`}
                                                title="YouTube video player"
                                                frameBorder="0"
                                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                                allowFullScreen
                                            ></iframe>
                                        </div>
                                    ) : (
                                        <div className="card-icon-container">
                                            <span className="card-icon-large">{item.icon}</span>
                                        </div>
                                    )}
                                    <div className="card-details">
                                        <div className="card-tag">{item.type}</div>
                                        <h3 className="card-title">
                                            <a href={item.url} target="_blank" rel="noopener noreferrer">
                                                {item.title}
                                            </a>
                                        </h3>
                                        {item.summary && <p className="card-summary">{item.summary}</p>}
                                    </div>
                                </div>
                                <a href={item.url} target="_blank" rel="noopener noreferrer" className="open-btn-link">
                                    View full content
                                </a>
                            </div>
                        );
                    })}
                </div>

                <button className="carousel-btn next" onClick={nextSuggestion}>→</button>
            </div>

            <div className="carousel-indicators">
                {suggestions.map((_, index) => (
                    <div
                        key={index}
                        className={`indicator ${index === currentSuggestion ? 'active' : ''}`}
                        onClick={() => setCurrentSuggestion(index)}
                    ></div>
                ))}
            </div>
        </section>
    );
};

export default Suggestions;
