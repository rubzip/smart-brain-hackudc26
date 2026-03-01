/**
 * SPDX-License-Identifier: AGPL-3.0-or-later
 * Copyright (C) 2026 Smart Brain Contributors
 * This file is part of Smart Brain.
 * See LICENSE at the project root for full terms.
 */

import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, Tooltip } from 'recharts';

const StatsModal = ({ isStatsOpen, setIsStatsOpen, weeklyData }) => {
    if (!isStatsOpen) return null;

    return (
        <div className="modal-overlay" onClick={() => setIsStatsOpen(false)}>
            <div className="modal-content panel glass" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Weekly Performance</h2>
                    <button className="close-modal" onClick={() => setIsStatsOpen(false)}>✕</button>
                </div>
                <p className="modal-subtitle">You surpassed 80% of your goals on 3 days this week! 🔥</p>

                <div className="chart-wrapper">
                    <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={weeklyData}>
                            <defs>
                                <linearGradient id="colorComp" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <XAxis
                                dataKey="day"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#94a3b8', fontSize: 12 }}
                                dy={10}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '12px',
                                    color: '#fff'
                                }}
                                itemStyle={{ color: '#818cf8', fontWeight: 'bold' }}
                                cursor={{ stroke: '#6366f1', strokeWidth: 1, strokeDasharray: '5 5' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="completion"
                                stroke="#6366f1"
                                strokeWidth={4}
                                fillOpacity={1}
                                fill="url(#colorComp)"
                                animationDuration={1500}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                <div className="modal-footer-stats">
                    <div className="stat-pill">
                        <span className="pill-label">Avg. Focus</span>
                        <span className="pill-value">72%</span>
                    </div>
                    <div className="stat-pill">
                        <span className="pill-label">Avg. Feeling</span>
                        <span className="pill-value">Great 😄</span>
                    </div>
                    <div className="stat-pill">
                        <span className="pill-label">Peak Day</span>
                        <span className="pill-value">Friday</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StatsModal;
