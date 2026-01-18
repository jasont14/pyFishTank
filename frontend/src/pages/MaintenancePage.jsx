import { useState, useEffect } from 'react'
import { maintenanceApi, tankApi } from '../api'
import Modal from '../components/Modal'
import MaintenanceForm from '../components/MaintenanceForm'

function MaintenancePage() {
  const [logs, setLogs] = useState([])
  const [tanks, setTanks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [filterTankId, setFilterTankId] = useState('')
  const [filterType, setFilterType] = useState('')

  const loadData = async () => {
    try {
      setLoading(true)
      const [logsData, tanksData] = await Promise.all([
        maintenanceApi.getAll({ limit: 50 }),
        tankApi.getAll()
      ])
      setLogs(logsData)
      setTanks(tanksData)
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

  const handleAddLog = async (data) => {
    try {
      await maintenanceApi.create(data)
      setShowAddModal(false)
      loadData()
    } catch (err) {
      throw err
    }
  }

  const getTankName = (tankId) => {
    const tank = tanks.find(t => t.id === tankId)
    return tank ? tank.name : 'Unknown Tank'
  }

  const getActivityIcon = (type) => {
    switch (type) {
      case 'water_change': return '💧'
      case 'feeding': return '🍽️'
      case 'filter_clean': return '🧹'
      case 'water_test': return '🧪'
      case 'equipment_check': return '🔧'
      case 'medication': return '💊'
      default: return '📝'
    }
  }

  const getActivityLabel = (type) => {
    switch (type) {
      case 'water_change': return 'Water Change'
      case 'feeding': return 'Feeding'
      case 'filter_clean': return 'Filter Cleaning'
      case 'water_test': return 'Water Test'
      case 'equipment_check': return 'Equipment Check'
      case 'medication': return 'Medication'
      default: return type
    }
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  let filteredLogs = logs
  if (filterTankId) {
    filteredLogs = filteredLogs.filter(log => log.tank_id === filterTankId)
  }
  if (filterType) {
    filteredLogs = filteredLogs.filter(log => log.activity_type === filterType)
  }

  if (loading) {
    return <div className="loading">Loading maintenance logs...</div>
  }

  return (
    <div>
      <div className="page-header">
        <h2>Maintenance Logs</h2>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <select
            value={filterTankId}
            onChange={(e) => setFilterTankId(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="">All Tanks</option>
            {tanks.map(tank => (
              <option key={tank.id} value={tank.id}>{tank.name}</option>
            ))}
          </select>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="">All Types</option>
            <option value="water_change">Water Change</option>
            <option value="feeding">Feeding</option>
            <option value="filter_clean">Filter Cleaning</option>
            <option value="water_test">Water Test</option>
            <option value="equipment_check">Equipment Check</option>
            <option value="medication">Medication</option>
          </select>
          <button className="primary" onClick={() => setShowAddModal(true)} disabled={tanks.length === 0}>
            Log Activity
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {tanks.length === 0 ? (
        <div className="empty-state">
          <div className="icon">📋</div>
          <p>Create a tank first before logging maintenance.</p>
        </div>
      ) : filteredLogs.length === 0 ? (
        <div className="empty-state">
          <div className="icon">📋</div>
          <p>No maintenance logs yet.</p>
        </div>
      ) : (
        <div className="card">
          {filteredLogs.map(log => (
            <div key={log.id} className="log-item">
              <div className={`log-icon ${log.activity_type}`}>
                {getActivityIcon(log.activity_type)}
              </div>
              <div className="log-content">
                <div className="log-title">{getActivityLabel(log.activity_type)}</div>
                <div className="log-description">{log.description}</div>
                <div className="log-meta">
                  {getTankName(log.tank_id)} &bull; {formatDate(log.date)}
                </div>
                {log.water_params && (
                  <div className="log-meta" style={{ marginTop: '0.5rem', background: '#f3f4f6', padding: '0.5rem', borderRadius: '4px' }}>
                    {log.water_params.temperature && `Temp: ${log.water_params.temperature}°F `}
                    {log.water_params.ph && `pH: ${log.water_params.ph} `}
                    {log.water_params.ammonia !== null && `Ammonia: ${log.water_params.ammonia}ppm `}
                    {log.water_params.nitrite !== null && `Nitrite: ${log.water_params.nitrite}ppm `}
                    {log.water_params.nitrate !== null && `Nitrate: ${log.water_params.nitrate}ppm `}
                    {log.water_params.salinity && `Salinity: ${log.water_params.salinity}ppt`}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showAddModal && (
        <Modal title="Log Maintenance Activity" onClose={() => setShowAddModal(false)}>
          <MaintenanceForm tanks={tanks} onSubmit={handleAddLog} onCancel={() => setShowAddModal(false)} />
        </Modal>
      )}
    </div>
  )
}

export default MaintenancePage
