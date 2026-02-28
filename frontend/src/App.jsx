import React, { useState, useEffect } from 'react'
import './App.css'

// Import components
import Header from './components/Header'
import TodoList from './components/TodoList'
import Schedule from './components/Schedule'
import Suggestions from './components/Suggestions'
import Footer from './components/Footer'
import MoodDock from './components/MoodDock'
import StatsModal from './components/StatsModal'
import ChatInterface from './components/ChatInterface'
import AddItem from './components/AddItem'

function App() {
  const [tasks, setTasks] = useState([
    { id: 1, text: '📖 Read 20 pages of Clean Code', completed: false },
    { id: 2, text: '🚿 Take a shower', completed: false },
    { id: 3, text: '💻 3 commits to an open source project', completed: false },
    { id: 4, text: '🏋️ Exercise', completed: false },
    { id: 5, text: '👵 Call grandma', completed: false }
  ])

  const [selectedMood, setSelectedMood] = useState(null)
  const [moodFeedback, setMoodFeedback] = useState(null)
  const [isStatsOpen, setIsStatsOpen] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(false)

  const weeklyData = [
    { day: 'Mon', completion: 65 },
    { day: 'Tue', completion: 40 },
    { day: 'Wed', completion: 85 },
    { day: 'Thu', completion: 50 },
    { day: 'Fri', completion: 95 },
    { day: 'Sat', completion: 70 },
    { day: 'Sun', completion: 30 }
  ]

  const [schedule, setSchedule] = useState([
    { id: 1, title: 'Deep Work Session', start: '09:00', end: '11:00', icon: '💻', type: 'work' },
    { id: 2, title: 'Team Sync', start: '11:30', end: '12:30', icon: '🤝', type: 'meeting' },
    { id: 3, title: 'Gym & Core', start: '14:00', end: '15:30', icon: '🏋️', type: 'health' },
    { id: 4, title: 'Client Presentation', start: '16:00', end: '17:30', icon: '📈', type: 'work' }
  ])

  const [accessToken, setAccessToken] = useState(null);
  const [tokenClient, setTokenClient] = useState(null);

  // IMPORTANT: Replace with your actual Google OAuth Client ID
  const CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';
  const SCOPES = 'https://www.googleapis.com/auth/calendar.readonly';

  useEffect(() => {
    // Load Google Identity Services script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      const client = window.google.accounts.oauth2.initTokenClient({
        client_id: CLIENT_ID,
        scope: SCOPES,
        callback: (response) => {
          if (response.error !== undefined) {
            throw (response);
          }
          setAccessToken(response.access_token);
          fetchEvents(response.access_token);
        },
      });
      setTokenClient(client);
    };
    document.body.appendChild(script);
  }, []);

  const handleAuthClick = () => {
    if (tokenClient) {
      tokenClient.requestAccessToken({ prompt: 'consent' });
    }
  };

  const fetchEvents = async (token) => {
    const now = new Date();
    const timeMin = new Date(now.setHours(0, 0, 0, 0)).toISOString();
    const timeMax = new Date(now.setHours(23, 59, 59, 999)).toISOString();

    try {
      const response = await fetch(
        `https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${timeMin}&timeMax=${timeMax}&singleEvents=true&orderBy=startTime`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();

      if (data.items && data.items.length > 0) {
        const mappedEvents = data.items.map((event, index) => ({
          id: event.id || index,
          title: event.summary || 'Untitled Event',
          start: new Date(event.start.dateTime || event.start.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          end: new Date(event.end.dateTime || event.end.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          icon: event.summary?.toLowerCase().includes('work') ? '💻' :
            event.summary?.toLowerCase().includes('gym') ? '🏋️' :
              event.summary?.toLowerCase().includes('sync') ? '🤝' : '📅',
          type: event.summary?.toLowerCase().includes('gym') ? 'health' :
            event.summary?.toLowerCase().includes('sync') ? 'meeting' : 'work'
        }));
        setSchedule(mappedEvents);
      }
    } catch (error) {
      console.error('Error fetching calendar events:', error);
    }
  };

  const upNext = schedule[0];

  const moods = [
    { label: 'Happy', emoji: '😄', value: 'happy' },
    { label: 'Tired', emoji: '🫩', value: 'tired' },
    { label: 'Sad', emoji: '😔', value: 'sad' }
  ]

  const moodPhrases = {
    happy: "Happiness is contagious! Keep that energy and tackle your most creative tasks today. 🌟",
    tired: "You're not alone. Take a break and recharge. 😴",
    sad: "It's okay to feel down. Be kind to yourself. Focus on small wins today. 🫂"
  }

  const handleMoodSubmit = async (moodValue) => {
    setSelectedMood(moodValue);
    setMoodFeedback(moodPhrases[moodValue]);
    if (moodValue === 'happy') triggerDopamine();

    // Persist sentiment to backend
    try {
      await fetch('http://localhost:8000/api/v1/sentiments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sentiment: moodValue }),
      });
    } catch (error) {
      console.error('Error recording sentiment:', error);
    }

    // Auto-hide feedback after 5 seconds
    setTimeout(() => {
      setMoodFeedback(null);
      setSelectedMood(null);
    }, 5000);
  };

  const suggestions = [
    {
      id: 1,
      type: 'Video',
      title: 'Clean Code - Uncle Bob',
      icon: '🎥',
      url: 'https://www.youtube.com/watch?v=7EmboKQH8lM',
      youtube_url: 'https://www.youtube.com/watch?v=7EmboKQH8lM',
      summary: 'A deep dive into the principles of writing clean, maintainable code by Robert C. Martin. Essential for professional developers.'
    },
    {
      id: 2,
      type: 'Article',
      title: 'The MIT License',
      icon: '📝',
      url: 'https://opensource.org/license/mit',
      summary: 'A short and simple permissive software license with very few restrictions. Perfect for open source projects.'
    },
    {
      id: 3,
      type: 'Video',
      title: 'Never Gonna Give You Up',
      icon: '🎥',
      url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      youtube_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      summary: 'A legendary masterpiece of digital culture. An essential piece of internet history that everyone should experience.'
    }
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
      <Header />

      <main className="main-area">
        <section className="left-column">
          <TodoList
            tasks={tasks}
            completedCount={completedCount}
            progress={progress}
            toggleTask={toggleTask}
          />

          <Schedule
            accessToken={accessToken}
            handleAuthClick={handleAuthClick}
            schedule={schedule}
            upNext={upNext}
          />

          <AddItem />
        </section>

        <div className="right-column">
          <Suggestions
            suggestions={suggestions}
            currentSuggestion={currentSuggestion}
            prevSuggestion={prevSuggestion}
            nextSuggestion={nextSuggestion}
            setCurrentSuggestion={setCurrentSuggestion}
          />
        </div>
      </main>

      <Footer onChatClick={() => setIsChatOpen(true)} />

      <ChatInterface
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />

      <MoodDock
        moodFeedback={moodFeedback}
        moods={moods}
        handleMoodSubmit={handleMoodSubmit}
        setIsStatsOpen={setIsStatsOpen}
        setMoodFeedback={setMoodFeedback}
        setSelectedMood={setSelectedMood}
      />

      <StatsModal
        isStatsOpen={isStatsOpen}
        setIsStatsOpen={setIsStatsOpen}
        weeklyData={weeklyData}
      />
    </div>
  )
}

export default App
