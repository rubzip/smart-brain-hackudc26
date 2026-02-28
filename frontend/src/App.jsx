import './App.css'

function App() {
  return (
    <div className="app-shell">
      <main className="main-area">
        <section className="left-column">
          <article className="panel">
            <h2>To do list</h2>
            <ul>
              <li>Review project brief</li>
              <li>Organize daily priorities</li>
              <li>Prepare status update</li>
            </ul>
          </article>

          <article className="panel">
            <h2>Pending calendar events</h2>
            <ul>
              <li>Mon · Team sync · 10:00</li>
              <li>Tue · Design review · 12:30</li>
              <li>Thu · Demo prep · 16:00</li>
            </ul>
          </article>
        </section>

        <section className="panel right-column">
          <h2>Suggestions (stored things to read/watch)</h2>
          <ul>
            <li>Article: Building better prompts</li>
            <li>Video: React state patterns</li>
            <li>Paper: Retrieval-augmented systems</li>
            <li>Talk: Productive dev workflows</li>
          </ul>
        </section>
      </main>

      <footer className="bottom-bar">
        <section className="panel bottom-item">
          <h2>Add new thing</h2>
          <button type="button">+ New item</button>
        </section>

        <section className="panel bottom-item">
          <h2>Start chat</h2>
          <div className="chat-row">
            <input type="text" placeholder="Write a message..." />
            <button type="button">Chat</button>
          </div>
        </section>
      </footer>
    </div>
  )
}

export default App
