import { useState } from 'react'

function TankForm({ initialData, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: initialData?.name || '',
    size_gallons: initialData?.size_gallons || '',
    tank_type: initialData?.tank_type || 'freshwater',
    location: initialData?.location || '',
    equipment: initialData?.equipment?.join(', ') || ''
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
        size_gallons: parseFloat(formData.size_gallons),
        tank_type: formData.tank_type,
        location: formData.location,
        equipment: formData.equipment
          ? formData.equipment.split(',').map(e => e.trim()).filter(e => e)
          : []
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
        <label htmlFor="name">Tank Name *</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          placeholder="e.g., Living Room Tank"
        />
      </div>

      <div className="form-group">
        <label htmlFor="size_gallons">Size (gallons) *</label>
        <input
          type="number"
          id="size_gallons"
          name="size_gallons"
          value={formData.size_gallons}
          onChange={handleChange}
          required
          min="0.1"
          step="0.1"
          placeholder="e.g., 40"
        />
      </div>

      <div className="form-group">
        <label htmlFor="tank_type">Tank Type *</label>
        <select
          id="tank_type"
          name="tank_type"
          value={formData.tank_type}
          onChange={handleChange}
          required
        >
          <option value="freshwater">Freshwater</option>
          <option value="saltwater">Saltwater</option>
          <option value="brackish">Brackish</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="location">Location</label>
        <input
          type="text"
          id="location"
          name="location"
          value={formData.location}
          onChange={handleChange}
          placeholder="e.g., Living Room"
        />
      </div>

      <div className="form-group">
        <label htmlFor="equipment">Equipment (comma-separated)</label>
        <input
          type="text"
          id="equipment"
          name="equipment"
          value={formData.equipment}
          onChange={handleChange}
          placeholder="e.g., Fluval 312, Heater, LED Light"
        />
      </div>

      <div className="modal-actions">
        <button type="button" className="secondary" onClick={onCancel} disabled={submitting}>
          Cancel
        </button>
        <button type="submit" className="primary" disabled={submitting}>
          {submitting ? 'Saving...' : (initialData ? 'Update' : 'Add Tank')}
        </button>
      </div>
    </form>
  )
}

export default TankForm
