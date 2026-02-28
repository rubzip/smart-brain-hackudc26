import React from 'react';

const TodoList = ({ tasks, completedCount, progress, toggleTask }) => {
    return (
        <article className="panel dopamine-todo">
            <div className="todo-header">
                <h2>Daily Goals</h2>
                <div className="progress-stat">{completedCount}/{tasks.length}</div>
            </div>

            <div className="progress-container">
                <div className="progress-bar" style={{ width: `${progress}%` }}></div>
            </div>

            <ul className="todo-list">
                {tasks.map(task => (
                    <li
                        key={task.id}
                        className={`todo-item ${task.completed ? 'completed' : ''}`}
                        onClick={() => toggleTask(task.id)}
                    >
                        <div className="checkbox">
                            {task.completed && <span className="check-mark">✓</span>}
                        </div>
                        <span className="task-text">{task.text}</span>
                    </li>
                ))}
            </ul>

            {completedCount === tasks.length && (
                <div className="all-done-msg">✨ You're crushing it! All goals done! ✨</div>
            )}
        </article>
    );
};

export default TodoList;
