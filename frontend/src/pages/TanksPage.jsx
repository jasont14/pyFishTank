import { useState, useEffect } from 'react'
import { tankApi, fishApi } from '../api'
import Modal from '../components/Modal'
import TankForm from '../components/TankForm'

function TanksPage() {
  const [tanks, setTanks] = useState([])
  const [fishByTank, setFishByTank] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingTank, setEditingTank] = useState(null)

  const loadData = async () => {
    try {
      setLoading(true)
      const [tanksData, fishData] = await Promise.all([
        tankApi.getAll(),
        fishApi.getAll()
      ])
      setTanks(tanksData)

      const grouped = {}
      fishData.forEach(fish => {
        if (!grouped[fish.tank_id]) grouped[fish.tank_id] = []
        grouped[fish.tank_id].push(fish)
      })
      setFishByTank(grouped)
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

  const handleAddTank = async (data) => {
    try {
      await tankApi.create(data)
      setShowAddModal(false)
      loadData()
    } catch (err) {
      throw err
    }
  }

  const handleEditTank = async (data) => {
    try {
      await tankApi.update(editingTank.id, data)
      setEditingTank(null)
      loadData()
    } catch (err) {
      throw err
    }
  }

  const handleDeleteTank = async (tank) => {
    if (!confirm(`Delete "${tank.name}"? This will also delete all fish and maintenance logs for this tank.`)) {
      return
    }
    try {
      await tankApi.delete(tank.id)
      loadData()
    } catch (err) {
      setError(err.message)
    }
  }

  const getTankTypeLabel = (type) => {
    return type.charAt(0).toUpperCase() + type.slice(1)
  }

  if (loading) {
    return <div className="loading">Loading tanks...</div>
  }

  return (
    <div>
      <div className="page-header">
        <h2>Tanks</h2>
        <button className="primary" onClick={() => setShowAddModal(true)}>
          Add Tank
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {tanks.length === 0 ? (
        <div className="empty-state">
          <div className="icon">🐠</div>
          <p>No tanks yet. Add your first tank to get started!</p>
        </div>
      ) : (
        <div className="card-grid">
          {tanks.map(tank => {
            const fish = fishByTank[tank.id] || []
            const healthyCounts = fish.reduce((acc, f) => {
              acc[f.health_status] = (acc[f.health_status] || 0) + 1
              return acc
            }, {})

            return (
              <div key={tank.id} className="tank-card">
                <h3>{tank.name}</h3>
                <div className="meta">
                  {tank.size_gallons} gal &bull; {getTankTypeLabel(tank.tank_type)}
                  {tank.location && ` &bull; ${tank.location}`}
                </div>
                <div className="stats">
                  <div className="stat">
                    <div className="stat-value">{fish.length}</div>
                    <div className="stat-label">Fish</div>
                  </div>
                  <div className="stat">
                    <div className="stat-value">{healthyCounts.healthy || 0}</div>
                    <div className="stat-label">Healthy</div>
                  </div>
                  <div className="stat">
                    <div className="stat-value">{(healthyCounts.sick || 0) + (healthyCounts.recovering || 0)}</div>
                    <div className="stat-label">Need Care</div>
                  </div>
                </div>
                {tank.equipment && tank.equipment.length > 0 && (
                  <div className="meta" style={{ marginBottom: '0.75rem' }}>
                    Equipment: {tank.equipment.join(', ')}
                  </div>
                )}
                <div className="actions">
                  <button className="secondary" onClick={() => setEditingTank(tank)}>
                    Edit
                  </button>
                  <button className="danger" onClick={() => handleDeleteTank(tank)}>
                    Delete
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {showAddModal && (
        <Modal title="Add Tank" onClose={() => setShowAddModal(false)}>
          <TankForm onSubmit={handleAddTank} onCancel={() => setShowAddModal(false)} />
        </Modal>
      )}

      {editingTank && (
        <Modal title="Edit Tank" onClose={() => setEditingTank(null)}>
          <TankForm
            initialData={editingTank}
            onSubmit={handleEditTank}
            onCancel={() => setEditingTank(null)}
          />
        </Modal>
      )}
    </div>
  )
}

export default TanksPage
