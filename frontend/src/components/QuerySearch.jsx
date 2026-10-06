import { useState } from 'react'

export default function QuerySearch({ onQuery, loading }) {
  const [question, setQuestion] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (question.trim()) {
      onQuery(question)
    }
  }

  return (
    <div className="query-section">
      <h2>Ask about motorcycle parts compatibility</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Is the CB650F 2018 alternator compatible with the 2020?"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
    </div>
  )
}
