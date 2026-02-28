import React, { useMemo } from 'react';
import { DeepChat } from 'deep-chat-react';
import { API_BASE_URL } from '../config';

const ChatInterface = React.memo(({ isOpen, onClose }) => {
    const chatRequest = useMemo(() => ({
        url: `${API_BASE_URL}/chat`,
        method: 'POST',
        serialize: (body) => {
            const lastMessage = body.messages[body.messages.length - 1];
            return JSON.stringify({ message: lastMessage.text });
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
                    demo={false}
                    request={chatRequest}
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

