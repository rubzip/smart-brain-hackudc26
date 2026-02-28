import React from 'react';

const MoodDock = ({ moodFeedback, moods, handleMoodSubmit, setIsStatsOpen, setMoodFeedback, setSelectedMood }) => {
    return (
        <div className="mood-dock-container">
            <div className={`mood-dock ${moodFeedback ? 'expanded' : ''}`}>
                {!moodFeedback ? (
                    <div className="dock-content">
                        <span className="dock-prompt">How's your vibe?</span>
                        <div className="dock-moods">
                            <button
                                className="dock-mood-btn analytics-btn"
                                onClick={() => setIsStatsOpen(true)}
                                title="Weekly Stats"
                            >
                                <span className="dock-emoji">📊</span>
                                <span className="dock-label">Stats</span>
                            </button>
                            <div className="dock-divider"></div>
                            {moods.map(mood => (
                                <button
                                    key={mood.value}
                                    className="dock-mood-btn"
                                    onClick={() => handleMoodSubmit(mood.value)}
                                >
                                    <span className="dock-emoji">{mood.emoji}</span>
                                    <span className="dock-label">{mood.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="dock-feedback">
                        <span className="dock-message">{moodFeedback}</span>
                        <button className="dock-close" onClick={() => { setMoodFeedback(null); setSelectedMood(null); }}>✕</button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MoodDock;
