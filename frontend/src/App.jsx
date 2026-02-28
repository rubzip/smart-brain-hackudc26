import React, { useState, useEffect } from 'react'
import confetti from 'canvas-confetti'
import './App.css'

function App() {
  const [tasks, setTasks] = useState([
    { id: 1, text: '📖 Read 20 pages of Clean Code', completed: false },
    { id: 2, text: '🚿 Take a shower', completed: false },
    { id: 3, text: '💻 3 commits to an open source project', completed: false },
    { id: 4, text: '🏋️ Exercise', completed: false },
    { id: 5, text: '👵 Call your grandma', completed: false }
  ])

  const suggestions = [
    { id: 1, type: 'Article', title: 'Building better prompts', icon: '📝' },
    { id: 2, type: 'Video', title: 'React state patterns', icon: '🎥' },
    { id: 3, type: 'Paper', title: 'Retrieval-augmented systems', icon: '📄' },
    { id: 4, type: 'Talk', title: 'Productive dev workflows', icon: '🎤' }
  ]

  const [currentSuggestion, setCurrentSuggestion] = useState(0)

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
    import('canvas-confetti').then(confetti => {
      confetti.default({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#2563eb', '#10b981', '#f59e0b', '#ec4899']
      })
    })
  }

  useEffect(() => {
    if (completedCount === tasks.length && tasks.length > 0) {
      import('canvas-confetti').then(confetti => {
        const duration = 3 * 1000
        const end = Date.now() + duration

        const frame = () => {
          confetti.default({
            particleCount: 5,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: ['#2563eb', '#10b981']
          })
          confetti.default({
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
      })
    }
  }, [completedCount, tasks.length])

  const nextSuggestion = () => {
    setCurrentSuggestion((prev) => (prev + 1) % suggestions.length)
  }

  const prevSuggestion = () => {
    setCurrentSuggestion((prev) => (prev - 1 + suggestions.length) % suggestions.length)
  }

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

        <section className="panel right-column suggestion-carousel-panel">
          <h2>Your Brain Suggestions</h2>
          <div className="carousel-container">
            <button className="carousel-btn prev" onClick={prevSuggestion}>←</button>

            <div className="carousel-track">
              {suggestions.map((item, index) => (
                <div
                  key={item.id}
                  className={`suggestion-card ${index === currentSuggestion ? 'active' : ''}`}
                  style={{ transform: `translateX(${(index - currentSuggestion) * 105}%)` }}
                >
                  <div className="card-icon">{item.icon}</div>
                  <div className="card-tag">{item.type}</div>
                  <h3 className="card-title">{item.title}</h3>
                  <button className="open-btn">View content</button>
                </div>
              ))}
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
