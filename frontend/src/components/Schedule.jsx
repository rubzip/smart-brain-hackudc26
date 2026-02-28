import React from 'react';

const Schedule = ({ accessToken, handleAuthClick, schedule, upNext }) => {
    return (
        <article className="panel schedule-panel">
            <div className="schedule-header">
                <h2>Pending for Today</h2>
                <div className="schedule-actions">
                    {!accessToken ? (
                        <button className="connect-calendar-btn" onClick={handleAuthClick}>
                            <span className="google-icon">G</span> Connect Calendar
                        </button>
                    ) : (
                        <span className="event-count">{schedule.length} events</span>
                    )}
                </div>
            </div>

            {upNext && (
                <div className="up-next-banner">
                    <span className="up-next-label">UP NEXT</span>
                    <div className="up-next-content">
                        <span className="up-next-icon">{upNext.icon}</span>
                        <div className="up-next-details">
                            <h3>{upNext.title}</h3>
                            <span>{upNext.start} - {upNext.end}</span>
                        </div>
                    </div>
                </div>
            )}

            <div className="schedule-list">
                {schedule.filter(event => (upNext ? event.id !== upNext.id : true)).map(event => (
                    <div key={event.id} className={`schedule-card ${event.type}`}>
                        <span className="event-icon">{event.icon}</span>
                        <div className="event-info">
                            <h4>{event.title}</h4>
                            <span className="event-time">{event.start} - {event.end}</span>
                        </div>
                    </div>
                ))}
            </div>
        </article>
    );
};

export default Schedule;
