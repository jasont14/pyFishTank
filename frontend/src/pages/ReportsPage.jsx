import { useState, useEffect } from 'react'
import { reportsApi, tankApi } from '../api'

function ReportsPage() {
  const [summary, setSummary] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadData = async () => {
    try {
      setLoading(true)
      const data = await reportsApi.getSummary()
      setSummary(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Never'
    const date = new Date(dateStr)
    return date.toLocaleDateString()
  }

  const getTankTypeLabel = (type) => {
    return type.charAt(0).toUpperCase() + type.slice(1)
  }

  if (loading) {
    return <div className="loading">Loading reports...</div>
  }

  const totalFish = summary.reduce((acc, s) => acc + s.fish_count, 0)
  const totalHealthy = summary.reduce((acc, s) => acc + s.health_counts.healthy, 0)
  const totalSick = summary.reduce((acc, s) => acc + s.health_counts.sick, 0)
  const totalRecovering = summary.reduce((acc, s) => acc + s.health_counts.recovering, 0)
  const totalDeceased = summary.reduce((acc, s) => acc + s.health_counts.deceased, 0)

  return (
    <div>
      <div className="page-header">
        <h2>Reports</h2>
        <button className="secondary" onClick={loadData}>
          Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {summary.length === 0 ? (
        <div className="empty-state">
          <div className="icon">📊</div>
          <p>No data to report yet. Add some tanks and fish first!</p>
        </div>
      ) : (
        <>
          <div className="card">
            <h3 style={{ marginBottom: '1rem', color: '#1e3a5f' }}>Overview</h3>
            <div className="summary-grid">
              <div className="summary-card">
                <h4>Total Tanks</h4>
                <div style={{ fontSize: '2rem', fontWeight: '600', color: '#3b82f6' }}>
                  {summary.length}
                </div>
              </div>
              <div className="summary-card">
                <h4>Total Fish</h4>
                <div style={{ fontSize: '2rem', fontWeight: '600', color: '#3b82f6' }}>
                  {totalFish}
                </div>
              </div>
              <div className="summary-card">
                <h4>Fish Health</h4>
                <div className="summary-stat">
                  <span>Healthy</span>
                  <span className="health-badge healthy">{totalHealthy}</span>
                </div>
                <div className="summary-stat">
                  <span>Sick</span>
                  <span className="health-badge sick">{totalSick}</span>
                </div>
                <div className="summary-stat">
                  <span>Recovering</span>
                  <span className="health-badge recovering">{totalRecovering}</span>
                </div>
                <div className="summary-stat">
                  <span>Deceased</span>
                  <span className="health-badge deceased">{totalDeceased}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '1rem', color: '#1e3a5f' }}>Tank Details</h3>
            <div className="summary-grid">
              {summary.map(s => (
                <div key={s.tank.id} className="summary-card">
                  <h4>{s.tank.name}</h4>
                  <div className="summary-stat">
                    <span>Type</span>
                    <span>{getTankTypeLabel(s.tank.tank_type)}</span>
                  </div>
                  <div className="summary-stat">
                    <span>Size</span>
                    <span>{s.tank.size_gallons} gal</span>
                  </div>
                  <div className="summary-stat">
                    <span>Fish</span>
                    <span>{s.fish_count}</span>
                  </div>
                  <div className="summary-stat">
                    <span>Healthy</span>
                    <span className="health-badge healthy">{s.health_counts.healthy}</span>
                  </div>
                  <div className="summary-stat">
                    <span>Need Care</span>
                    <span className="health-badge sick">
                      {s.health_counts.sick + s.health_counts.recovering}
                    </span>
                  </div>
                  <div className="summary-stat">
                    <span>Maintenance Logs</span>
                    <span>{s.maintenance_count}</span>
                  </div>
                  <div className="summary-stat">
                    <span>Last Maintenance</span>
                    <span>{formatDate(s.last_maintenance)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ReportsPage
