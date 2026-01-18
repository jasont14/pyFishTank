import { useState, useEffect } from 'react'
import { fishApi, tankApi } from '../api'
import Modal from '../components/Modal'
import FishForm from '../components/FishForm'

function FishPage() {
  const [fish, setFish] = useState([])
  const [tanks, setTanks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingFish, setEditingFish] = useState(null)
  const [filterTankId, setFilterTankId] = useState('')

  const loadData = async () => {
    try {
      setLoading(true)
      const [fishData, tanksData] = await Promise.all([
        fishApi.getAll(),
        tankApi.getAll()
      ])
      setFish(fishData)
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

  const handleAddFish = async (data) => {
    try {
      await fishApi.create(data)
      setShowAddModal(false)
      loadData()
    } catch (err) {
      throw err
    }
  }

  const handleEditFish = async (data) => {
    try {
      await fishApi.update(editingFish.id, data)
      setEditingFish(null)
      loadData()
    } catch (err) {
      throw err
    }
  }

  const handleDeleteFish = async (f) => {
    if (!confirm(`Remove "${f.name}" from the tank?`)) {
      return
    }
    try {
      await fishApi.delete(f.id)
      loadData()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleUpdateHealth = async (f, status) => {
    try {
      await fishApi.updateHealth(f.id, status)
      loadData()
    } catch (err) {
      setError(err.message)
    }
  }

  const getTankName = (tankId) => {
    const tank = tanks.find(t => t.id === tankId)
    return tank ? tank.name : 'Unknown Tank'
  }

  const getHealthIcon = (status) => {
    switch (status) {
      case 'healthy': return '✓'
      case 'sick': return '✗'
      case 'recovering': return '↻'
      case 'deceased': return '†'
      default: return '?'
    }
  }

  const filteredFish = filterTankId
    ? fish.filter(f => f.tank_id === filterTankId)
    : fish

  if (loading) {
    return <div className="loading">Loading fish...</div>
  }

  return (
    <div>
      <div className="page-header">
        <h2>Fish</h2>
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
          <button className="primary" onClick={() => setShowAddModal(true)} disabled={tanks.length === 0}>
            Add Fish
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {tanks.length === 0 ? (
        <div className="empty-state">
          <div className="icon">🐟</div>
          <p>Create a tank first before adding fish.</p>
        </div>
      ) : filteredFish.length === 0 ? (
        <div className="empty-state">
          <div className="icon">🐟</div>
          <p>No fish yet. Add your first fish!</p>
        </div>
      ) : (
        <div className="card">
          <div className="card-grid">
            {filteredFish.map(f => (
              <div key={f.id} className="fish-card">
                <div className="fish-icon">🐠</div>
                <div className="fish-info">
                  <div className="fish-name">{f.name}</div>
                  <div className="fish-species">{f.species}</div>
                  <div className="fish-tank">{getTankName(f.tank_id)}</div>
                  {f.color && <div className="fish-tank">Color: {f.color}</div>}
                  {f.size && <div className="fish-tank">Size: {f.size}</div>}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                  <span className={`health-badge ${f.health_status}`}>
                    {getHealthIcon(f.health_status)} {f.health_status}
                  </span>
                  <div style={{ display: 'flex', gap: '0.25rem' }}>
                    <select
                      value={f.health_status}
                      onChange={(e) => handleUpdateHealth(f, e.target.value)}
                      style={{ width: 'auto', padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                    >
                      <option value="healthy">Healthy</option>
                      <option value="sick">Sick</option>
                      <option value="recovering">Recovering</option>
                      <option value="deceased">Deceased</option>
                    </select>
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <button className="secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => setEditingFish(f)}>
                    Edit
                  </button>
                  <button className="danger" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleDeleteFish(f)}>
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showAddModal && (
        <Modal title="Add Fish" onClose={() => setShowAddModal(false)}>
          <FishForm tanks={tanks} onSubmit={handleAddFish} onCancel={() => setShowAddModal(false)} />
        </Modal>
      )}

      {editingFish && (
        <Modal title="Edit Fish" onClose={() => setEditingFish(null)}>
          <FishForm
            tanks={tanks}
            initialData={editingFish}
            onSubmit={handleEditFish}
            onCancel={() => setEditingFish(null)}
          />
        </Modal>
      )}
    </div>
  )
}

export default FishPage
