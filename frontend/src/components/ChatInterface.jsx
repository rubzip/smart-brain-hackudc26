import React from 'react';
import { DeepChat } from 'deep-chat-react';
import { API_BASE_URL } from '../config';

const ChatInterface = ({ isOpen, onClose }) => {
    if (!isOpen) return null;

    return (
        <div className="chat-window-overlay" onClick={onClose}>
            <div className="chat-window-container glass" onClick={(e) => e.stopPropagation()}>
                <div className="chat-window-header">
                    <h3>Smart Brain Chat 🧠</h3>
                    <button className="close-chat" onClick={onClose}>✕</button>
                </div>

                <DeepChat
                    demo={false}
                    request={{
                        url: `${API_BASE_URL}/chat`,
                        method: 'POST',
                        serialize: (body) => {
                            const lastMessage = body.messages[body.messages.length - 1];
                            return JSON.stringify({ message: lastMessage.text });
                        }
                    }}
                    style={{
                        borderRadius: '16px',
                        padding: '10px',
                        width: '100%',
                        height: '450px',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        backgroundColor: 'rgba(15, 23, 42, 0.95)', // Solid dark background to avoid transparency issues
                    }}
                    messageStyles={{
                        default: {
                            user: {
                                bubble: { backgroundColor: '#4f46e5', color: '#ffffff' }
                            },
                            ai: {
                                bubble: {
                                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                                    color: '#f8fafc', // Using var(--text-main) equivalent
                                    border: '1px solid rgba(255, 255, 255, 0.1)'
                                }
                            },
                        }
                    }}
                    inputAreaStyle={{
                        backgroundColor: 'rgba(51, 65, 85, 0.5)', // Slate background for input area
                        borderRadius: '12px',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                    }}
                    textInput={{
                        placeholder: { text: 'Write a message...', style: { color: '#94a3b8' } },
                        style: {
                            color: '#ffffff', // Explicitly white text for input
                            backgroundColor: 'transparent'
                        }
                    }}
                    submitButtonStyles={{
                        submit: {
                            container: {
                                default: {
                                    backgroundColor: '#6366f1',
                                }
                            }
                        }
                    }}
                />
            </div>
        </div>
    );
};

export default ChatInterface;
