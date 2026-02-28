import React, { useState, useEffect } from 'react'
import confetti from 'canvas-confetti'
import './App.css'

function App() {
  const [tasks, setTasks] = useState([
    { id: 1, text: '📖 Read 20 pages', completed: false },
    { id: 2, text: '🚿 Take a shower', completed: false },
    { id: 3, text: '👟 Walk 10k steps', completed: false },
    { id: 4, text: '🏋️ Exercise', completed: false },
    { id: 5, text: '👵 Call your grandma', completed: false }
  ])

  const completedCount = tasks.filter(t => t.completed).length
  const progress = (completedCount / tasks.length) * 100

  const toggleTask = (id) => {
    setTasks(prev => prev.map(task => {
      if (task.id === id) {
        const newStatus = !task.completed
        if (newStatus) {
          triggerDopamine()
        }
        return { ...task, completed: newStatus }
      }
      return task
    }))
  }

  const triggerDopamine = () => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#2563eb', '#10b981', '#f59e0b', '#ec4899']
    })
  }

  useEffect(() => {
    if (completedCount === tasks.length && tasks.length > 0) {
      // Mega Celebration
      const duration = 3 * 1000
      const end = Date.now() + duration

      const frame = () => {
        confetti({
          particleCount: 5,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: ['#2563eb', '#10b981']
        })
        confetti({
          particleCount: 5,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: ['#f59e0b', '#ec4899']
        })

        if (Date.now() < end) {
          requestAnimationFrame(frame)
        }
      }
      frame()
    }
  }, [completedCount, tasks.length])

  return (
    <div className="app-shell">
      <header className="top-nav panel">
        <h1 className="app-title">Smart Brain <span className="logo-emoji">🧠</span></h1>
        <nav className="nav-actions" aria-label="Quick navigation">
          <a className="nav-link" href="#add-item-panel">Add items</a>
          <a className="nav-link" href="#chat-panel">Chat</a>
        </nav>
      </header>

      <main className="main-area">
        <section className="left-column">
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

          <article className="panel">
            <h2>Pending calendar events</h2>
            <ul className="event-list">
              <li>Mon · Team sync · 10:00</li>
              <li>Tue · Design review · 12:30</li>
              <li>Thu · Demo prep · 16:00</li>
            </ul>
          </article>
        </section>

        <section className="panel right-column">
          <h2>Suggestions (stored links)</h2>
          <ul className="suggestion-list">
            <li>Article: Building better prompts</li>
            <li>Video: React state patterns</li>
            <li>Paper: Retrieval-augmented systems</li>
            <li>Talk: Productive dev workflows</li>
          </ul>
        </section>
      </main>

      <footer className="bottom-bar">
        <section className="panel bottom-item" id="add-item-panel">
          <h2>Add new thing</h2>
          <button type="button" className="action-btn">+ New item</button>
        </section>

        <section className="panel bottom-item" id="chat-panel">
          <h2>Ask your Brain</h2>
          <div className="chat-row">
            <input type="text" placeholder="Explain my today priorities..." />
            <button type="button" className="action-btn">Chat</button>
          </div>
        </section>
      </footer>
    </div>
  )
}

export default App
