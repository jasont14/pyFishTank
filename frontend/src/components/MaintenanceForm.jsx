import { useState } from 'react'

function MaintenanceForm({ tanks, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    tank_id: tanks[0]?.id || '',
    activity_type: 'water_change',
    description: '',
    percentage: '',
    temperature: '',
    ph: '',
    ammonia: '',
    nitrite: '',
    nitrate: '',
    salinity: ''
  })
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      const data = {
        tank_id: formData.tank_id,
        activity_type: formData.activity_type,
        description: formData.description
      }

      if (formData.activity_type === 'water_change' && formData.percentage) {
        data.percentage = parseInt(formData.percentage)
      }

      if (formData.activity_type === 'water_test') {
        data.water_params = {}
        if (formData.temperature) data.water_params.temperature = parseFloat(formData.temperature)
        if (formData.ph) data.water_params.ph = parseFloat(formData.ph)
        if (formData.ammonia) data.water_params.ammonia = parseFloat(formData.ammonia)
        if (formData.nitrite) data.water_params.nitrite = parseFloat(formData.nitrite)
        if (formData.nitrate) data.water_params.nitrate = parseFloat(formData.nitrate)
        if (formData.salinity) data.water_params.salinity = parseFloat(formData.salinity)
      }

      await onSubmit(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const selectedTank = tanks.find(t => t.id === formData.tank_id)
  const isSaltwater = selectedTank?.tank_type === 'saltwater'

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label htmlFor="tank_id">Tank *</label>
        <select
          id="tank_id"
          name="tank_id"
          value={formData.tank_id}
          onChange={handleChange}
          required
        >
          {tanks.map(tank => (
            <option key={tank.id} value={tank.id}>{tank.name}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="activity_type">Activity Type *</label>
        <select
          id="activity_type"
          name="activity_type"
          value={formData.activity_type}
          onChange={handleChange}
          required
        >
          <option value="water_change">Water Change</option>
          <option value="feeding">Feeding</option>
          <option value="filter_clean">Filter Cleaning</option>
          <option value="water_test">Water Test</option>
          <option value="equipment_check">Equipment Check</option>
          <option value="medication">Medication</option>
        </select>
      </div>

      {formData.activity_type === 'water_change' && (
        <div className="form-group">
          <label htmlFor="percentage">Water Change Percentage</label>
          <input
            type="number"
            id="percentage"
            name="percentage"
            value={formData.percentage}
            onChange={handleChange}
            min="1"
            max="100"
            placeholder="e.g., 25"
          />
        </div>
      )}

      {formData.activity_type === 'water_test' && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label htmlFor="temperature">Temperature (°F)</label>
              <input
                type="number"
                id="temperature"
                name="temperature"
                value={formData.temperature}
                onChange={handleChange}
                step="0.1"
                placeholder="e.g., 78"
              />
            </div>
            <div className="form-group">
              <label htmlFor="ph">pH</label>
              <input
                type="number"
                id="ph"
                name="ph"
                value={formData.ph}
                onChange={handleChange}
                step="0.1"
                placeholder="e.g., 7.2"
              />
            </div>
            <div className="form-group">
              <label htmlFor="ammonia">Ammonia (ppm)</label>
              <input
                type="number"
                id="ammonia"
                name="ammonia"
                value={formData.ammonia}
                onChange={handleChange}
                step="0.01"
                placeholder="e.g., 0"
              />
            </div>
            <div className="form-group">
              <label htmlFor="nitrite">Nitrite (ppm)</label>
              <input
                type="number"
                id="nitrite"
                name="nitrite"
                value={formData.nitrite}
                onChange={handleChange}
                step="0.01"
                placeholder="e.g., 0"
              />
            </div>
            <div className="form-group">
              <label htmlFor="nitrate">Nitrate (ppm)</label>
              <input
                type="number"
                id="nitrate"
                name="nitrate"
                value={formData.nitrate}
                onChange={handleChange}
                step="0.1"
                placeholder="e.g., 10"
              />
            </div>
            {isSaltwater && (
              <div className="form-group">
                <label htmlFor="salinity">Salinity (ppt)</label>
                <input
                  type="number"
                  id="salinity"
                  name="salinity"
                  value={formData.salinity}
                  onChange={handleChange}
                  step="0.1"
                  placeholder="e.g., 35"
                />
              </div>
            )}
          </div>
        </>
      )}

      <div className="form-group">
        <label htmlFor="description">Notes</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          placeholder="Additional details..."
        />
      </div>

      <div className="modal-actions">
        <button type="button" className="secondary" onClick={onCancel} disabled={submitting}>
          Cancel
        </button>
        <button type="submit" className="primary" disabled={submitting}>
          {submitting ? 'Saving...' : 'Log Activity'}
        </button>
      </div>
    </form>
  )
}

export default MaintenanceForm
