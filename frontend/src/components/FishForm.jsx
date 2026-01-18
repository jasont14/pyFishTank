import { useState } from 'react'

function FishForm({ tanks, initialData, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: initialData?.name || '',
    species: initialData?.species || '',
    tank_id: initialData?.tank_id || (tanks[0]?.id || ''),
    health_status: initialData?.health_status || 'healthy',
    size: initialData?.size || '',
    color: initialData?.color || '',
    feeding_preferences: initialData?.feeding_preferences || '',
    notes: initialData?.notes || '',
    birth_date: initialData?.birth_date || ''
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
        name: formData.name,
        species: formData.species,
        tank_id: formData.tank_id,
        health_status: formData.health_status,
        size: formData.size || null,
        color: formData.color || null,
        feeding_preferences: formData.feeding_preferences || null,
        notes: formData.notes || null,
        birth_date: formData.birth_date || null
      }
      await onSubmit(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label htmlFor="name">Name *</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          placeholder="e.g., Nemo"
        />
      </div>

      <div className="form-group">
        <label htmlFor="species">Species *</label>
        <input
          type="text"
          id="species"
          name="species"
          value={formData.species}
          onChange={handleChange}
          required
          placeholder="e.g., Clownfish"
        />
      </div>

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
        <label htmlFor="health_status">Health Status</label>
        <select
          id="health_status"
          name="health_status"
          value={formData.health_status}
          onChange={handleChange}
        >
          <option value="healthy">Healthy</option>
          <option value="sick">Sick</option>
          <option value="recovering">Recovering</option>
          <option value="deceased">Deceased</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="color">Color</label>
        <input
          type="text"
          id="color"
          name="color"
          value={formData.color}
          onChange={handleChange}
          placeholder="e.g., Orange and white"
        />
      </div>

      <div className="form-group">
        <label htmlFor="size">Size</label>
        <input
          type="text"
          id="size"
          name="size"
          value={formData.size}
          onChange={handleChange}
          placeholder="e.g., 2 inches"
        />
      </div>

      <div className="form-group">
        <label htmlFor="birth_date">Birth Date</label>
        <input
          type="date"
          id="birth_date"
          name="birth_date"
          value={formData.birth_date}
          onChange={handleChange}
        />
      </div>

      <div className="form-group">
        <label htmlFor="feeding_preferences">Feeding Preferences</label>
        <input
          type="text"
          id="feeding_preferences"
          name="feeding_preferences"
          value={formData.feeding_preferences}
          onChange={handleChange}
          placeholder="e.g., Flakes, twice daily"
        />
      </div>

      <div className="form-group">
        <label htmlFor="notes">Notes</label>
        <textarea
          id="notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          placeholder="Any additional notes..."
        />
      </div>

      <div className="modal-actions">
        <button type="button" className="secondary" onClick={onCancel} disabled={submitting}>
          Cancel
        </button>
        <button type="submit" className="primary" disabled={submitting}>
          {submitting ? 'Saving...' : (initialData ? 'Update' : 'Add Fish')}
        </button>
      </div>
    </form>
  )
}

export default FishForm
