/**
 * Smart Brain - Chat Interface with RAG
 * Copyright (C) 2026 Smart Brain Contributors
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import React, { useMemo } from 'react';
import { DeepChat } from 'deep-chat-react';
import { API_BASE_URL } from '../config';

const ChatInterface = React.memo(({ isOpen, onClose }) => {
    const connectConfig = useMemo(() => ({
        url: `${API_BASE_URL}/chat`,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        additionalBodyProps: {
            retrieval_scope: [],
            delete_item_ids: []
        }
    }), []);

    const chatStyle = useMemo(() => ({
        borderRadius: '16px',
        padding: '10px',
        width: '100%',
        height: '450px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
    }), []);

    const messageStyles = useMemo(() => ({
        default: {
            user: { bubble: { backgroundColor: '#4f46e5', color: '#ffffff' } },
            ai: {
                bubble: {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    color: '#f8fafc',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                }
            },
        }
    }), []);

    const inputAreaStyle = useMemo(() => ({
        backgroundColor: 'rgba(51, 65, 85, 0.5)',
        borderRadius: '12px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
    }), []);

    const textInput = useMemo(() => ({
        placeholder: { text: 'Write a message...', style: { color: '#94a3b8' } },
        style: { color: '#ffffff', backgroundColor: 'transparent' }
    }), []);

    const submitButtonStyles = useMemo(() => ({
        submit: {
            container: { default: { backgroundColor: '#6366f1' } }
        }
    }), []);

    if (!isOpen) return null;

    return (
        <div className="chat-window-overlay" onClick={onClose}>
            <div className="chat-window-container glass" onClick={(e) => e.stopPropagation()}>
                <div className="chat-window-header">
                    <h3>Smart Brain Chat 🧠</h3>
                    <button className="close-chat" onClick={onClose}>✕</button>
                </div>

                <DeepChat
                    connect={connectConfig}
                    requestInterceptor={(details) => {
                        // DeepChat sends { messages: [{role, text}] }
                        // Backend expects { message: string, retrieval_scope: [], delete_item_ids: [] }
                        if (details.body) {
                            const parsed = typeof details.body === 'string' 
                                ? JSON.parse(details.body) 
                                : details.body;
                            
                            const lastMessage = parsed.messages?.[parsed.messages.length - 1];
                            const transformedBody = {
                                message: lastMessage?.text || '',
                                retrieval_scope: [],
                                delete_item_ids: []
                            };
                            
                            // Return the object, let DeepChat serialize it
                            details.body = transformedBody;
                            console.log('Sending to backend:', transformedBody);
                        }
                        return details;
                    }}
                    style={chatStyle}
                    messageStyles={messageStyles}
                    inputAreaStyle={inputAreaStyle}
                    textInput={textInput}
                    submitButtonStyles={submitButtonStyles}
                />
            </div>
        </div>
    );
});



export default ChatInterface;

