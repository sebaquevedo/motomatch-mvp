import { useNavigate } from 'react-router-dom'
import QuerySearch from '../components/QuerySearch'
import ResultsDisplay from '../components/ResultsDisplay'
import { useAuth } from '../hooks/useAuth'
import { useRagQuery } from '../hooks/useRagQuery'
import '../styles/dashboard.css'

export default function DashboardPage() {
  const { logout } = useAuth()
  const { query, loading, result, error } = useRagQuery()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>MotoMatch</h1>
        <button onClick={handleLogout} className="btn-logout">
          Logout
        </button>
      </header>

      <main className="dashboard-content">
        <QuerySearch onQuery={query} loading={loading} />
        {error && <div className="query-error">{error}</div>}
        {result && <ResultsDisplay result={result} />}
      </main>
    </div>
  )
}
